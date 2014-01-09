"""
Usage:
  icinga2jira.py ( -c config )

Options:
  -h --help                         Show this screen.
  -c, --config CONFIG               config file for plugin

"""
from __future__ import print_function

import os
import sys
import ConfigParser
import textwrap
from abc import ABCMeta, abstractmethod

from docopt import docopt
from jira.client import JIRA
from jira.exceptions import JIRAError
from jinja2 import Template


MANDATORY_CONFIG_ENTRIES = [
    'url', 'username', 'password', 'jira_project_key', 'jira_issue_type']


class CantCloseTicketException(Exception):
    pass


class UnknownIssueException(Exception):
    pass


class IcingaEnvironment(object):
    MAPPING = {'host_address': 'ICINGA_HOSTADDRESS',
               'host_name': 'ICINGA_HOSTNAME',
               'host_output': 'ICINGA_HOSTOUTPUT',
               'host_problem_id': 'ICINGA_HOSTPROBLEMID',
               'host_state': 'ICINGA_HOSTSTATE',
               'last_service_problem_id': 'ICINGA_LASTSERVICEPROBLEMID',
               'last_host_problem_id': 'ICINGA_LASTHOSTPROBLEMID',
               'notification_author': 'ICINGA_NOTIFICATIONAUTHOR',
               'notification_comment': 'ICINGA_NOTIFICATIONCOMMENT',
               'notification_type': 'ICINGA_NOTIFICATIONTYPE',
               'service_description': 'ICINGA_SERVICEDESC',
               'service_output': 'ICINGA_SERVICEOUTPUT',
               'service_priority_id': 'ICINGA_SERVICEJIRA_PRIORITY_ID',
               'service_problem_id': 'ICINGA_SERVICEPROBLEMID',
               'service_state': 'ICINGA_SERVICESTATE',
               'short_date_time': 'ICINGA_SHORTDATETIME',
               }

    ICINGA_PREFIX = "ICI"

    def __init__(self, environment):
        for attribute_name, argument_name in self.MAPPING.iteritems():
            if argument_name in environment and environment[argument_name] not in [None, '']:
                setattr(self, attribute_name, environment[argument_name])
            else:
                setattr(self, attribute_name, None)

        self._validate()

    def _extract_missing_values(self, keys):
        missing = []
        for env_key in keys:
            if getattr(self, env_key) in [None, '']:
                missing.append(self.MAPPING[env_key])
        return missing

    def _validate_recovery_data(self):
        missing_service_recovery_data = self._extract_missing_values(
            ['last_service_problem_id'])
        missing_host_recovery_data = self._extract_missing_values(
            ['last_host_problem_id'])

        if self.is_service_issue():
            if len(missing_service_recovery_data) != 0:
                raise ValueError('Environment is missing values: %s' %
                                 ', '.join(set(missing_service_recovery_data)))
        elif self.is_host_issue():
            if len(missing_host_recovery_data) != 0:
                raise ValueError('Environment is missing values: %s' %
                                 ', '.join(set(missing_host_recovery_data)))

    def _validate_problem_data(self):
        missing_service_data = self._extract_missing_values(
            ['host_name', 'service_state', 'service_problem_id'])
        missing_host_data = self._extract_missing_values(
            ['host_name', 'host_state', 'host_problem_id'])
        if len(missing_service_data) != 0 and len(missing_host_data) != 0:
            raise ValueError('Environment is missing values: %s' %
                             ', '.join(set(missing_service_data + missing_host_data)))

    def _validate(self):
        if not self.notification_type:
            raise ValueError('Environment is missing %s' %
                             self.MAPPING['notification_type'])

        if (self.has_new_problem()):
            self._validate_problem_data()
        elif self.is_recovered():
            self._validate_recovery_data()
        else:
            pass

    def has_new_problem(self):
        return self.notification_type == 'PROBLEM'

    def is_recovered(self):
        return self.notification_type == 'RECOVERY'

    def is_service_issue(self):
        return self.service_problem_id or self.last_service_problem_id

    def is_host_issue(self):
        return not self.is_service_issue()

    def get_recovery_last_problem_id(self):
        if not self.is_recovered():
            raise TypeError(
                "Ticket does not act in recovery mode, but %s" % self.notification_type)
        if self.is_service_issue():
            return self.last_service_problem_id
        return self.last_host_problem_id

    def _create_icinga_label(self, icinga_id):
        return "%s#%s#%s" % (self.ICINGA_PREFIX, icinga_id, self.host_name)

    def get_jira_recovery_label(self):
        return self._create_icinga_label(self.get_recovery_last_problem_id())

    def create_labels_list(self):
        labels = []
        if self.is_service_issue():
            labels.append(self._create_icinga_label(self.service_problem_id))
        else:
            labels.append(self._create_icinga_label(self.host_problem_id))
        return labels


def issue_factory(jira, icinga_environment, config):
    if icinga_environment.has_new_problem():
        return OpenIssue(jira, config, icinga_environment)

    elif icinga_environment.is_recovered():
        return CloseIssue(jira, icinga_environment)

    else:
        raise UnknownIssueException("Unknown icinga alert")


class Issue(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self):
        pass

    def create_description(self):
        DESCRIPTION_TEMPLATE = textwrap.dedent("""
            {% if notification_type == "PROBLEM" %}
            {color:#3b0b0b}*Icinga Problem Alert*{color}
            {% elif notification_type == "RECOVERY" %}
            {color:#0b3b0b}*Icinga Recovery Alert*{color}
            {% elif notification_type == "ACKNOWLEDGEMENT" %}
            {color:#0f5d94}*Icinga Acknowledgement*{color}
            {% else %}
            {color:#585858}*Unknown Alert*{color}
            {% endif %}

            The following information was provided by Icinga:
            * Date & Time: {{short_date_time}}
            * Host Address: {{host_address}}
            {% if service_description %}
            * Status Information: {{service_output}}
            * Current Host State: {{host_state}}
            * Current Service State: {{service_state}}
            {% else %}
            * Status Information: {{host_output}}
            * Current Host State: {{host_state}}
            {% endif %}
            {% if notification_type == "ACKNOWLEDGEMENT" %}
            * Notification Author: {{ notification_author }}
            * Notification Comment: {{ notification_comment }}
            {% endif %}

            {% if notification_type == "RECOVERY" %}
            This ticket was closed automatically.
            {% endif %}
        """)
        template = Template(DESCRIPTION_TEMPLATE, trim_blocks=True)
        return str(template.render(self.icinga_environment.__dict__)).strip()


class OpenIssue(Issue):

    def __init__(self, jira, config, icinga_environment):
        self.jira = jira

        self.project_key = config['jira_project_key']
        self.issue_type = config['jira_issue_type']

        self.icinga_environment = icinga_environment

    def execute(self):
        return [self.jira.create_issue(fields=self._create_issue_dict())]

    def _create_issue_dict(self):
        return {'project': {'key': self.project_key},
                'summary': self._create_summary(),
                'description': self.create_description(),
                'issuetype': {'name': self.issue_type},
                'labels': self.icinga_environment.create_labels_list()
                }

    def _create_summary(self):
        if self.icinga_environment.is_service_issue():
            return ("ICINGA: %s on %s is %s" %
                    (self.icinga_environment.service_description,
                     self.icinga_environment.host_name,
                     self.icinga_environment.service_state))
        else:
            return "ICINGA: %s is %s" % (self.icinga_environment.host_name,
                                         self.icinga_environment.host_state)


class CloseIssue(Issue):

    def __init__(self, jira, icinga_environment):
        self.jira = jira
        self.icinga_environment = icinga_environment

    def execute(self):
        issues = self._find_jira_issues_by_label()
        handled_issues = []
        for issue in issues:
            try:
                self._close(issue)
                self._set_comment(issue)
                handled_issues.append(issue)
            except CantCloseTicketException as e:
                print("WARNING: %s could not be closed, reason: %s" %
                      (issue.key, str(e)))
        return handled_issues

    def _find_jira_issues_by_label(self):
        return self.jira.search_issues("labels='%s'" % self.icinga_environment.get_jira_recovery_label())

    def _set_comment(self, issue):
        self.jira.add_comment(issue, self.create_description())

    def _close(self, issue):
        try:
            close_transition_id = self._get_close_transition(issue)
            if close_transition_id:
                self.jira.transition_issue(issue, close_transition_id)
        except JIRAError as jira_error:
            raise CantCloseTicketException(jira_error)

    def _get_close_transition(self, issue):
        for transition in self.jira.transitions(issue):
            if transition['name'] == 'Close':
                return int(transition['id'])
        raise CantCloseTicketException(
            "Ticket does not have 'Close' transition; maybe it's already closed")


def open_jira_session(server, username, password, verify=False):
    return JIRA(options={'server': server, 'verify': verify},
                basic_auth=(username, password))


def parse_and_validate_config_file(file_pointer):
    config_parser = ConfigParser.ConfigParser()
    config_parser.readfp(file_pointer)
    config = dict(config_parser.items('settings'))
    for key in MANDATORY_CONFIG_ENTRIES:
        if key not in config:
            raise ValueError('config file is missing: %s' % key)
    return config


def print_usage_and_exit(arguments):
    print(arguments)
    sys.exit(1)


def parse_arguments(argv=None):
    arguments = docopt(__doc__, argv=argv)
    return arguments


def read_configuration_file(args):
    with open(args['--config']) as file_pointer:
        return parse_and_validate_config_file(file_pointer)


def create_ticket_list(config, issues):
    return ["%s/browse/%s" % (config['url'], issue.key) for issue in issues]

if __name__ == '__main__':
    args = parse_arguments()
    try:
        config = read_configuration_file(args)
        icinga_environment = IcingaEnvironment(os.environ)
    except IOError as e:
        print("Could not find configuration file: %s" % e)
        print_usage_and_exit(args)
    except ValueError as e:
        print(e)
        print_usage_and_exit(args)
    except ConfigParser.NoSectionError as e:
        print("Configuration file is corrupt: %s" % e)
        print_usage_and_exit(args)

    jira = open_jira_session(config['url'],
                             config['username'],
                             config['password'])

    try:
        issues = issue_factory(jira, icinga_environment, config).execute()
        issue_url_list_as_string = ",".join(create_ticket_list(config, issues))
        print("Event %s has been successfully handled: %s" %
              (icinga_environment.notification_type, issue_url_list_as_string))
    except Exception as e:
        print("An error occurred while handling event %s: %s" %
              (icinga_environment.notification_type, e))
        sys.exit(1)

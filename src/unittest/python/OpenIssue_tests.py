import unittest

from mock import Mock, patch

from icinga2jira import OpenIssue


ANY_PROJECT_KEY = 'MON'
ANY_ISSUE_TYPE = 'Technical task'
ANY_LAST_SERVICE_PROBLEM_ID = "76540"
ANY_PRIORITY_ID = "12"
ANY_HOST_PROBLEM_ID = "76543"
ANY_SERVICE_PROBLEM_ID = "12345"
ANY_SERVICE_STATE = "any servcie state"
ANY_HOSTNAME = "myserver1"
ANY_SERVICE_DESCRIPTION = "foo application services"
ANY_COMMENT = "any comment"
ANY_NOTIFICATION_AUTHOR = "any notification author"
ANY_HOST_OUTPUT = 'any host output'
ANY_HOST_STATE = 'any host state'
ANY_SERVICE_MESSAGE = "any service message"
ANY_SHORT_DATE_TIME = "11-26-2013 15:42:05"
NOTIFICATION_TYPE_PROBLEM = "PROBLEM"


class TestOpenIssue(unittest.TestCase):

    def setUp(self):
        self.jira_mock = Mock()
        self.ticket = Mock()
        self.icinga_environment = self.create_icinga_environment_mock()
        self.config = {'jira_project_key': ANY_PROJECT_KEY, 'jira_issue_type': ANY_ISSUE_TYPE}
        self.open_issue = OpenIssue(self.jira_mock, self.config, self.icinga_environment)

    def test_execute_is_called_properly_and_returns_list_of_handled_issues(self):
        self.jira_mock.create_issue.return_value = 'new issue'

        with patch.object(OpenIssue, '_create_issue_dict', return_value='issue_dict') as mock_create:
            open_issue = OpenIssue(self.jira_mock, self.config, self.icinga_environment)
            result = open_issue.execute()

            self.jira_mock.create_issue.assert_called_with(fields='issue_dict')
            mock_create.assert_called()
            self.assertEqual(['new issue'], result)

    def test_ticket_init(self):
        self.assertTrue(self.open_issue.jira)
        self.assertEqual(ANY_ISSUE_TYPE, self.open_issue.issue_type)
        self.assertEqual(ANY_PROJECT_KEY, self.open_issue.project_key)
        self.assertTrue(self.open_issue.icinga_environment)

    def test_create_issue_dict_should_return_valid_issue(self):
        self.icinga_environment.create_labels_list.return_value = \
            ['ICI#%s' % ANY_SERVICE_PROBLEM_ID]

        open_issue = OpenIssue(self.jira_mock, self.get_valid_configuration(), self.icinga_environment)
        actual_issue = open_issue._create_issue_dict()

        self.assertEqual(actual_issue['issuetype']['name'], ANY_ISSUE_TYPE)
        self.assertEqual(actual_issue['project']['key'], ANY_PROJECT_KEY)
        self.assertTrue(actual_issue['summary'])
        self.assertTrue(actual_issue['description'])
        self.assertEqual(actual_issue['labels'][0], "ICI#" + ANY_SERVICE_PROBLEM_ID)

    def test_summary_with_service_description(self):
        self.icinga_environment.is_service_issue.return_value = True

        open_issue = OpenIssue(self.jira_mock, self.get_valid_configuration(), self.icinga_environment)
        actual_summary = open_issue._create_summary()

        self.assertEquals("ICINGA: %s on %s is %s" % (ANY_SERVICE_DESCRIPTION, ANY_HOSTNAME, ANY_SERVICE_STATE),
                          actual_summary)

    def test_summary_without_service_description(self):
        self.icinga_environment.is_service_issue.return_value = False

        open_issue = OpenIssue(self.jira_mock, self.get_valid_configuration(), self.icinga_environment)
        actual_summary = open_issue._create_summary()

        self.assertEquals(actual_summary, "ICINGA: %s is %s" % (ANY_HOSTNAME, ANY_HOST_STATE))

    def get_valid_configuration(self):
        return {'jira_project_key': ANY_PROJECT_KEY, 'jira_issue_type': ANY_ISSUE_TYPE}

    def create_icinga_environment_mock(self):
        environment = Mock()
        environment.service_description = ANY_SERVICE_DESCRIPTION
        environment.service_state = ANY_SERVICE_STATE
        environment.host_name = ANY_HOSTNAME
        environment.host_state = ANY_HOST_STATE
        environment.short_date_time = ANY_SHORT_DATE_TIME
        environment.service_output = ANY_SERVICE_MESSAGE
        environment.host_output = ANY_HOST_OUTPUT
        environment.notification_type = NOTIFICATION_TYPE_PROBLEM
        environment.notification_author = ANY_NOTIFICATION_AUTHOR
        environment.notification_comment = ANY_COMMENT
        environment.service_problem_id = ANY_SERVICE_PROBLEM_ID
        return environment

import unittest
import textwrap
from mock import Mock

from icinga2jira import Issue


NOTIFICATION_TYPE_PROBLEM = "PROBLEM"


def create_icinga_environment_mock(notification_type=NOTIFICATION_TYPE_PROBLEM):
    ANY_SERVICE_PROBLEM_ID = "12345"
    ANY_SERVICE_STATE = "any service state"
    ANY_SERVICE_DESCRIPTION = "foo application services"
    ANY_HOST_ADDRESS = "myserv1.server.com"
    ANY_COMMENT = "any comment"
    ANY_NOTIFICATION_AUTHOR = "any notification author"
    ANY_HOST_OUTPUT = 'any host output'
    ANY_HOST_STATE = 'any host state'
    ANY_SERVICE_MESSAGE = "any service message"
    ANY_SHORT_DATE_TIME = "11-26-2013 15:42:05"

    environment = Mock()
    environment.service_description = ANY_SERVICE_DESCRIPTION
    environment.service_state = ANY_SERVICE_STATE
    environment.host_state = ANY_HOST_STATE
    environment.short_date_time = ANY_SHORT_DATE_TIME
    environment.host_address = ANY_HOST_ADDRESS
    environment.service_output = ANY_SERVICE_MESSAGE
    environment.host_output = ANY_HOST_OUTPUT
    environment.notification_type = notification_type
    environment.notification_author = ANY_NOTIFICATION_AUTHOR
    environment.notification_comment = ANY_COMMENT
    environment.service_problem_id = ANY_SERVICE_PROBLEM_ID
    return environment


class IssueDummy(Issue):

    def __init__(self, icinga_environment):
        self.icinga_environment = icinga_environment

    def execute(self):
        pass


class TestIssue(unittest.TestCase):

    EXPECTED_PROBLEM_DESCRIPTION_WITH_SERVICE = textwrap.dedent("""
        {color:#3b0b0b}*Icinga Problem Alert*{color}

        The following information was provided by Icinga:
        * Date & Time: 11-26-2013 15:42:05
        * Host Address: myserv1.server.com
        * Status Information: any service message
        * Current Host State: any host state
        * Current Service State: any service state""").strip()

    EXPECTED_ACKNOWLEDGEMENT_DESCRIPTION_WITH_SERVICE = textwrap.dedent("""
        {color:#0f5d94}*Icinga Acknowledgement*{color}

        The following information was provided by Icinga:
        * Date & Time: 11-26-2013 15:42:05
        * Host Address: myserv1.server.com
        * Status Information: any service message
        * Current Host State: any host state
        * Current Service State: any service state
        * Notification Author: any notification author
        * Notification Comment: any comment""").strip()

    EXPECTED_PROBLEM_DESCRIPTION_WITHOUT_SERVICE_DESCRIPTION = textwrap.dedent("""
        {color:#3b0b0b}*Icinga Problem Alert*{color}

        The following information was provided by Icinga:
        * Date & Time: 11-26-2013 15:42:05
        * Host Address: myserv1.server.com
        * Status Information: any host output
        * Current Host State: any host state""").strip()

    EXPECTED_RECOVERY_DESCRIPTION_WITH_SERVICE = textwrap.dedent("""
        {color:#0b3b0b}*Icinga Recovery Alert*{color}

        The following information was provided by Icinga:
        * Date & Time: 11-26-2013 15:42:05
        * Host Address: myserv1.server.com
        * Status Information: any service message
        * Current Host State: any host state
        * Current Service State: any service state

        This ticket was closed automatically.""").strip()

    def setUp(self):
        self.icinga_environment = create_icinga_environment_mock()
        self.issue = IssueDummy(self.icinga_environment)

    def test_description_for_problem_with_service_description(self):
        actual_description = self.issue.create_description()

        self.assertEqual(actual_description, self.EXPECTED_PROBLEM_DESCRIPTION_WITH_SERVICE)

    def test_description_for_problem_without_service_description(self):
        self.icinga_environment.service_description = None

        actual_description = self.issue.create_description()

        self.assertEqual(actual_description,
                         self.EXPECTED_PROBLEM_DESCRIPTION_WITHOUT_SERVICE_DESCRIPTION)

    def test_description_for_acknowledgement_with_service_description(self):
        self.icinga_environment.notification_type = "ACKNOWLEDGEMENT"

        actual_description = self.issue.create_description()

        self.assertEqual(actual_description, self.EXPECTED_ACKNOWLEDGEMENT_DESCRIPTION_WITH_SERVICE)

    def test_description_for_recovery_with_service_description(self):
        self.icinga_environment.notification_type = "RECOVERY"

        actual_description = self.issue.create_description()

        self.assertEqual(actual_description, self.EXPECTED_RECOVERY_DESCRIPTION_WITH_SERVICE)

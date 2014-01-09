import unittest

from icinga2jira import IcingaEnvironment

ANY_PROJECT_KEY = 'MON'
ANY_ISSUE_TYPE = 'Technical task'
ANY_LAST_SERVICE_PROBLEM_ID = "76540"
ANY_PRIORITY_ID = "12"
ANY_HOST_PROBLEM_ID = "76543"
ANY_SERVICE_PROBLEM_ID = "12345"
ANY_SERVICE_STATE = "any service state"
ANY_HOSTNAME = "myserver1"
ANY_SERVICE_DESCRIPTION = "foo application services"
ANY_COMMENT = "any comment"
ANY_NOTIFICATION_AUTHOR = "any notification author"
ANY_HOST_OUTPUT = 'any host output'
ANY_HOST_STATE = 'any host state'
NOTIFICATION_TYPE_PROBLEM = "PROBLEM"
NOTIFICATION_TYPE_RECOVERY = "RECOVERY"
ANY_SERVICE_MESSAGE = "any service message"
ANY_SHORT_DATE_TIME = "11-26-2013 15:42:05"
ANY_LAST_HOST_PROBLEM_ID = "9999999999999"
ANY_ICINGA_LABEL_STRING_FORMAT = "ICI#%s#%s"


def create_valid_environment_dict_for_host_problem():
    return {
        'ICINGA_HOSTNAME': ANY_HOSTNAME,
        'ICINGA_HOSTOUTPUT': ANY_HOST_OUTPUT,
        'ICINGA_HOSTPROBLEMID': ANY_HOST_PROBLEM_ID,
        'ICINGA_HOSTSTATE': ANY_HOST_STATE,
        'ICINGA_NOTIFICATIONAUTHOR': ANY_NOTIFICATION_AUTHOR,
        'ICINGA_NOTIFICATIONCOMMENT': ANY_COMMENT,
        'ICINGA_NOTIFICATIONTYPE': NOTIFICATION_TYPE_PROBLEM,
        'ICINGA_SHORTDATETIME': ANY_SHORT_DATE_TIME,
        }

def create_valid_environment_dict_for_host_recovery():
    return {
        'ICINGA_HOSTNAME': ANY_HOSTNAME,
        'ICINGA_HOSTOUTPUT': ANY_HOST_OUTPUT,
        'ICINGA_LASTHOSTPROBLEMID': ANY_LAST_HOST_PROBLEM_ID,
        'ICINGA_HOSTSTATE': ANY_HOST_STATE,
        'ICINGA_NOTIFICATIONAUTHOR': ANY_NOTIFICATION_AUTHOR,
        'ICINGA_NOTIFICATIONCOMMENT': ANY_COMMENT,
        'ICINGA_NOTIFICATIONTYPE': NOTIFICATION_TYPE_RECOVERY,
        'ICINGA_SHORTDATETIME': ANY_SHORT_DATE_TIME,
        }

def create_valid_environment_dict_for_service_problem():
    return {
        'ICINGA_HOSTNAME': ANY_HOSTNAME,
        'ICINGA_HOSTOUTPUT': ANY_HOST_OUTPUT,
        'ICINGA_HOSTSTATE': ANY_HOST_STATE,
        'ICINGA_NOTIFICATIONAUTHOR': ANY_NOTIFICATION_AUTHOR,
        'ICINGA_NOTIFICATIONCOMMENT': ANY_COMMENT,
        'ICINGA_NOTIFICATIONTYPE': NOTIFICATION_TYPE_PROBLEM,
        'ICINGA_SERVICEDESC': ANY_SERVICE_DESCRIPTION,
        'ICINGA_SERVICEOUTPUT': ANY_SERVICE_MESSAGE,
        'ICINGA_SERVICEPROBLEMID': ANY_SERVICE_PROBLEM_ID,
        'ICINGA_SERVICESTATE': ANY_SERVICE_STATE,
        'ICINGA_SHORTDATETIME': ANY_SHORT_DATE_TIME,
        }

def create_valid_environment_dict_for_service_recovery():
    return {
        'ICINGA_HOSTNAME': ANY_HOSTNAME,
        'ICINGA_HOSTOUTPUT': ANY_HOST_OUTPUT,
        'ICINGA_HOSTSTATE': ANY_HOST_STATE,
        'ICINGA_LASTSERVICEPROBLEMID': ANY_LAST_SERVICE_PROBLEM_ID,
        'ICINGA_NOTIFICATIONAUTHOR': ANY_NOTIFICATION_AUTHOR,
        'ICINGA_NOTIFICATIONCOMMENT': ANY_COMMENT,
        'ICINGA_NOTIFICATIONTYPE': NOTIFICATION_TYPE_RECOVERY,
        'ICINGA_SERVICEDESC': ANY_SERVICE_DESCRIPTION,
        'ICINGA_SERVICEOUTPUT': ANY_SERVICE_MESSAGE,
        'ICINGA_SERVICESTATE': ANY_SERVICE_STATE,
        'ICINGA_SERVICEJIRA_PRIORITY_ID': ANY_PRIORITY_ID,
        'ICINGA_SHORTDATETIME': ANY_SHORT_DATE_TIME,
        }


class IcingaEnvironmentTest(unittest.TestCase):

    def test_icinga_environment_should_skip_nonexisting_or_empty_environment_values(self):
        environment = create_valid_environment_dict_for_service_problem()
        environment['ICINGA_LASTHOSTPROBLEMID'] = None
        environment['ICINGA_HOSTPROBLEMID'] = ''
        environment.pop('ICINGA_NOTIFICATIONCOMMENT')

        icinga_environment = IcingaEnvironment(environment)
        self.assertEqual(icinga_environment.last_host_problem_id, None)
        self.assertEqual(icinga_environment.host_problem_id, None)
        self.assertEqual(icinga_environment.notification_comment, None)


    def test_validation_raises_value_error_with_empty_environment(self):
        self.assertRaises(ValueError, IcingaEnvironment, {})

    def test_validation_for_PROBLEM_raises_value_error_with_only_notification_type(self):
        environment = {'ICINGA_NOTIFICATIONTYPE': NOTIFICATION_TYPE_PROBLEM}
        self.assertRaises(ValueError, IcingaEnvironment, environment)

    def test_validation_for_PROBLEM_succeeds_with_minimal_service_state_environment(self):
        environment = {'ICINGA_NOTIFICATIONTYPE': NOTIFICATION_TYPE_PROBLEM,
                       'ICINGA_SERVICEDESC': ANY_SERVICE_DESCRIPTION,
                       'ICINGA_HOSTNAME': ANY_HOSTNAME,
                       'ICINGA_SERVICESTATE': ANY_SERVICE_STATE,
                       'ICINGA_SERVICEPROBLEMID': ANY_SERVICE_PROBLEM_ID,
                       }
        IcingaEnvironment(environment)

    def test_validation_for_PROBLEM_raises_ValueError_when_service_problem_id_is_empty(self):
        environment = {'ICINGA_NOTIFICATIONTYPE': NOTIFICATION_TYPE_PROBLEM,
                       'ICINGA_SERVICEDESC': ANY_SERVICE_DESCRIPTION,
                       'ICINGA_HOSTNAME': ANY_HOSTNAME,
                       'ICINGA_SERVICESTATE': ANY_SERVICE_STATE,
                       'ICINGA_SERVICEPROBLEMID': '',
                       }
        self.assertRaises(ValueError, IcingaEnvironment, environment)


    def test_validation_for_PROBLEM_succeeds_with_minimal_host_environment(self):
        environment = {'ICINGA_NOTIFICATIONTYPE': NOTIFICATION_TYPE_PROBLEM,
                       'ICINGA_HOSTNAME': ANY_HOSTNAME,
                       'ICINGA_HOSTSTATE': ANY_HOST_STATE,
                       'ICINGA_HOSTPROBLEMID': ANY_HOST_PROBLEM_ID,
                       }
        IcingaEnvironment(environment)

    def test_validation_for_PROBLEM_raises_when_host_problem_id_is_empty(self):
        environment = {'ICINGA_NOTIFICATIONTYPE': NOTIFICATION_TYPE_PROBLEM,
                       'ICINGA_HOSTNAME': ANY_HOSTNAME,
                       'ICINGA_HOSTSTATE': ANY_HOST_STATE,
                       'ICINGA_HOSTPROBLEMID': '',
                       }
        self.assertRaises(ValueError, IcingaEnvironment, environment)

    def test_validation_for_RECOVERY_succeeds_with_minimal_service_state_environment(self):
        environment = {'ICINGA_NOTIFICATIONTYPE': NOTIFICATION_TYPE_RECOVERY,
                       'ICINGA_SERVICEDESC': ANY_SERVICE_DESCRIPTION,
                       'ICINGA_LASTSERVICEPROBLEMID': ANY_LAST_SERVICE_PROBLEM_ID,
                       }
        IcingaEnvironment(environment)

    def test_validation_for_RECOVERY_succeeds_with_minimal_host_state_environment(self):
        environment = {'ICINGA_NOTIFICATIONTYPE': NOTIFICATION_TYPE_RECOVERY,
                       'ICINGA_SERVICEDESC': None,
                       'ICINGA_LASTHOSTPROBLEMID': ANY_LAST_HOST_PROBLEM_ID,
                       }
        IcingaEnvironment(environment)

    def test_validation_for_RECOVERY_raises_for_missing_service_and_host_problem_id(self):
        environment = {'ICINGA_NOTIFICATIONTYPE': NOTIFICATION_TYPE_RECOVERY}
        self.assertRaises(ValueError, IcingaEnvironment, environment)

    def test_has_new_problem_returns_true(self):
        environment = IcingaEnvironment(create_valid_environment_dict_for_service_problem())
        self.assertTrue(environment.has_new_problem())

    def test_service_is_recovered(self):
        test_dict = create_valid_environment_dict_for_service_recovery()
        environment = IcingaEnvironment(test_dict)
        self.assertTrue(environment.is_recovered())

    def test_host_is_recovered(self):
        test_dict = create_valid_environment_dict_for_host_recovery()
        environment = IcingaEnvironment(test_dict)
        self.assertTrue(environment.is_recovered())

    def test_when_is_service_issue_is_true_then_is_host_issue_is_false(self):
        environment = IcingaEnvironment(create_valid_environment_dict_for_service_problem())
        self.assertTrue(environment.is_service_issue())
        self.assertFalse(environment.is_host_issue())

    def test_get_recovery_last_problem_id_raises_type_error_when_not_in_recovery_state(self):
        environment = IcingaEnvironment(create_valid_environment_dict_for_host_problem())
        self.assertRaises(TypeError, environment.get_recovery_last_problem_id)

    def test_get_recovery_last_problem_id_returns_last_service_problem_id_for_service_recovery(self):
        environment = IcingaEnvironment(create_valid_environment_dict_for_service_recovery())
        problem_id = environment.get_recovery_last_problem_id()
        self.assertEqual(ANY_LAST_SERVICE_PROBLEM_ID, problem_id)

    def test_get_recovery_last_problem_id_returns_last_host_problem_id_for_host_recovery(self):
        test_dict = create_valid_environment_dict_for_host_recovery()
        environment = IcingaEnvironment(test_dict)
        problem_id = environment.get_recovery_last_problem_id()
        self.assertEqual(ANY_LAST_HOST_PROBLEM_ID, problem_id)

    def test_get_jira_recovery_label_returns_correct_value_for_service_recovery(self):
        test_dict = create_valid_environment_dict_for_service_recovery()

        environment = IcingaEnvironment(test_dict)

        self.assertEqual(ANY_ICINGA_LABEL_STRING_FORMAT % (ANY_LAST_SERVICE_PROBLEM_ID, ANY_HOSTNAME),
                         environment.get_jira_recovery_label())

    def test_get_jira_recovery_label_returns_correct_value_for_host_recovery(self):
        test_dict = create_valid_environment_dict_for_host_recovery()

        environment = IcingaEnvironment(test_dict)

        self.assertEqual(ANY_ICINGA_LABEL_STRING_FORMAT % (ANY_LAST_HOST_PROBLEM_ID, ANY_HOSTNAME),
                         environment.get_jira_recovery_label())

    def test_create_labels_list_contains_service_problem_id(self):
        test_dict = create_valid_environment_dict_for_service_problem()
        environment = IcingaEnvironment(test_dict)
        actual_labels = environment.create_labels_list()

        self.assertEqual(len(actual_labels), 1)
        self.assertEqual(actual_labels[0], ANY_ICINGA_LABEL_STRING_FORMAT % (ANY_SERVICE_PROBLEM_ID, ANY_HOSTNAME))

    def test_create_labels_list_contains_host_problem_id(self):
        test_dict = create_valid_environment_dict_for_host_problem()
        environment = IcingaEnvironment(test_dict)
        actual_labels = environment.create_labels_list()

        self.assertEqual(1, len(actual_labels))
        self.assertEqual(ANY_ICINGA_LABEL_STRING_FORMAT % (ANY_HOST_PROBLEM_ID, ANY_HOSTNAME), actual_labels[0])

    def test_create_icinga_label_with_prefix_and_hostname(self):
        test_dict = create_valid_environment_dict_for_host_problem()
        environment = IcingaEnvironment(test_dict)
        actual_label = environment._create_icinga_label(ANY_HOST_PROBLEM_ID)

        self.assertEqual(ANY_ICINGA_LABEL_STRING_FORMAT % (ANY_HOST_PROBLEM_ID, ANY_HOSTNAME), actual_label)


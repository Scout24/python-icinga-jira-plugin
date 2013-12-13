import unittest
from docopt import DocoptExit
import icinga2jira as i2j
import textwrap
from StringIO import StringIO
from ConfigParser import NoSectionError
from mock import patch, Mock
from jira.exceptions import JIRAError

ANY_TEXT_PARAMETER = "any service output"
ANY_CONFIG_PATH = "/tmp/config.ini"
ANY_URL = 'http://www.example.com'
ANY_USERNAME = 'god'
ANY_PASSWORD = 'h3aven'
ANY_PROJECT_KEY = 'PROJECT_KEY'
ANY_ISSUE_TYPE = 'Issue type'
NOTIFICATION_TYPE_PROBLEM = "PROBLEM"

TEMPLATE = textwrap.dedent("""
    [settings]
    url = %s
    username = %s
    password = %s
    jira_project_key = %s
    jira_issue_type = %s
""" % (ANY_URL, ANY_USERNAME, ANY_PASSWORD,
       ANY_PROJECT_KEY, ANY_ISSUE_TYPE))


def create_icinga_environment_mock(notification_type=NOTIFICATION_TYPE_PROBLEM):

        environment = Mock()
        environment.notification_type = notification_type
        return environment


def create_template_with_skipped_line(line_idx):
    lines = TEMPLATE.strip().split('\n')
    return '\n'.join(lines[0:line_idx] + lines[line_idx + 1:])


class TestReadConfig(unittest.TestCase):

    def test_parse_and_validate_config_file_delivers_all_expected_fields(self):
        self.assert_that_configuration_correctly_read_file(i2j.parse_and_validate_config_file(StringIO(TEMPLATE)))

    def test_parse_and_validate_config_file_throws_error_when_config_does_not_contain_settings_section(self):
        config = StringIO(textwrap.dedent("""
        [somethingelse]
        url = fsdfsdfsdf
        """))
        self.assertRaises(NoSectionError, i2j.parse_and_validate_config_file, config)

    def test_parse_and_validate_config_file_throws_error_when_config_missing_value(self):
        for line_idx in range(1, 6):
            target = create_template_with_skipped_line(line_idx)
            self.assertRaises(ValueError, i2j.parse_and_validate_config_file, StringIO(target))

    def assert_that_configuration_correctly_read_file(self, config_dict):
        self.assertEqual(config_dict['url'], ANY_URL)
        self.assertEqual(config_dict['username'], ANY_USERNAME)
        self.assertEqual(config_dict['password'], ANY_PASSWORD)
        self.assertEqual(config_dict['jira_project_key'], ANY_PROJECT_KEY)
        self.assertEqual(config_dict['jira_issue_type'], ANY_ISSUE_TYPE)


class TestParseOptions(unittest.TestCase):

    def test_parse_mandatory_parameter_config_and_c(self):
        argv = ['--config', ANY_CONFIG_PATH]
        actualOptions = i2j.parse_arguments(argv)
        self.assertEqual(actualOptions['--config'], ANY_CONFIG_PATH)

        argv = ['-c', ANY_CONFIG_PATH]
        actualOptions = i2j.parse_arguments(argv)
        self.assertEqual(actualOptions['--config'], ANY_CONFIG_PATH)

    def test_when_unallowed_options_are_set_an_error_is_thrown(self):
        self.assertRaises(DocoptExit, i2j.parse_arguments, ["--foo", "bar"])
        self.assertRaises(DocoptExit, i2j.parse_arguments, ["open", "--foo"])


class TestJIRAUsage(unittest.TestCase):

    def setUp(self):
        self.jira_mock = Mock()
        self.ticket = Mock()

    def test_open_jira_session_called_properly(self):
        with patch('icinga2jira.JIRA') as JIRA:
            JIRA.return_value = 'jira'
            result = i2j.open_jira_session('spam', 'eggs', 'ham')
            self.assertEqual(result, 'jira')
            JIRA.assert_called_with(basic_auth=('eggs', 'ham'),
                                    options={'verify': False, 'server': 'spam'})

    def test_open_jira_session_raises_exception(self):
        with patch('icinga2jira.JIRA') as JIRA:
            JIRA.side_effect = JIRAError()
            self.assertRaises(JIRAError, i2j.open_jira_session,
                              'spam', 'eggs', 'ham')

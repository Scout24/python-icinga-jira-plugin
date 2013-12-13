import unittest

from mock import Mock, patch
from jira.exceptions import JIRAError

from icinga2jira import CloseIssue, CantCloseTicketException

ANY_ISSUE = {'id': 'any id'}
ANY_TRANSITIONS = [{'name': 'Close', 'id': 45},
                   {'name': 'Start Work', 'id': 11},
                   ]


def create_issue_mock(key):
    issue = Mock()
    issue.key.return_value = key
    return issue


class TestCloseIssue(unittest.TestCase):

    def setUp(self):
        self.jira_mock = Mock()
        self.ticket = Mock()
        self.icinga_environment = Mock()
        self.icinga_environment.get_jira_recovery_label.return_value = 'ICI#123'
        self.close_issue = CloseIssue(self.jira_mock, self.icinga_environment)

    def test_find_jira_issue_by_label(self):
        self.jira_mock.search_issues.return_value = 'found issue'

        result = self.close_issue._find_jira_issues_by_label()

        self.assertEqual('found issue', result)
        self.ticket.get_jira_recovery_label.assert_called()
        self.jira_mock.search_issues.assert_called_with("labels='ICI#123'")

    def test_set_comment(self):
        with patch.object(CloseIssue, 'create_description', return_value='comment') as create_mock:
            close_issue = CloseIssue(self.jira_mock, self.icinga_environment)

            close_issue._set_comment(ANY_ISSUE)

            create_mock.create_description.assert_called()
            self.jira_mock.add_comment.assert_called_with(ANY_ISSUE, 'comment')

    def test_get_close_transition_returns_id_of_close_transition_in_issue(self):
        self.jira_mock.transitions.return_value = ANY_TRANSITIONS

        actual_transition_id = self.close_issue._get_close_transition({'id': 'any id'})

        self.assertEqual(45, actual_transition_id)

    def test_get_close_transition_with_unicode(self):
        self.jira_mock.transitions.return_value = ANY_TRANSITIONS

        actual_transition_id = self.close_issue._get_close_transition({'id': 'any id'})

        self.assertEqual(45, actual_transition_id)

    def test_get_close_transition_raises_exception_when_no_close_transition_has_been_found(self):
        transitions = [{'name': 'Start Work', 'id': 11}]
        self.jira_mock.transitions.return_value = transitions

        self.assertRaises(CantCloseTicketException,
                          self.close_issue._get_close_transition,
                          ANY_ISSUE)

    def test_get_close_transition_raises_exception_when_no_transitions_have_been_found(self):
        self.jira_mock.transitions.return_value = []

        self.assertRaises(CantCloseTicketException,
                          self.close_issue._get_close_transition,
                          ANY_ISSUE)

    def test_close_happy_trail(self):
        transitions = [{'name': 'Close', 'id': 45}]
        self.jira_mock.transitions.return_value = transitions

        self.close_issue._close(ANY_ISSUE)

        self.jira_mock.transition_issue.assert_called_with(ANY_ISSUE, 45)

    def test_close_on_already_closed_ticket_raises_exception(self):
        self.jira_mock.transitions.return_value = []

        self.assertRaises(CantCloseTicketException, self.close_issue._close, ANY_ISSUE)

    def test_close_reraises_exception_if_jira_fails(self):
        self.jira_mock.transitions.return_value = ANY_TRANSITIONS
        self.jira_mock.transition_issue.side_effect = JIRAError

        self.assertRaises(CantCloseTicketException,
                          self.close_issue._close, ANY_ISSUE)

    def test_execute_is_called_properly_and_returns_list_of_handled_issues(self):
        find_mock = Mock(return_value=['issue1', 'issue2'])
        close_mock = Mock()
        comment_mock = Mock()

        with patch.multiple(CloseIssue,
                            _find_jira_issues_by_label=find_mock,
                            _close=close_mock,
                            _set_comment=comment_mock
                            ) as values:
            close_issue = CloseIssue(self.jira_mock, self.icinga_environment)
            result = close_issue.execute()

            self.assertEqual(find_mock.call_count, 1)
            self.assertEqual(close_mock.call_count, 2)
            comment_mock.assert_called_twice_with(comment_str='comment')
            self.assertEqual(['issue1', 'issue2'], result)

    def test_execute_skips_issues_causing_CantCloseTicketException(self):
        find_mock = Mock(return_value=[create_issue_mock('a'), create_issue_mock('b')])
        close_mock = Mock(side_effect=CantCloseTicketException())
        comment_mock = Mock()

        with patch.multiple(CloseIssue,
                            _find_jira_issues_by_label=find_mock,
                            _close=close_mock,
                            _set_comment=comment_mock
                            ) as values:
            close_issue = CloseIssue(self.jira_mock, self.icinga_environment)
            result = close_issue.execute()

            self.assertEqual(find_mock.call_count, 1)
            self.assertEqual(close_mock.call_count, 2)
            comment_mock.assert_not_called()
            self.assertEqual([], result)

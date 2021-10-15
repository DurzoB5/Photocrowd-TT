from django.test import TestCase

from .factories import CompetitionFactory, SubmissionFactory, UserFactory


class UserTestCase(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()

    def test_user_string(self) -> None:
        """Test the User models string representation"""
        self.assertEqual(str(self.user), self.user.username)


class CompetitionTestCase(TestCase):
    def setUp(self) -> None:
        self.competition = CompetitionFactory()

    def test_competition_string(self) -> None:
        """Test the Competition models string representation"""
        self.assertEqual(str(self.competition), self.competition.name)


class SubmissionTestCase(TestCase):
    def setUp(self) -> None:
        self.submission = SubmissionFactory()

    def test_submission_string(self) -> None:
        """Test the Submission models string representation"""
        self.assertEqual(
            str(self.submission),
            f'{self.submission.user.username} - {self.submission.name}',
        )

from uuid import uuid4

from django.test import TestCase

from leaderboard.models import Submission, User
from leaderboard.services import UserService
from leaderboard.tests.factories import SubmissionFactory, UserFactory


class GeUsersTestCase(TestCase):
    def setUp(self) -> None:
        self.service = UserService.get_users
        self.users = UserFactory.create_batch(size=50)
        self.submission = SubmissionFactory(user=self.users[0])

    def test_get_users(self) -> None:
        """
        Test all Users are returned from the UserService
        ordered by the username
        """
        query_set = self.service()
        self.assertEqual(query_set.count(), 50)
        self.users.sort(key=lambda x: x.username)
        self.assertEqual(list(query_set), self.users)

    def test_get_users_with_filtering_by_invalid_field(self) -> None:
        """Test filtering on a field that is not valid will return all results"""
        query_set = self.service(filters={'test': 'test'})
        self.assertEqual(query_set.count(), 50)

    def test_get_users_ordering_by_invalid_field(self) -> None:
        """Test get Users are returned ordered by username when invalid field passed"""
        query_set = self.service(filters={'ordering': 'test'})
        self.users.sort(key=lambda x: x.username)
        self.assertEqual(list(query_set), self.users)

    def test_get_no_users(self) -> None:
        """Test an empty queryset is returned from the UserService if no Users exist"""
        User.objects.all().delete()

        self.assertEqual(self.service().count(), 0)


class GetUserTestCase(TestCase):
    def setUp(self) -> None:
        self.service = UserService.get_user
        self.user = UserFactory()

    def test_get_user(self) -> None:
        """Test all Users are returned from the UserService"""
        self.assertEqual(self.service(user_id=self.user.id), self.user)

    def test_get_user_by_when_does_not_exist(self):
        with self.assertRaises(User.DoesNotExist):
            self.service(user_id=uuid4())


class GetUserByUsernameTestCase(TestCase):
    def setUp(self) -> None:
        self.service = UserService.get_user_by_username
        self.user = UserFactory()

    def test_get_user_by_username(self):
        """Test getting a User by it's username"""
        self.assertEqual(self.service(username=self.user.username), self.user)

    def test_get_user_with_invalid_username(self):
        """Test getting a User by it's username when the username doesn't exist"""
        with self.assertRaises(User.DoesNotExist):
            self.service(username='ghljj')


class GetUserRankingsTestCase(TestCase):
    def setUp(self) -> None:
        self.service = UserService.get_user_rankings
        self.user = UserFactory()
        self.new_user = UserFactory()
        self.submissions = SubmissionFactory.create_batch(user=self.user, size=3)
        SubmissionFactory(user=self.new_user)
        self.ranking_score = 0
        for submission in self.submissions:
            self.ranking_score += submission.score

        self.old_user = UserFactory()
        self.old_user_submissions = SubmissionFactory.create_batch(
            30, user=self.old_user
        )
        self.old_ranking_score = 0
        for submission in Submission.objects.filter(user=self.old_user).order_by(
            '-score'
        )[:24]:
            self.old_ranking_score += submission.score

    def test_get_user_rankings(self):
        """Test generating user rankings"""
        self.old_user.delete()
        self.assertEqual(
            self.service()[0].total_score, self.ranking_score  # type: ignore
        )

    def test_get_user_rankings_not_enough_submissions(self):
        """Test a user without at least 3 submissions doesn't get a ranking"""
        self.assertNotIn(self.new_user, self.service())

    def test_only_best_24_used(self):
        """Test only the best 24 submissions are used"""
        self.user.delete()
        rankings = self.service()

        self.assertEqual(
            rankings[0].total_score, self.old_ranking_score  # type: ignore
        )
        self.assertEqual(rankings[0].rank, 1)  # type: ignore

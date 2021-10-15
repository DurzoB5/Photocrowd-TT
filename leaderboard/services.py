import logging
from typing import Any, Dict, Optional, Sequence, Union
from uuid import UUID

from django.db.models import Count, QuerySet
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.query import Prefetch

from .filters import CompetitionFilter, SubmissionFilter, UserFilter
from .models import Competition, Submission, User

LOGGER = logging.getLogger('photocrowd')


class UserService:
    """Service for interacting with the :class:`User` model"""

    @staticmethod
    def create_user(*, username: str, **kwargs) -> User:
        """
        Create a new user in the system

        :param username: The username to give the new user.
        :return: The newly created :class:`User`.
        """
        LOGGER.info(f'UserService:create_user called with {username}')

        return User.objects.create_user(username=username, **kwargs)

    @staticmethod
    def get_user(*, user_id: Union[UUID, str]) -> User:
        """
        Get details of a :class:`User` using it's ID

        :param user_id: The ID of the :class:`User`.
        :raise User.DoesNotExist: If a :class:`User` with the specified ID
            does not exist.
        :return: The :class:`User` object.
        """
        LOGGER.debug(f'UserService:get_user called with {user_id}')

        return User.objects.get(id=user_id)

    @staticmethod
    def get_or_create_user_by_username(
        *, username: str, defaults: Dict[str, Any]
    ) -> User:
        """
        Get the details of a :class:`User` using it's username or create the
        :class:`User` using the said username and any other data provided in
        defaults

        :param username: The username of the :class:`User`.
        :param defaults: Any data to use to create the :class:`User` if it does not
            exist.
        :return: The :class:`User` retrieved or created.
        """
        LOGGER.debug(
            f'UserService:get_or_create_user_by_username called with {username}'
        )

        try:
            return UserService.get_user_by_username(username=username)
        except User.DoesNotExist:
            return UserService.create_user(username=username, **defaults)

    @staticmethod
    def get_user_by_username(*, username: str) -> User:
        """
        Get details of a :class:`User` using it's username.

        This service is case insensitive.

        :param username: The username of the :class:`User`.
        :raise User.DoesNotExist: If a :class:`User` with the specified
            username does not exist.
        :return: The :class:`User` object.
        """
        LOGGER.debug(f'UserService:get_user_by_username called with {username}')

        return User.objects.get(username__iexact=username)

    @staticmethod
    def get_users(*, filters: Optional[Dict[str, Any]] = None) -> QuerySet:
        """
        Get all :class:`User`\s

        :param filters: A dictionary of filters to apply to the QuerySet
        :return: A filtered :class:`django.db.models.QuerySet`
        """
        LOGGER.debug('UserService:get_users called')
        filters = filters or {}

        qs = (
            User.objects.all()
            .prefetch_related('submissions', 'submissions__competition')
            .order_by('username')
        )  # order_by will be ignored if passed in filter

        return UserFilter(filters, qs).qs

    @staticmethod
    def get_user_rankings_old():
        pass

    @staticmethod
    def get_user_rankings() -> Sequence[User]:
        """
        Get all ranking scores for :class:`User`\s that have submitted at least three
        submissions
        """
        # Subquery to get the highest 24 submissions per user
        sub_query = Subquery(
            Submission.objects.filter(user_id=OuterRef('user_id'))
            .order_by('-score')[:24]
            .values_list('id', flat=True)
        )

        #  Fetch the top 24 submissions per user and store it in top_submissions
        prefetch = Prefetch(
            'submissions',
            queryset=Submission.objects.filter(id__in=sub_query),
            to_attr='top_submissions',
        )

        # Query users that have at least submissions and prefetch their top 24
        users = list(
            User.objects.annotate(submission_count=Count('submissions'))
            .filter(submission_count__gte=3)
            .prefetch_related(prefetch)
        )

        # Loop through and combine the scores of each users top_submissions
        for user in users:
            user_score = 0
            for submission in user.top_submissions:  # type: ignore
                user_score += submission.score

            setattr(user, 'total_score', user_score)

        # Use total_score to rank the users in order
        users = sorted(
            users, key=lambda user: user.total_score, reverse=True  # type: ignore
        )

        # Generate a rank for each user
        rank = 1
        for user in users:
            setattr(user, 'rank', rank)
            rank += 1

        return users


class CompetitionService:
    """Service for interacting with the :class:`Competition` model"""

    @staticmethod
    def create_competition(*, name: str) -> Competition:
        """
        Create a new :class:`Competition`

        :param name: The name to give the :class:`Competition`.
        :return: The newly created Competition.
        """
        LOGGER.info(f'CompetitionService:create_competition called with {name}')

        return Competition.objects.create(name=name)

    @staticmethod
    def get_competition(*, competition_id: Union[UUID, str]) -> Competition:
        """
        Get details of a :class:`Competition` using it's ID

        :param competition_id: The ID of the :class:`Competition`.
        :raise Competition.DoesNotExist: If a :class:`Competition` with the specified
            ID does not exist.
        :return: The :class:`Competition` object.
        """
        LOGGER.debug(f'CompetitionService:get_competition called with {competition_id}')

        return Competition.objects.get(id=competition_id)

    @staticmethod
    def get_competition_by_name(*, name: str) -> Competition:
        """
        Get details of a :class:`Competition` using it's name

        :param name: The name of the :class:`Competition`.
        :raise Competition.DoesNotExist: If a :class:`Competition` doesn't exist with
            the provided name.
        :return: The :class:`Competition` object.
        """
        LOGGER.debug(f'CompetitionService:get_competition_by_name called with {name}')

        return Competition.objects.get(name=name)

    @staticmethod
    def get_or_create_competition(*, name: str) -> Competition:
        """
        Get the details of a :class:`Competition` or create one if it does not exist

        :param name: The name of the :class:`Competition`.
        :return: The :class:`Competition` retrieved or created.
        """
        LOGGER.debug(f'CompetitionService:get_or_create_competition called with {name}')

        try:
            return CompetitionService.get_competition_by_name(name=name)
        except Competition.DoesNotExist:
            return CompetitionService.create_competition(name=name)

    @staticmethod
    def get_competitions(*, filters: Optional[Dict[str, Any]] = None) -> QuerySet:
        """
        Get all :class:`Competition`\s

        :param filters: A dictionary of filters to apply to the QuerySet
        :return: A filtered :class:`django.db.models.QuerySet`
        """
        LOGGER.debug('CompetitionService:get_competitions called')
        filters = filters or {}

        qs = (
            Competition.objects.all()
            .prefetch_related('submissions', 'submissions__user')
            .order_by('name')
        )  # order_by will be ignored if passed in filter

        return CompetitionFilter(filters, qs).qs


class SubmissionService:
    """Service for interacting with the :class:`Submission` model"""

    @staticmethod
    def create_submission(
        *,
        user: Union[User, UUID, str],
        competition: Union[Competition, UUID, str],
        name: str,
        score: int = 0,
    ) -> Submission:
        """
        Create a new :class:`Submission`

        :param user: The :class:`User` or ID of the :class:`User` that is creating this
            :class:`Submission`.
        :param competition: The :class:`Competition` or ID of the :class:`Competition`
            this :class:`Submission` is for.
        :param name: The name of the submission.
        :param score: The score this :class:`Submission` received, or None if not
            scored yet.
        :return: The newly created :class:`Submission`.
        """
        LOGGER.info(f'SubmissionService.create_submission called with {name}')

        # If not a User object then get it from the DB
        if not isinstance(user, User):
            user = UserService.get_user(user_id=user)

        # If not a Competition object then get it from the DB
        if not isinstance(competition, Competition):
            competition = CompetitionService.get_competition(competition_id=competition)

        return Submission.objects.create(
            user=user, competition=competition, name=name, score=score
        )

    @staticmethod
    def get_submissions(*, filters: Optional[Dict[str, Any]] = None) -> QuerySet:
        """
        Get all :class:`Submission`\s

        :param filters: A dictionary of filters to apply to the QuerySet
        :return: A filtered :class:`django.db.models.QuerySet`
        """
        LOGGER.debug('SubmissionService:get_submissions called')
        filters = filters or {}

        qs = (
            Submission.objects.all()
            .prefetch_related('user', 'competition')
            .order_by('score')
        )  # order_by will be ignored if passed in filter

        return SubmissionFilter(filters, qs).qs

    @staticmethod
    def get_submission(*, submission_id: Union[str, UUID]) -> Submission:
        """
        Get a specific ::class:`Submission` from the database

        :param submission_id: The ID of the :class:`Submission`
        :raise Submission.DoesNotExist: If a :class:`Submission` with the provided ID
            does not exist
        :return: The :class:`Submission` object
        """
        LOGGER.debug(f'SubmissionService:get_submission called with {submission_id}')

        return Submission.objects.get(id=submission_id)

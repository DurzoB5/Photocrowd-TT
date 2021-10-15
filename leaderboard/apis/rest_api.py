from typing import Union
from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import exceptions as rest_exceptions
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from leaderboard.models import Competition, Submission, User
from leaderboard.pagination import HeaderLimitOffsetPagination, get_paginated_response
from leaderboard.services import CompetitionService, SubmissionService, UserService


class BaseFilterSerializer(serializers.Serializer):
    """Base serializer for filtering that provides the ability to order results"""

    ordering = serializers.CharField(required=False)


class APIErrorsMixin:
    """
    Mixin that transforms Django and Python exceptions into rest_framework ones
    """

    expected_exceptions = {
        ValueError: rest_exceptions.ValidationError,
        ValidationError: rest_exceptions.ValidationError,
        ObjectDoesNotExist: rest_exceptions.NotFound,
    }

    def handle_exception(self, exception):
        if isinstance(exception, tuple(self.expected_exceptions.keys())):
            try:
                drf_exception_class = self.expected_exceptions[exception.__class__]
            except KeyError:
                exception_parent = type(exception).__bases__[0]
                drf_exception_class = self.expected_exceptions[exception_parent]
            drf_exception = drf_exception_class(str(exception))

            return super().handle_exception(drf_exception)  # type: ignore

        return super().handle_exception(exception)  # type: ignore


class UserFilterSerializer(BaseFilterSerializer):
    username = serializers.CharField(required=False)


class CompetitionFilterSerializer(BaseFilterSerializer):
    name = serializers.CharField(required=False)


class SubmissionFilterSerializer(BaseFilterSerializer):
    user_id = serializers.UUIDField(required=False)
    competition_id = serializers.UUIDField(required=False)


class SubmissionUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class SubmissionCompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competition
        fields = ['id', 'name']


class SubmissionSerializer(serializers.ModelSerializer):
    user = SubmissionUserSerializer()
    competition = SubmissionCompetitionSerializer()

    class Meta:
        model = Submission
        fields = ['id', 'name', 'user', 'competition']


class UserSerializer(serializers.ModelSerializer):
    submissions = SubmissionSerializer(many=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'last_login',
            'is_superuser',
            'submissions',
        ]


class CompetitionSerializer(serializers.ModelSerializer):
    submissions = SubmissionSerializer(many=True)

    class Meta:
        model = Competition
        fields = ['id', 'name', 'submissions']


class RankingSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    username = serializers.CharField()
    total_score = serializers.IntegerField()
    rank = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id', 'username', 'total_score', 'rank']


class UserViewSet(APIErrorsMixin, ViewSet):
    queryset = User.objects.all()

    def list(self, request: Request) -> Response:
        """List all :class:`User`\s"""
        filters_serializer = UserFilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        users = UserService.get_users(filters=filters_serializer.validated_data)

        return get_paginated_response(
            pagination_class=HeaderLimitOffsetPagination,
            serializer_class=UserSerializer,
            queryset=users,
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, user_id: Union[str, UUID]) -> Response:
        """
        Retrieve a specific :class:`User` based on it's ID

        :param user_id: The ID of the :class:`User` to retrieve
        """
        user = UserService.get_user(user_id=user_id)

        serializer = UserSerializer(user)

        return Response(serializer.data)


class CompetitionViewSet(APIErrorsMixin, ViewSet):
    queryset = Competition.objects.all()

    def list(self, request: Request) -> Response:
        """List all :class:`Competition`\s"""
        filters_serializer = CompetitionFilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        competitions = CompetitionService.get_competitions(
            filters=filters_serializer.validated_data
        )

        return get_paginated_response(
            pagination_class=HeaderLimitOffsetPagination,
            serializer_class=CompetitionSerializer,
            queryset=competitions,
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, competition_id: Union[str, UUID]) -> Response:
        """
        Retrieve a specific :class:`Competition` based on it's ID

        :param cpmpetition_id: The ID of the :class:`Competition` to retrieve
        """
        competition = CompetitionService.get_competition(competition_id=competition_id)

        serializer = CompetitionSerializer(competition)

        return Response(serializer.data)


class SubmissionViewSet(APIErrorsMixin, ViewSet):
    queryset = Submission.objects.all()

    def list(self, request: Request) -> Response:
        """List all :class:`Submission`\s"""
        filters_serializer = SubmissionFilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        submissions = SubmissionService.get_submissions(
            filters=filters_serializer.validated_data
        )

        return get_paginated_response(
            pagination_class=HeaderLimitOffsetPagination,
            serializer_class=SubmissionSerializer,
            queryset=submissions,
            request=request,
            view=self,
        )

    def retrieve(self, request: Request, submission_id: Union[str, UUID]) -> Response:
        """
        Retrieve a specific :class:`Submission` based on it's ID

        :param submission_id: The ID of the :class:`Submission` to retrieve
        """
        submission = SubmissionService.get_submission(submission_id=submission_id)

        serializer = SubmissionSerializer(submission)

        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def rankings(self, request: Request) -> Response:
        rankings = UserService.get_user_rankings()

        output_serializer = RankingSerializer(rankings, many=True)

        return Response(output_serializer.data)

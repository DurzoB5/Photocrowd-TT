import django_filters
from django.db.models import F
from django_filters.constants import EMPTY_VALUES

from .models import Competition, Submission, User


class NullsLastOrderingFilter(django_filters.OrderingFilter):
    """
    Custom ordering filter that will put null field values at the end of the order
    """

    def filter(self, qs, value):
        f_ordering = []

        if value in EMPTY_VALUES:
            return qs

        ordering = [self.get_ordering_value(param) for param in value]

        for o in ordering:
            if o.startswith('-'):
                f_ordering.append(F(o[1:]).desc(nulls_last=True))
            else:
                f_ordering.append(F(o).asc(nulls_last=True))

        return qs.order_by(*f_ordering)


class UserFilter(django_filters.FilterSet):
    """
    Filter which allows filtering :class:`User`\s by competitions they have entered
    """

    ordering = NullsLastOrderingFilter(
        fields=(('username', 'username'),),
        field_labels={
            'username': 'Username',
        },
    )

    class Meta:
        model = User
        fields = ['username']


class CompetitionFilter(django_filters.FilterSet):
    """
    Filter which allows filtering :class:`Competition`\s by name
    """

    name = django_filters.CharFilter()

    ordering = NullsLastOrderingFilter(
        fields=(('name', 'name'),),
        field_labels={'name': 'Name'},
    )

    class Meta:
        model = Competition
        fields = ['name']


class SubmissionFilter(django_filters.FilterSet):
    """
    Filter which allows filtering :class:`Submission`\s by :class:`Competition` or
    :class:`User`
    """

    user = django_filters.CharFilter()
    competition = django_filters.CharFilter()

    ordering = NullsLastOrderingFilter(
        fields=(
            ('name', 'name'),
            ('user', 'user'),
            ('competition', 'competition'),
            ('score', 'score'),
        ),
        field_labels={
            'name': 'Name',
            'user': 'User',
            'competition': 'Competition',
            'score': 'Score',
        },
    )

    class Meta:
        model = Submission
        fields = ['name', 'score', 'user', 'competition']

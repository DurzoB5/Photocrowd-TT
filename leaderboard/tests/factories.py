import factory.fuzzy
from django.contrib.auth.hashers import make_password
from factory import django
from faker import Faker

from leaderboard.models import Competition, Submission, User

FAKER = Faker()


class UserFactory(django.DjangoModelFactory):
    """Factory for generating :class:`User`\s for testing"""

    username = factory.LazyAttribute(lambda _: FAKER.user_name())
    password = factory.LazyFunction(lambda: make_password(FAKER.word()))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        user = super()._create(model_class, *args, **kwargs)
        user.set_unusable_password()

        return user

    class Meta:
        model = User


class CompetitionFactory(django.DjangoModelFactory):
    """Factory for generating :class:`Competition`/s for testing"""

    name = factory.LazyAttribute(lambda _: FAKER.user_name())

    class Meta:
        model = Competition


class SubmissionFactory(django.DjangoModelFactory):
    """Factory for generating :class:`Submission`\s for testing"""

    competition = factory.SubFactory(CompetitionFactory)
    user = factory.SubFactory(UserFactory)
    name = factory.LazyAttribute(lambda _: FAKER.word())
    score = factory.LazyAttribute(lambda _: FAKER.pyint(100, 10000))

    class Meta:
        model = Submission

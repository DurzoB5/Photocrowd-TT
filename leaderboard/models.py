import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class BaseModel(models.Model):
    """
    Base model that provides common fields across all models.

    Normally this would live inside a `core` app but as this test has such a limited
    amount of models it can live here
    """

    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    """A unique identifier for this instance of the model"""

    created_at = models.DateTimeField(auto_now_add=True)
    """The time and date this instance was created"""

    updated_at = models.DateTimeField(auto_now=True)
    """The time and date this instance was last updated"""

    class Meta:
        abstract = True


class User(BaseModel, AbstractUser):
    """Model that represents a User of the system"""

    # submissions = models.ForeignKey(
    #     'Submission',
    #     help_text='The submissions this User has made',
    # )
    """The submissions this User has made to competitions"""

    def __str__(self) -> str:
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Competition(BaseModel):
    """
    Model that represents a Competition a :class:`User` can enter
    """

    name = models.CharField(max_length=255, unique=True, blank=False, null=False)

    @property
    def submission_count(self) -> int:
        """Retrieve the amount of submissions made to this competition"""
        return self.submissions.count()

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Competition'
        verbose_name_plural = 'Competitions'


class Submission(BaseModel):
    """
    Model that represents a submission from a :class:`User` to a :class:`Competition`
    """

    competition = models.ForeignKey(
        Competition,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text='The competition this submission is being made to',
    )
    """The :class:`Competition` this Submission was made to"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='The user creating this submission',
        related_name='submissions',
    )
    """The :class:`User` that submitted this Submission"""
    name = models.CharField(max_length=255, help_text='The name of the submission')
    """The name of this Submission"""
    score = models.IntegerField(
        validators=[
            MaxValueValidator(10000, 'The maximum score allowed is 10000'),
            MinValueValidator(100, 'The minimum score allowed is 100'),
        ],
        help_text='The score this submission received',
    )
    """The score this Submission received"""

    def __str__(self) -> str:
        return f'{self.user} - {self.name}'

    class Meta:
        verbose_name = 'Submission'
        verbose_name_plural = 'Submissions'
        unique_together = ['name', 'competition']
        ordering = ['score']

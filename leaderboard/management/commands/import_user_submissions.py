import json
from typing import Any, Dict, List, Optional

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.db import transaction
from django.db.utils import IntegrityError

from leaderboard.services import CompetitionService, SubmissionService, UserService


class Command(BaseCommand):
    help = 'Import user submission data from JSON'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            'json_data',
            type=open,
            help='The path to a JSON file containing user submission data',
        )
        parser.add_argument(
            '--fail-fast',
            action='store_true',
            help='Whether to stop processing the data at the first error',
        )

    def handle(self, *args: Any, **options: Any) -> Optional[str]:
        # Load the json file into a list of dicts
        try:
            data: List[Dict[str, Any]] = json.load(options['json_data'])
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR('The provided json file is not valid'))
            raise CommandError()

        for user_data in data:
            try:
                with transaction.atomic():
                    # Generate the user's email, username using their name
                    full_name = user_data['name'].replace(' ', '.')
                    try:
                        # Try to extract a first name and last name
                        first_name, last_name = full_name.split('.')
                    except ValueError:
                        # TODO: This is a bit of a hack to deal with irregular data
                        names = full_name.split('.')
                        if len(names) == 4:
                            first_name = names[1]
                            last_name = names[2]

                    # Get or create the user in the database
                    user = UserService.get_or_create_user_by_username(
                        username=full_name.lower(),
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                        },
                    )

                    for submission in user_data.get('submissions', []):
                        with transaction.atomic():
                            # Generate competition name and submission name
                            submission_name, competition_name = submission[
                                'name'
                            ].split(' in ')

                            # Get or create the Competition in the database
                            competition = CompetitionService.get_or_create_competition(
                                name=competition_name.strip('"')
                            )

                            # Create the Submission in the database
                            try:
                                SubmissionService.create_submission(
                                    user=user,
                                    competition=competition,
                                    name=submission_name,
                                    score=submission['score'],
                                )
                            except IntegrityError:
                                self.stderr.write(
                                    self.style.WARNING(
                                        f'A submission already exists from {user} for '
                                        f'{competition} with name {submission_name}'
                                    )
                                )

            except Exception as exc:
                self.stderr.write(self.style.ERROR(f'Failed to process a user: {exc}'))
                if options['fail_fast']:
                    raise

        return 'OK'

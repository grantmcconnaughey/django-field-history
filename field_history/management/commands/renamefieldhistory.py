from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from django.core.management import BaseCommand, CommandError

from field_history.models import FieldHistory


class Command(BaseCommand):

    help = """Updates FieldHistory field_names for a given model. Run this after renaming a model field via migrations.

Example:

    python manage.py renamefieldhistory --model=myapp.User --from_field=username to_field=handle
"""

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='The model class to update in '
                 'app_label.model_name format (e.g. auth.User)')

        parser.add_argument(
            '--from_field',
            type=str,
            help='The old model field name')

        parser.add_argument(
            '--to_field',
            type=str,
            help='The new model field name')

    def handle(self, *args, **options):
        model_name = options.get('model')
        from_field = options.get('from_field')
        to_field = options.get('to_field')

        if not model_name:
            raise CommandError('--model_name is a required argument')
        if not from_field:
            raise CommandError('--from_field is a required argument')
        if not to_field:
            raise CommandError('--to_field is a required argument')

        model = apps.get_model(model_name)
        content_type = ContentType.objects.get_for_model(model)
        field_histories = FieldHistory.objects.filter(content_type=content_type, field_name=from_field)

        self.stdout.write('Updating {} FieldHistory object(s)\n'.format(field_histories.count()))

        field_histories.update(field_name=to_field)

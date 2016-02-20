import inspect

from django.apps import apps
from django.core import serializers
from django.core.management import BaseCommand

from field_history.models import FieldHistory
from field_history.tracker import FieldHistoryTracker


class Command(BaseCommand):

    help = "Adds initial FieldHistory objects"

    def handle(self, *args, **options):
        models = []
        for model in apps.get_models():
            for member in inspect.getmembers(model):
                if isinstance(member[1], FieldHistoryTracker):
                    models.append((model, member[1].fields))
                    break

        if models:
            self.stdout.write('Creating initial field history for {} models\n'.format(len(models)))

            for model_fields in models:
                model = model_fields[0]
                fields = model_fields[1]

                for obj in model._default_manager.all():
                    for field in list(fields):
                        data = serializers.serialize('json',
                                                     [obj],
                                                     fields=[field])
                        FieldHistory.objects.create(
                            object=obj,
                            field_name=field,
                            serialized_data=data,
                        )
        else:
            self.stdout.write('There are no models to create field history for.')

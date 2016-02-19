from django.db.models import Manager
from django.contrib.contenttypes.models import ContentType


class FieldHistoryManager(Manager):

    def get_for_model(self, object):
        content_type = ContentType.objects.get_for_model(object)
        return self.filter(object_id=object.pk,
                           content_type=content_type)

    def get_for_model_and_field(self, object, field):
        return self.get_for_model(object).filter(field_name=field)

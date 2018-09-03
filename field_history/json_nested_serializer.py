"""
Serialize data to/from JSON
Only one change comparing to Django build-in json serializer: obj.local_fields -> obj.fields for supporting
nested models, parent fields are included to output
"""

# Avoid shadowing the standard library json module
from __future__ import absolute_import
from __future__ import unicode_literals

import warnings

from django.core.serializers.json import Serializer as JsonSerializer
from django.utils import six

try:
    from django.utils.deprecation import RemovedInDjango19Warning
except ImportError:
    RemovedInDjango19Warning = None


class Serializer(JsonSerializer):
    """
    Convert a queryset to JSON.
    """
    def serialize(self, queryset, **options):
        """
        Serialize a queryset.
        """
        self.options = options

        self.stream = options.pop("stream", six.StringIO())
        self.selected_fields = options.pop("fields", None)
        self.use_natural_keys = options.pop("use_natural_keys", False)
        if self.use_natural_keys and RemovedInDjango19Warning is not None:
            warnings.warn("``use_natural_keys`` is deprecated; use ``use_natural_foreign_keys`` instead.",
                          RemovedInDjango19Warning)
        self.use_natural_foreign_keys = options.pop('use_natural_foreign_keys', False) or self.use_natural_keys
        self.use_natural_primary_keys = options.pop('use_natural_primary_keys', False)

        self.start_serialization()
        self.first = True
        for obj in queryset:
            self.start_object(obj)
            # Use the concrete parent class' _meta instead of the object's _meta
            # This is to avoid local_fields problems for proxy models. Refs #17717.
            concrete_model = obj._meta.concrete_model
            # only one change local_fields -> fields for supporting nested models
            for field in concrete_model._meta.fields:
                if field.serialize:
                    if field.remote_field is None:
                        if self.selected_fields is None or field.attname in self.selected_fields:
                            self.handle_field(obj, field)
                    else:
                        if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
                            self.handle_fk_field(obj, field)
            for field in concrete_model._meta.many_to_many:
                if field.serialize:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_m2m_field(obj, field)
            self.end_object(obj)
            if self.first:
                self.first = False
        self.end_serialization()
        return self.getvalue()

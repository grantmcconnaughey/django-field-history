from __future__ import unicode_literals

from copy import deepcopy

from django.core import serializers
from django.core.exceptions import FieldError
from django.db import models
from django.utils.functional import curry

from .models import FieldHistory


class FieldInstanceTracker(object):
    def __init__(self, instance, fields, field_map):
        self.instance = instance
        self.fields = fields
        self.field_map = field_map

    def get_field_value(self, field):
        return getattr(self.instance, self.field_map[field])

    def set_saved_fields(self, fields=None):
        if not self.instance.pk:
            self.saved_data = {}
        elif not fields:
            self.saved_data = self.current()
        else:
            self.saved_data.update(**self.current(fields=fields))

        # preventing mutable fields side effects
        for field, field_value in self.saved_data.items():
            self.saved_data[field] = deepcopy(field_value)

    def current(self, fields=None):
        """Returns dict of current values for all tracked fields"""
        if fields is None:
            fields = self.fields

        return dict((f, self.get_field_value(f)) for f in fields)

    def has_changed(self, field):
        """Returns ``True`` if field has changed from currently saved value"""
        return self.previous(field) != self.get_field_value(field)

    def previous(self, field):
        """Returns currently saved value of given field"""
        return self.saved_data.get(field)


class FieldHistoryTracker(object):

    tracker_class = FieldInstanceTracker

    def __init__(self, fields=None):
        if fields is None:
            fields = []
        self.fields = set(fields)

    def get_field_map(self, cls):
        """Returns dict mapping fields names to model attribute names"""
        field_map = dict((field, field) for field in self.fields)
        all_fields = dict((f.name, f.attname) for f in cls._meta.local_fields)
        field_map.update(**dict((k, v) for (k, v) in all_fields.items()
                                if k in field_map))
        return field_map

    def contribute_to_class(self, cls, name):
        setattr(cls, '_get_field_history', _get_field_history)
        for field in self.fields:
            setattr(cls, 'get_%s_history' % field,
                    curry(cls._get_field_history, field=field))
        self.name = name
        self.attname = '_%s' % name
        models.signals.class_prepared.connect(self.finalize_class, sender=cls)

    def finalize_class(self, sender, **kwargs):
        self.fields = self.fields
        self.field_map = self.get_field_map(sender)
        models.signals.post_init.connect(self.initialize_tracker)
        self.model_class = sender
        setattr(sender, self.name, self)

    def initialize_tracker(self, sender, instance, **kwargs):
        if not isinstance(instance, self.model_class):
            return  # Only init instances of given model (including children)
        tracker = self.tracker_class(instance, self.fields, self.field_map)
        setattr(instance, self.attname, tracker)
        tracker.set_saved_fields()
        self.patch_save(instance)

    def patch_save(self, instance):
        original_save = instance.save
        def save(**kwargs):
            is_new_object = instance.pk is None
            ret = original_save(**kwargs)
            tracker = getattr(instance, self.attname)

            # Create a FieldHistory for all self.fields that have changed
            for field in self.fields:
                if tracker.has_changed(field) or is_new_object:
                    data = serializers.serialize('json', [instance], fields=[field])
                    FieldHistory.objects.create(
                        object=instance,
                        field_name=field,
                        serialized_data=data,
                    )

            # Update tracker in case this model is saved again
            self.field_map = self.get_field_map(instance)
            tracker = self.tracker_class(instance, self.fields, self.field_map)
            setattr(instance, self.attname, tracker)
            tracker.set_saved_fields()

            return ret
        instance.save = save

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return FieldHistory.objects.get_for_model(instance)


def _get_field_history(self, field):
    return FieldHistory.objects.get_for_model_and_field(self, field)

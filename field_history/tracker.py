from __future__ import unicode_literals

from copy import deepcopy
import threading

from django.core import serializers
from django.conf import settings
from django.db import models
from django.utils.functional import curry

from .models import FieldHistory


def get_serializer_name():
    return getattr(settings, 'FIELD_HISTORY_SERIALIZER_NAME', 'json')


class FieldInstanceTracker(object):
    def __init__(self, instance, fields):
        self.instance = instance
        self.fields = fields

    def get_field_value(self, field):
        return getattr(self.instance, field)

    def set_saved_fields(self, fields=None):
        if not self.instance.pk:
            self.saved_data = {}
        elif not fields:
            self.saved_data = self.current()

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
    thread = threading.local()

    def __init__(self, fields):
        if not fields:
            raise ValueError("Can't track zero fields")
        self.fields = set(fields)

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
        models.signals.post_init.connect(self.initialize_tracker)
        self.model_class = sender
        setattr(sender, self.name, self)

    def initialize_tracker(self, sender, instance, **kwargs):
        if not isinstance(instance, self.model_class):
            return  # Only init instances of given model (including children)
        self._inititalize_tracker(instance)
        self.patch_save(instance)

    def _inititalize_tracker(self, instance):
        tracker = self.tracker_class(instance, self.fields)
        setattr(instance, self.attname, tracker)
        tracker.set_saved_fields()

    def patch_save(self, instance):
        original_save = instance.save

        def save(**kwargs):
            is_new_object = instance.pk is None
            ret = original_save(**kwargs)
            tracker = getattr(instance, self.attname)
            field_histories = []

            # Create a FieldHistory for all self.fields that have changed
            for field in self.fields:
                if tracker.has_changed(field) or is_new_object:
                    data = serializers.serialize(get_serializer_name(),
                                                 [instance],
                                                 fields=[field])
                    user = self.get_field_history_user(instance)
                    history = FieldHistory(
                        object=instance,
                        field_name=field,
                        serialized_data=data,
                        user=user,
                    )
                    field_histories.append(history)

            if field_histories:
                # Create all the FieldHistory objects in one batch
                FieldHistory.objects.bulk_create(field_histories)

            # Update tracker in case this model is saved again
            self._inititalize_tracker(instance)

            return ret
        instance.save = save

    def get_field_history_user(self, instance):
        try:
            return instance._field_history_user
        except AttributeError:
            try:
                if self.thread.request.user.is_authenticated:
                    return self.thread.request.user
                return None
            except AttributeError:
                return None

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return FieldHistory.objects.get_for_model(instance)


def _get_field_history(self, field):
    return FieldHistory.objects.get_for_model_and_field(self, field)

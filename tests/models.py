from django.conf import settings
from django.db import models

from field_history.tracker import FieldHistoryTracker


class Pet(models.Model):
    name = models.CharField(max_length=255)


class Person(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)

    field_history = FieldHistoryTracker(['name'])

    @property
    def _field_history_user(self):
        return self.created_by


class Owner(Person):
    pet = models.ForeignKey(Pet, blank=True, null=True)

    field_history = FieldHistoryTracker(['name', 'pet'])


class Human(models.Model):
    age = models.IntegerField(blank=True, null=True)
    is_female = models.BooleanField(default=True)
    body_temp = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    field_history = FieldHistoryTracker(['age', 'is_female',
                                         'body_temp', 'birth_date'])


class PizzaOrder(models.Model):
    STATUS_ORDERED = 'ORDERED'
    STATUS_COOKING = 'COOKING'
    STATUS_COMPLETE = 'COMPLETE'

    STATUS_CHOICES = (
        (STATUS_ORDERED, 'Ordered'),
        (STATUS_COOKING, 'Cooking'),
        (STATUS_COMPLETE, 'Complete'),
    )
    status = models.CharField(max_length=64, choices=STATUS_CHOICES)

    field_history = FieldHistoryTracker(['status'])

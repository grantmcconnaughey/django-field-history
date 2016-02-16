from django.db import models

from field_history.tracker import FieldHistoryTracker


class Pet(models.Model):
    name = models.CharField(max_length=255)


class Owner(models.Model):
    name = models.CharField(max_length=255)
    pet = models.ForeignKey(Pet, blank=True, null=True)

    history_fields = FieldHistoryTracker(['pet'])


class Person(models.Model):
    name = models.CharField(max_length=255)

    history_fields = FieldHistoryTracker(['name'])


class Human(models.Model):
    age = models.IntegerField(blank=True, null=True)
    is_female = models.BooleanField(blank=True, null=True)
    body_temp = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    history_fields = FieldHistoryTracker(['age', 'is_female',
                                          'body_temp', 'birth_date'])

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

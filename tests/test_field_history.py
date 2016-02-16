#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest.case import skip
from django.test import TestCase

from field_history.models import FieldHistory

from .models import Person, Pet, Owner


class TestFieldHistory(TestCase):

    def test_new_object_creates_field_history(self):
        # No FieldHistory objects yet
        self.assertEqual(FieldHistory.objects.count(), 0)

        person = Person.objects.create(name='Initial Name')

        # Creating an object will make one
        self.assertEqual(FieldHistory.objects.count(), 1)

        # This object has some fields on it
        history = FieldHistory.objects.get()
        self.assertEqual(history.object, person)
        self.assertEqual(history.field_name, 'name')
        self.assertEqual(history.field_value, 'Initial Name')
        self.assertIsNotNone(history.date_created)

    def test_updated_object_creates_additional_field_history(self):
        person = Person.objects.create(name='Initial Name')

        # Updating that particular field creates a new FieldHistory
        person.name = 'Updated Name'
        person.save()
        self.assertEqual(FieldHistory.objects.count(), 2)

        # You can query FieldHistory objects this way
        histories = FieldHistory.objects.get_for_model_and_field(person, 'name')

        updated_history = histories.order_by('-date_created').first()
        self.assertEqual(updated_history.object, person)
        self.assertEqual(updated_history.field_name, 'name')
        self.assertEqual(updated_history.field_value, 'Updated Name')
        self.assertIsNotNone(updated_history.date_created)

    def test_model_has_new_field_history_property(self):
        person = Person.objects.create(name='Initial Name')

        history = FieldHistory.objects.get()

        # Or using the {field_name}_history property added to your model
        self.assertItemsEqual(list(person.name_history), [history])

    def test_field_history_is_not_created_if_field_value_did_not_change(self):
        person = Person.objects.create(name='Initial Name')

        self.assertEqual(FieldHistory.objects.count(), 1)

        # The value of person did not change, so don't create a new FieldHistory
        person.name = 'Initial Name'
        person.save()

        self.assertEqual(FieldHistory.objects.count(), 1)

    # def test_field_history_works_with_foreign_key_field(self):
    #     pet = Pet.objects.create(name='Pet')
    #     owner = Owner.objects.create(name='Initial Name', pet=pet)

    #     history = FieldHistory.objects.get()

    #     self.assertEqual(history.object, owner)
    #     self.assertEqual(history.field_name, 'pet')
    #     self.assertEqual(history.field_value, pet)
    #     self.assertIsNotNone(history.date_created)

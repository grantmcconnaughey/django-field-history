#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

from django.contrib.auth import get_user_model
from django.core.management import CommandError, call_command
from django.core.urlresolvers import reverse
from django.test.utils import override_settings
from django.test import TestCase
from django.utils import six
from field_history.models import FieldHistory

from .models import Human, Owner, Person, Pet, PizzaOrder

JSON_NESTED_SETTINGS = dict(FIELD_HISTORY_SERIALIZER_NAME='json_nested',
                            SERIALIZATION_MODULES={'json_nested': 'field_history.json_nested_serializer'})


class FieldHistoryTests(TestCase):

    def test_readme(self):
        """Update this test when changes are made to the README.rst example."""
        # No FieldHistory objects yet
        assert FieldHistory.objects.count() == 0

        # Creating an object will make one
        pizza_order = PizzaOrder.objects.create(status='ORDERED')
        assert FieldHistory.objects.count() == 1

        # This object has some fields on it
        history = FieldHistory.objects.get()
        assert history.object == pizza_order
        assert history.field_name == 'status'
        assert history.field_value == 'ORDERED'
        assert history.date_created is not None

        # You can query FieldHistory using the get_{field_name}_history()
        # method added to your model
        histories = pizza_order.get_status_history()
        assert list(FieldHistory.objects.all()) == list(histories)

        # Or using the custom FieldHistory manager
        histories2 = FieldHistory.objects.get_for_model_and_field(pizza_order, 'status')
        assert list(histories) == list(histories2)

        # Updating that particular field creates a new FieldHistory
        pizza_order.status = 'COOKING'
        pizza_order.save()
        assert FieldHistory.objects.count() == 2

        updated_history = histories.latest()
        assert updated_history.object == pizza_order
        assert updated_history.field_name == 'status'
        assert updated_history.field_value == 'COOKING'
        assert updated_history.date_created is not None

    def test_str(self):
        person = Person.objects.create(name='Initial Name')

        history = FieldHistory.objects.get()

        self.assertEqual(str(history),
                         'name field history for {}'.format(str(person)))

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
        self.assertIsNone(history.user)

    def test_field_history_user_is_from_field_history_user_property(self):
        user = get_user_model().objects.create(
            username='test',
            email='test@test.com')
        person = Person.objects.create(
            name='Initial Name',
            created_by=user)

        history = person.get_name_history().get()
        self.assertEqual(history.object, person)
        self.assertEqual(history.field_name, 'name')
        self.assertEqual(history.field_value, 'Initial Name')
        self.assertIsNotNone(history.date_created)
        self.assertEqual(history.user, user)

    def test_field_history_user_is_from_request_user(self):
        user = get_user_model().objects.create(
            username='test',
            email='test@test.com')
        user.set_password('password')
        user.save()
        self.client.login(username='test', password='password')

        response = self.client.get(reverse("index"))

        # Make sure the view worked
        self.assertEqual(response.status_code, 200)
        order = PizzaOrder.objects.get()
        history = order.get_status_history().get()
        self.assertEqual(history.object, order)
        self.assertEqual(history.field_name, 'status')
        self.assertEqual(history.field_value, 'ORDERED')
        self.assertIsNotNone(history.date_created)
        self.assertEqual(history.user, user)

    def test_updated_object_creates_additional_field_history(self):
        person = Person.objects.create(name='Initial Name')

        # Updating that particular field creates a new FieldHistory
        person.name = 'Updated Name'
        person.save()
        self.assertEqual(FieldHistory.objects.count(), 2)

        histories = FieldHistory.objects.get_for_model_and_field(person, 'name')

        updated_history = histories.order_by('-date_created').first()
        self.assertEqual(updated_history.object, person)
        self.assertEqual(updated_history.field_name, 'name')
        self.assertEqual(updated_history.field_value, 'Updated Name')
        self.assertIsNotNone(updated_history.date_created)

        # One more time for good measure
        person.name = 'Updated Again'
        person.save()
        self.assertEqual(FieldHistory.objects.count(), 3)

        histories = FieldHistory.objects.get_for_model_and_field(person, 'name')

        third_history = histories.order_by('-date_created').first()
        self.assertEqual(third_history.object, person)
        self.assertEqual(third_history.field_name, 'name')
        self.assertEqual(third_history.field_value, 'Updated Again')
        self.assertIsNotNone(third_history.date_created)

    def test_model_field_history_attribute_returns_all_histories(self):
        person = Person.objects.create(name='Initial Name')

        histories = FieldHistory.objects.get_for_model_and_field(person, 'name')

        six.assertCountEqual(self, list(person.field_history), list(histories))

    def test_model_has_get_field_history_method(self):
        person = Person.objects.create(name='Initial Name')

        history = FieldHistory.objects.get()

        # Or using the {field_name}_history property added to your model
        six.assertCountEqual(self, list(person.get_name_history()), [history])

    def test_field_history_is_not_created_if_field_value_did_not_change(self):
        person = Person.objects.create(name='Initial Name')

        self.assertEqual(FieldHistory.objects.count(), 1)

        # The value of person did not change, so don't create a new FieldHistory
        person.name = 'Initial Name'
        person.save()

        self.assertEqual(FieldHistory.objects.count(), 1)

    def test_field_history_works_with_integer_field(self):
        human = Human.objects.create(age=18)

        self.assertEqual(human.get_age_history().count(), 1)
        history = human.get_age_history()[0]

        self.assertEqual(history.object, human)
        self.assertEqual(history.field_name, 'age')
        self.assertEqual(history.field_value, 18)
        self.assertIsNotNone(history.date_created)

    def test_field_history_works_with_decimal_field(self):
        human = Human.objects.create(body_temp=98.6)

        self.assertEqual(human.get_body_temp_history().count(), 1)
        history = human.get_body_temp_history()[0]

        self.assertEqual(history.object, human)
        self.assertEqual(history.field_name, 'body_temp')
        self.assertEqual(history.field_value, 98.6)
        self.assertIsNotNone(history.date_created)

    def test_field_history_works_with_boolean_field(self):
        human = Human.objects.create(is_female=True)

        self.assertEqual(human.get_is_female_history().count(), 1)
        history = human.get_is_female_history()[0]

        self.assertEqual(history.object, human)
        self.assertEqual(history.field_name, 'is_female')
        self.assertEqual(history.field_value, True)
        self.assertIsNotNone(history.date_created)

    def test_field_history_works_with_date_field(self):
        birth_date = datetime.date(1991, 11, 6)
        human = Human.objects.create(birth_date=birth_date)

        self.assertEqual(human.get_birth_date_history().count(), 1)
        history = human.get_birth_date_history()[0]

        self.assertEqual(history.object, human)
        self.assertEqual(history.field_name, 'birth_date')
        self.assertEqual(history.field_value, birth_date)
        self.assertIsNotNone(history.date_created)

    def test_field_history_tracks_multiple_fields_changed_at_same_time(self):
        human = Human.objects.create(
            birth_date=datetime.date(1991, 11, 6),
            is_female=True,
            body_temp=98.6,
            age=18,
        )

        self.assertEqual(FieldHistory.objects.count(), 4)
        self.assertEqual(FieldHistory.objects.get_for_model_and_field(human, 'birth_date').count(), 1)
        self.assertEqual(FieldHistory.objects.get_for_model_and_field(human, 'is_female').count(), 1)
        self.assertEqual(FieldHistory.objects.get_for_model_and_field(human, 'body_temp').count(), 1)
        self.assertEqual(FieldHistory.objects.get_for_model_and_field(human, 'age').count(), 1)

        human.birth_date = datetime.date(1992, 11, 6)
        human.is_female = False
        human.body_temp = 100.0
        human.age = 21
        human.save()

        self.assertEqual(FieldHistory.objects.count(), 8)
        self.assertEqual(FieldHistory.objects.get_for_model_and_field(human, 'birth_date').count(), 2)
        self.assertEqual(FieldHistory.objects.get_for_model_and_field(human, 'is_female').count(), 2)
        self.assertEqual(FieldHistory.objects.get_for_model_and_field(human, 'body_temp').count(), 2)
        self.assertEqual(FieldHistory.objects.get_for_model_and_field(human, 'age').count(), 2)

    def test_field_history_works_with_foreign_key_field(self):
        pet = Pet.objects.create(name='Garfield')
        owner = Owner.objects.create(name='Jon', pet=pet)

        self.assertEqual(owner.get_pet_history().count(), 1)
        history = owner.get_pet_history()[0]

        self.assertEqual(history.object, owner)
        self.assertEqual(history.field_name, 'pet')
        self.assertEqual(history.field_value, pet)
        self.assertIsNotNone(history.date_created)

    def test_field_history_works_with_field_set_to_None(self):
        owner = Owner.objects.create(pet=None)

        history = owner.get_pet_history()[0]

        self.assertEqual(history.object, owner)
        self.assertEqual(history.field_name, 'pet')
        self.assertEqual(history.field_value, None)

    @override_settings(**JSON_NESTED_SETTINGS)
    def test_field_history_works_with_field_of_parent_model(self):
        owner = Owner.objects.create(name='Jon')

        history = owner.get_name_history()[0]

        self.assertEqual(history.object, owner)
        self.assertEqual(history.field_name, 'name')
        self.assertEqual(history.field_value, 'Jon')


class ManagementCommandsTests(TestCase):

    def test_createinitialfieldhistory_command_no_objects(self):
        call_command('createinitialfieldhistory')

        self.assertEqual(FieldHistory.objects.count(), 0)

    def test_createinitialfieldhistory_command_one_object(self):
        person = Person.objects.create(name='Initial Name')
        FieldHistory.objects.all().delete()

        call_command('createinitialfieldhistory')

        self.assertEqual(FieldHistory.objects.count(), 1)

        history = FieldHistory.objects.get()
        self.assertEqual(history.object, person)
        self.assertEqual(history.field_name, 'name')
        self.assertEqual(history.field_value, 'Initial Name')
        self.assertIsNotNone(history.date_created)

    def test_createinitialfieldhistory_command_only_tracks_new_object(self):
        Person.objects.create(name='Initial Name')
        FieldHistory.objects.all().delete()
        call_command('createinitialfieldhistory')

        self.assertEqual(FieldHistory.objects.count(), 1)

        PizzaOrder.objects.create(status=PizzaOrder.STATUS_ORDERED)
        call_command('createinitialfieldhistory')

        self.assertEqual(FieldHistory.objects.count(), 2)

    def test_renamefieldhistory(self):
        Person.objects.create(name='Initial Name')

        self.assertEqual(FieldHistory.objects.filter(field_name='name').count(), 1)

        call_command(
            'renamefieldhistory',
            model='tests.Person',
            from_field='name',
            to_field='name2')

        self.assertEqual(FieldHistory.objects.filter(field_name='name').count(), 0)
        self.assertEqual(FieldHistory.objects.filter(field_name='name2').count(), 1)

    def test_renamefieldhistory_model_arg_is_required(self):
        Person.objects.create(name='Initial Name')

        self.assertEqual(FieldHistory.objects.filter(field_name='name').count(), 1)

        with self.assertRaises(CommandError):
            call_command('renamefieldhistory', from_field='name', to_field='name2')

    def test_renamefieldhistory_from_field_arg_is_required(self):
        Person.objects.create(name='Initial Name')

        self.assertEqual(FieldHistory.objects.filter(field_name='name').count(), 1)

        with self.assertRaises(CommandError):
            call_command('renamefieldhistory', model='tests.Person', to_field='name2')

    def test_renamefieldhistory_to_field_arg_is_required(self):
        Person.objects.create(name='Initial Name')

        self.assertEqual(FieldHistory.objects.filter(field_name='name').count(), 1)

        with self.assertRaises(CommandError):
            call_command('renamefieldhistory', model='tests.Person', from_field='name')

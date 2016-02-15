=============================
django-field-history
=============================

.. image:: https://badge.fury.io/py/django-field-history.png
    :target: https://badge.fury.io/py/django-field-history

.. image:: https://travis-ci.org/grantmcconnaughey/django-field-history.png?branch=master
    :target: https://travis-ci.org/grantmcconnaughey/django-field-history

A Django app to track changes to a model field.

Documentation
-------------

The full documentation is at https://django-field-history.readthedocs.org.

Quickstart
----------

Install django-field-history::

    pip install django-field-history

Then use it in a project::

    import field_history

    class Person(models.Model):
        name = models.CharField(max_length=255)

        history_fields = field_history.FieldHistoryTracker(['name'])

    # No FieldHistory objects yet
    self.assertEqual(FieldHistory.objects.count(), 0)

    person = Person.objects.create(name='Initial Name')

    # Creating an object will make one
    self.assertEqual(FieldHistory.objects.count(), 1)

    # This object has some fields on it
    history = FieldHistory.objects.get()
    self.assertEqual(history.model_object, person)
    self.assertEqual(history.field_name, 'name')
    self.assertEqual(history.field_value, 'Initial Name')
    self.assertIsNotNone(history.history_date)

    # Updating that particular field creates a new FieldHistory
    person.name = 'Updated Name'
    person.save()
    self.assertEqual(FieldHistory.objects.count(), 2)

    # You can query FieldHistory objects this way
    histories = FieldHistory.objects.get_for_model_and_field(person, 'name')
    self.assertQuerysetEqual(person.history_fields.all(), histories)

    # Or using the {field_name}_history property added to your model
    self.assertQuerysetEqual(person.name_history, histories)

    updated_history = histories.order_by('-history_date').first()
    self.assertEqual(history.model_object, person)
    self.assertEqual(history.field_name, 'name')
    self.assertEqual(history.field_value, 'Updated Name')
    self.assertIsNotNone(history.history_date)

Features
--------

* TODO

Running Tests
--------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements-test.txt
    (myenv) $ python runtests.py

Credits
---------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-pypackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage

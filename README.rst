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

Be sure to put it in INSTALLED_APPS.

.. code-block:: python

    INSTALLED_APPS = [
        # other apps...
        'field_history',
    ]

Then add it to your models.

.. code-block:: python

    from field_history.tracker import FieldHistoryTracker

    class Person(models.Model):
        name = models.CharField(max_length=255)

        field_history = FieldHistoryTracker(['name'])

Now each time you change the name field information about that change will be stored in the database.

.. code-block:: python

    from field_history.models import FieldHistory

    # No FieldHistory objects yet
    self.assertEqual(FieldHistory.objects.count(), 0)

    # Creating an object will make one
    person = Person.objects.create(name='Initial Name')
    assert FieldHistory.objects.count() == 1

    # This object has some fields on it
    history = FieldHistory.objects.get()
    assert history.object == person
    assert history.field_name == 'name'
    assert history.field_value == 'Initial Name'
    assert history.date_created is not None

    # Updating that particular field creates a new FieldHistory
    person.name = 'Updated Name'
    person.save()
    assert FieldHistory.objects.count() == 2

    # You can query FieldHistory objects this way
    histories = FieldHistory.objects.get_for_model_and_field(person, 'name')
    assert list(person.field_history) == list(histories)

    # Or using the get_{field_name}_history() method added to your model
    self.assertItemsEqual([person.get_name_history()], [histories])

    updated_history = histories.order_by('-date_created').first()
    assert history.object == person
    assert history.field_name == 'name'
    assert history.field_value == 'Updated Name'
    assert history.date_created is not None

Features
--------

* Keeps a history of all changes to a particular field.
* Stores the field's name, value, date and time of change, and the user that changed the field.
* Works with all model field types (except ``ManyToManyField``).

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

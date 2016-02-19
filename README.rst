====================
django-field-history
====================

.. image:: https://badge.fury.io/py/django-field-history.svg
    :target: https://badge.fury.io/py/django-field-history

.. image:: https://readthedocs.org/projects/django-field-history/badge/?version=latest
    :target: http://django-field-history.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/grantmcconnaughey/django-field-history.svg?branch=master
    :target: https://travis-ci.org/grantmcconnaughey/django-field-history

.. image:: https://coveralls.io/repos/github/grantmcconnaughey/django-field-history/badge.svg?branch=master
    :target: https://coveralls.io/github/grantmcconnaughey/django-field-history?branch=master


A Django app to track changes to a model field.

Documentation
-------------

The full documentation is at https://django-field-history.readthedocs.org.

Features
--------

* Keeps a history of all changes to a particular field.
* Stores the field's name, value, date and time of change, and the user that changed it.
* Works with all model field types (except ``ManyToManyField``).

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

    class PizzaOrder(models.Model):
        STATUS_CHOICES = (
            ('ORDERED', 'Ordered'),
            ('COOKING', 'Cooking'),
            ('COMPLETE', 'Complete'),
        )
        status = models.CharField(max_length=64, choices=STATUS_CHOICES)

        field_history = FieldHistoryTracker(['status'])

Now each time you change the order's status field information about that change will be stored in the database.

.. code-block:: python

    from field_history.models import FieldHistory

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

    # Updating that particular field creates a new FieldHistory
    pizza_order.status = 'COOKING'
    pizza_order.save()
    assert FieldHistory.objects.count() == 2

    # You can query FieldHistory objects this way
    histories = FieldHistory.objects.get_for_model_and_field(pizza_order, 'status')
    assert list(pizza_order.field_history) == list(histories)

    # Or using the get_{field_name}_history() method added to your model
    self.assertItemsEqual([pizza_order.get_status_history()], [histories])

    updated_history = histories.order_by('-date_created').first()
    assert history.object == pizza_order
    assert history.field_name == 'status'
    assert history.field_value == 'COOKING'
    assert history.date_created is not None

Management Commands
-------------------

django-field-history comes with one management command called ``createinitialfieldhistory``. This command will inspect all of the models in your application and create ``FieldHistory`` objects for the models that have a ``FieldHistoryTracker``. Run this the first time you install django-field-history.

::

    python manage.py createinitialfieldhistory


Storing Which User Changed the Field
------------------------------------

To store the user that changed a field add a ``_field_history_user`` property to your model. This property should return the user you would like stored on ``FieldHistory`` when your field is updated.

.. code-block:: python

    class Pizza(models.Model):
        name = models.CharField(max_length=255)
        updated_by = models.ForeignKey('auth.User')

        field_history = FieldHistoryTracker(['name'])

        @property
        def _field_history_user(self):
            return self.updated_by

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements-test.txt
    (myenv) $ python runtests.py

TO-DO
-----

* Add a management command to handle fields that are renamed. Command should update all ``FieldHistory`` entries for models of a particular type.

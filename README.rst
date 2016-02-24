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

A Django app to track changes to a model field. For Python 2.7/3.2+ and Django 1.8+.

Documentation
-------------

The full documentation is at https://django-field-history.readthedocs.org.

Features
--------

* Keeps a history of all changes to a particular model's field.
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

Management Commands
-------------------

django-field-history comes with a few management commands.

createinitialfieldhistory
+++++++++++++++++++++++++

This command will inspect all of the models in your application and create ``FieldHistory`` objects for the models that have a ``FieldHistoryTracker``. Run this the first time you install django-field-history.

::

    python manage.py createinitialfieldhistory

renamefieldhistory
++++++++++++++++++

Use this command after changing a model field name of a field you track with ``FieldHistoryTracker``::

    python manage.py renamefieldhistory --model=app_label.model_name --from_field=old_field_name --to_field=new_field_name

For instance, if you have this model::

    class Person(models.Model):
        username = models.CharField(max_length=255)

        field_history = FieldHistoryTracker(['username'])

And you change the ``username`` field name to ``handle``::

    class Person(models.Model):
        handle = models.CharField(max_length=255)

        field_history = FieldHistoryTracker(['handle'])

You will need to also update the ``field_name`` value in all ``FieldHistory`` objects that point to this model::

    python manage.py renamefieldhistory --model=myapp.Person --from_field=username --to_field=handle

Storing Which User Changed the Field
------------------------------------

There are two ways to store the user that changed your model field. The simplest way is to use **the logged in user** that made the request. To do this, add the ``FieldHistoryMiddleware`` class to your ``MIDDLEWARE_CLASSES`` setting::

    MIDDLEWARE_CLASSES = (
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "field_history.middleware.FieldHistoryMiddleware",
    )

Alternatively, you can add a ``_field_history_user`` property to the model that has fields you are tracking. This property should return the user you would like stored on ``FieldHistory`` when your field is updated.

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

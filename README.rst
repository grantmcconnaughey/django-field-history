====================
django-field-history
====================

.. image:: https://badge.fury.io/py/django-field-history.svg
    :target: https://badge.fury.io/py/django-field-history

.. image:: https://readthedocs.org/projects/django-field-history/badge/?version=latest
    :target: https://django-field-history.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://travis-ci.org/grantmcconnaughey/django-field-history.svg?branch=master
    :target: https://travis-ci.org/grantmcconnaughey/django-field-history

.. image:: https://coveralls.io/repos/github/grantmcconnaughey/django-field-history/badge.svg?branch=master
    :target: https://coveralls.io/github/grantmcconnaughey/django-field-history?branch=master

A Django app to track changes to a model field. For Python 2.7/3.4+ and Django 1.11/2.0+.

Other similar apps are `django-reversion <https://github.com/etianen/django-reversion>`_ and `django-simple-history <https://github.com/treyhunner/django-simple-history>`_, which track *all* model fields.

+------------------------+----------------------+------------------+----------------------------------+
| Project                | django-field-history | django-reversion | django-simple-history            |
+------------------------+----------------------+------------------+----------------------------------+
| Admin Integration      | N/A                  | Yes              | Yes                              |
+------------------------+----------------------+------------------+----------------------------------+
| All/Some fields        | Some                 | Some             | All                              |
+------------------------+----------------------+------------------+----------------------------------+
| Object History         | No                   | Yes              | Yes                              |
+------------------------+----------------------+------------------+----------------------------------+
| Model History          | N/A                  | No               | Yes                              |
+------------------------+----------------------+------------------+----------------------------------+
| Multi-object Revisions | N/A                  | Yes              | No                               |
+------------------------+----------------------+------------------+----------------------------------+
| Extra Model Manager    | Yes                  | No               | Yes                              |
+------------------------+----------------------+------------------+----------------------------------+
| Model Registry         | No                   | Yes              | No                               |
+------------------------+----------------------+------------------+----------------------------------+
| Django View Helpers    | No                   | Yes              | No                               |
+------------------------+----------------------+------------------+----------------------------------+
| Manager Helper Methods | N/A                  | Yes              | Yes (``as_of``, ``most_recent``) |
+------------------------+----------------------+------------------+----------------------------------+
| MySQL Support          | Extra config         | Complete         | Complete                         |
+------------------------+----------------------+------------------+----------------------------------+

Documentation
-------------

The full documentation is at https://django-field-history.readthedocs.io.

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

For instance, if you have this model:

.. code-block:: python

    class Person(models.Model):
        username = models.CharField(max_length=255)

        field_history = FieldHistoryTracker(['username'])

And you change the ``username`` field name to ``handle``:

.. code-block:: python

    class Person(models.Model):
        handle = models.CharField(max_length=255)

        field_history = FieldHistoryTracker(['handle'])

You will need to also update the ``field_name`` value in all ``FieldHistory`` objects that point to this model::

    python manage.py renamefieldhistory --model=myapp.Person --from_field=username --to_field=handle

Storing Which User Changed the Field
------------------------------------

There are two ways to store the user that changed your model field. The simplest way is to use **the logged in user** that made the request. To do this, add the ``FieldHistoryMiddleware`` class to your ``MIDDLEWARE`` setting.

.. code-block:: python

    MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'field_history.middleware.FieldHistoryMiddleware',
    ]

Alternatively, you can add a ``_field_history_user`` property to the model that has fields you are tracking. This property should return the user you would like stored on ``FieldHistory`` when your field is updated.

.. code-block:: python

    class Pizza(models.Model):
        name = models.CharField(max_length=255)
        updated_by = models.ForeignKey('auth.User')

        field_history = FieldHistoryTracker(['name'])

        @property
        def _field_history_user(self):
            return self.updated_by

Working with MySQL
------------------

If you're using MySQL, the default configuration will throw an exception when you run migrations. (By default, ``FieldHistory.object_id`` is implemented as a ``TextField`` for flexibility, but indexed columns in MySQL InnoDB tables may be a maximum of 767 bytes.) To fix this, you can set ``FIELD_HISTORY_OBJECT_ID_TYPE`` in settings.py to override the default field type with one that meets MySQL's constraints. ``FIELD_HISTORY_OBJECT_ID_TYPE`` may be set to either:

1. the Django model field class you wish to use, or
2. a tuple ``(field_class, kwargs)``, where ``field_class`` is a Django model field class and ``kwargs`` is a dict of arguments to pass to the field class constructor.

To approximate the default behavior for Postgres when using MySQL, configure ``object_id`` to use a ``CharField`` by adding the following to settings.py:

.. code-block:: python

    from django.db import models
    FIELD_HISTORY_OBJECT_ID_TYPE = (models.CharField, {'max_length': 100})

``FIELD_HISTORY_OBJECT_ID_TYPE`` also allows you to use a field type that's more efficient for your use case, even if you're using Postgres (or a similarly unconstrained database). For example, if you always let Django auto-create an ``id`` field (implemented internally as an ``AutoField``), setting ``FIELD_HISTORY_OBJECT_ID_TYPE`` to ``IntegerField`` will result in efficiency gains (both in time and space). This would look like:

.. code-block:: python

    from django.db import models
    FIELD_HISTORY_OBJECT_ID_TYPE = models.IntegerField

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install -r requirements-test.txt
    (myenv) $ python runtests.py

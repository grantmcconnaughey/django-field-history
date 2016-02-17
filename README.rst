=============================
django-field-history
=============================

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
        INVOICE_NUMBER_TYPE = (
            ('ORDER', 'Ordered'),
            ('COOK', 'Cooking'),
            ('COMPL', 'Complete'),
        )
        status = models.CharField(max_length=10, choices=PIZZA_CHOICES)

        field_history = FieldHistoryTracker(['status'])

Now each time you change the order's status field information about that change will be stored in the database.

.. code-block:: python

    from field_history.models import FieldHistory

    # No FieldHistory objects yet
    assert FieldHistory.objects.count() == 0

    # Creating an object will make one
    pizza_order = PizzaOrder.objects.create(status='ORDER')
    assert FieldHistory.objects.count() == 1

    # This object has some fields on it
    history = FieldHistory.objects.get()
    assert history.object == pizza_order
    assert history.field_name == 'status'
    assert history.field_value == 'ORDER'
    assert history.date_created is not None

    # Updating that particular field creates a new FieldHistory
    pizza_order.status = 'COOK'
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
    assert history.field_value == 'COOK'
    assert history.date_created is not None

Features
--------

* Keeps a history of all changes to a particular field.
* Stores the field's name, value, date and time of change.
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

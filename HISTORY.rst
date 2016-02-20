.. :changelog:

History
-------

0.3.0 (Not released)
++++++++++++++++++

* ``FieldHistory`` objects are now created using ``bulk_create``, which means only one query will be executed, even when changing multiple fields at the same time.
* Added a way to store which user updated a field.
* Added ``get_latest_by`` to ``FieldHistory`` Meta options so ``.latest()`` and ``.earliest()`` can be used.
* Added ``createinitialfieldhistory`` management command.
* Added ``renamefieldhistory`` management command.

0.2.0 (2016-02-17)
++++++++++++++++++

* First release on PyPI.

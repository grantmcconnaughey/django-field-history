.. :changelog:

History
-------

0.7.0 (September 3, 2018)
++++++++++++++++++++
* Added support for Django 2.0 and 2.1
* Added support for Python 3.7
* Dropped support for Django 1.7 through 1.10
* Dropped support for Python 3.2 and 3.3
* Fixed generic primary key bug with `createinitialfieldhistory` command (#20)

0.6.0 (December 22, 2016)
+++++++++++++++++++++++++
* Added Django 1.10 compatibility.
* Added MySQL compatibility.
* Fixed issue that would duplicate tracked fields.

0.5.0 (April 16, 2016)
++++++++++++++++++++++
* Added the ability to track field history of parent models.
* Added Django 1.7 compatibility.

0.4.0 (February 24, 2016)
+++++++++++++++++++++++++
* Added a way to automatically store the logged in user on ``FieldHistory.user``.

0.3.0 (February 20, 2016)
+++++++++++++++++++++++++

* ``FieldHistory`` objects are now created using ``bulk_create``, which means only one query will be executed, even when changing multiple fields at the same time.
* Added a way to store which user updated a field.
* Added ``get_latest_by`` to ``FieldHistory`` Meta options so ``.latest()`` and ``.earliest()`` can be used.
* Added ``createinitialfieldhistory`` management command.
* Added ``renamefieldhistory`` management command.

0.2.0 (February 17, 2016)
+++++++++++++++++++++++++

* First release on PyPI.

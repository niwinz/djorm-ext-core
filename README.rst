django-orm-extensions core module
=================================

This module contaisn all basic and generic improvements needed by all submodules.


PostgreSQL server side cursors
------------------------------

For most cases, the normal cursor and django psycopg2 are more than enough. But there are cases where we have to do queries to tables with large amounts of data, and we need an efficient way to query this data.

On first step, put ``djorm_core.postgresql`` in your ``INSTALLED_APPS``.

This is a simple example of usage:

.. code-block:: python

    from djorm_core.postgresql import server_side_cursors

    with server_side_cursors(qs, itersize=100):
        for item in Model.objects.all():
            print item.value

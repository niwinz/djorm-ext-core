# -*- coding: utf-8 -*-

import threading
import uuid
import sys

from django.conf import settings
import django

try:
    import psycopg2
except ImportError:
    print("psycopg2 import error, djorm_core.postgres modulue "
          "is only compatible with postgresql_psycopg2 backend")
    sys.exit(-1)



_local_data = threading.local()


class server_side_cursors(object):
    def __init__(self, itersize=None, withhold=False, once=False):
        self.itersize = itersize
        self.withhold = withhold
        self.m_once = once

    def __enter__(self):
        self.old_itersize = getattr(_local_data, 'itersize', None)
        self.old_cursors = getattr(_local_data, 'server_side_cursors', False)
        self.old_withhold = getattr(_local_data, 'withhold', False)
        self.old_once = getattr(_local_data, 'once', False)
        _local_data.itersize = self.itersize
        _local_data.server_side_cursors = True
        _local_data.withhold = self.withhold
        _local_data.once = self.m_once
        return self

    def __exit__(self, type, value, traceback):
        _local_data.itersize = self.old_itersize
        _local_data.server_side_cursors = self.old_cursors
        _local_data.withhold = self.old_withhold
        _local_data.once = self.old_once

    def _set_enable(self, en):
        _local_data.server_side_cursors = en
    def _get_enable(self):
        return _local_data.server_side_cursors

    def _set_once(self, once):
        _local_data.once = once
        if once:
            _local_data.server_side_cursors = True
    def _get_once(self):
        return _local_data.once

    enabled = property(_get_enable, _set_enable)
    once = property(_get_once, _set_once)



def patch_cursor_wrapper_django_lt_1_6():
    from django.db.backends.postgresql_psycopg2 import base

    if hasattr(base, "_CursorWrapper"):
        return

    base._CursorWrapper = base.CursorWrapper

    class CursorWrapper(base._CursorWrapper):
        def __init__(self, *args, **kwargs):
            super(CursorWrapper, self).__init__(*args, **kwargs)

            if not getattr(_local_data, 'server_side_cursors', False):
                return

            connection = self.cursor.connection
            cursor = self.cursor

            name = uuid.uuid4().hex
            self.cursor = connection.cursor(name="cur{0}".format(name),
                    withhold=getattr(_local_data, 'withhold', False))
            self.cursor.tzinfo_factory = cursor.tzinfo_factory

            if getattr(_local_data, 'itersize', None):
                self.cursor.itersize = _local_data.itersize

            if getattr(_local_data, 'once', False):
                _local_data.server_side_cursors = False
                _local_data.once = False


    base.CursorWrapper = CursorWrapper


def patch_cursor_wrapper_django_gte_1_6():
    from django.db.backends.postgresql_psycopg2 import base
    if hasattr(base, "_ssc_patched"):
        return

    base._ssc_patched = True

    old_create_cursor = base.DatabaseWrapper.create_cursor
    def new_create_cursor(self):
        if getattr(_local_data, 'server_side_cursors', False):
            name = uuid.uuid4().hex
            cursor = self.connection.cursor(name="cur{0}".format(name))
            cursor.tzinfo_factory = base.utc_tzinfo_factory if settings.USE_TZ else None
            return cursor

        return old_create_cursor(self)

    base.DatabaseWrapper.create_cursor = new_create_cursor


if django.VERSION[:2] < (1, 6):
    patch_cursor_wrapper_django_lt_1_6()
else:
    patch_cursor_wrapper_django_gte_1_6()

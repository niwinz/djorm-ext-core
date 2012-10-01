# -*- coding: utf-8 -*-

from django.db.models import signals
from django.db.backends import signals as backend_signals
from django.conf import settings
from django.utils.importlib import import_module
from .utils import Singleton


class ConnectionCreateHandler(object):
    """
    Generic connection handlers manager.
    Executes attrached funcitions on connection is created.
    With facilty of attaching single execution methods.
    """

    __metaclass__ = Singleton

    generic_handlers = {}
    unique_handlers = {}

    def __call__(self, sender, connection, **kwargs):
        handlers = set()
        if None in self.unique_handlers:
            handlers.update(self.unique_handlers[None])
            del self.unique_handlers[None]

        if connection.vendor in self.unique_handlers:
            handlers.update(self.unique_handlers[connection.vendor])
            del self.unique_handlers[connection.vendor]

        if connection.vendor in self.generic_handlers:
            handlers.update(self.generic_handlers[connection.vendor])

        [x(connection) for x in handlers]

    def attach_handler(self, func, vendor=None, unique=False):
        if unique:
            if vendor not in self.unique_handlers:
                self.unique_handlers[vendor] = [func]
            else:
                self.unique_handlers[vendor].append(func)

        else:
            if vendor not in self.generic_handlers:
                self.generic_handlers[vendor] = [func]
            else:
                self.generic_handlers[vendor].append(func)


connection_handler = ConnectionCreateHandler()
backend_signals.connection_created.connect(connection_handler)

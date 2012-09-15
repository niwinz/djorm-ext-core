# -*- coding: utf-8 -*-

import unicodedata

def remove_diacritic(input):
    '''
    Accept a unicode string, and return a normal string (bytes in Python 3)
    without any diacritical marks.
    '''
    return unicodedata.normalize('NFKD', input).encode('ASCII', 'ignore')


class Singleton(type):
    """ Singleton metaclass. """

    def __init__(cls, name, bases, dct):
        cls.__instance = None
        type.__init__(cls, name, bases, dct)

    def __call__(cls, *args, **kw):
        if cls.__instance is None:
            cls.__instance = type.__call__(cls, *args,**kw)
        return cls.__instance

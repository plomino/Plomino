# -*- coding: utf-8 -*-
#
# File: dictionaryproperty.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#
_marker = object()

class DictionaryProperty(object):
    """Computed attributes based on schema fields stored in a dictionary
    (based on zope/schema/fieldproperty.py) 
    """

    def __init__(self, field, dictionary, name=None):
        if name is None:
            name = field.__name__

        self.__field = field
        self.__name = name
        self.__dictionary = dictionary

    def __get__(self, inst, klass):
        if inst is None:
            return self

        value = getattr(inst, self.__dictionary).get(self.__name, _marker)
        if value is _marker:
            field = self.__field.bind(inst)
            value = getattr(field, 'default', _marker)
            if value is _marker:
                raise AttributeError(self.__name)

        return value

    def __set__(self, inst, value):
        field = self.__field.bind(inst)
        field.validate(value)
        if field.readonly and inst.__dict__.has_key(self.__name):
            raise ValueError(self.__name, 'field is readonly')
        getattr(inst, self.__dictionary)[self.__name] = value

    def __getattr__(self, name):
        return getattr(self.__field, name)

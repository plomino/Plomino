# -*- coding: utf-8 -*-
#
# File: text.py
#
# Copyright (c) 2013 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields
from zope.schema import Choice
from zope.schema.vocabulary import SimpleVocabulary

from dictionaryproperty import DictionaryProperty

from base import IBaseField, BaseField, BaseForm

class IBooleanField(IBaseField):
    """
    Boolean field schema
    """
    widget = Choice(
            vocabulary=SimpleVocabulary.fromItems(
                [("Single checkbox", "CHECKBOX"),]),
            title=u'Widget',
            description=u'Field rendering',
            default="CHECKBOX",
            required=True)

class BooleanField(BaseField):
    """
    """
    implements(IBooleanField)

    def processInput(self, strValue):
        """
        """
        if strValue == "1":
            return True
        else:
            return False

for f in getFields(IBooleanField).values():
    setattr(BooleanField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IBooleanField)

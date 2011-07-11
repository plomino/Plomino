# -*- coding: utf-8 -*-
#
# File: text.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields
from zope.schema import TextLine, Text, Choice
from zope.schema.vocabulary import SimpleVocabulary

from dictionaryproperty import DictionaryProperty

from base import IBaseField, BaseField, BaseForm

class ITextField(IBaseField):
    """
    Text field schema
    """
    widget = Choice(vocabulary=SimpleVocabulary.fromItems([("Text", "TEXT"), ("Long text", "TEXTAREA")]),
                    title=u'Widget',
                    description=u'Field rendering',
                    default="TEXT",
                    required=True)
    size = TextLine(title=u'Size',
                      description=u'Length or rows (depending on the widget)',
                      required=False)

class TextField(BaseField):
    """
    """
    implements(ITextField)

for f in getFields(ITextField).values():
    setattr(TextField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(ITextField)

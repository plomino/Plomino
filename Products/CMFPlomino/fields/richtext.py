# -*- coding: utf-8 -*-
#
# File: richtext.py
#
# Copyright (c) 2009 by ['Eric BREHAULT']
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

class IRichtextField(IBaseField):
    """
    Text field schema
    """
    height = TextLine(title=u'Height',
                      description=u'Height in pixels',
                      required=False)

class RichtextField(BaseField):
    """
    """
    implements(IRichtextField)

for f in getFields(IRichtextField).values():
    setattr(RichtextField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IRichtextField)


# -*- coding: utf-8 -*-
#
# File: googlechart.py
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
from zope.schema import TextLine

from dictionaryproperty import DictionaryProperty

from base import IBaseField, BaseField, BaseForm

class IGooglechartField(IBaseField):
    """
    Google chart field schema
    """
    editrows = TextLine(title=u'Rows',
                      description=u'Size of the editable text area',
                      default=u"6",
                      required=False)

class GooglechartField(BaseField):
    """
    """
    implements(IGooglechartField)

    def validate(self, submittedValue):
        """
        """
        errors=[]
        # no validation needed (we do not want to parse the GoogleChart param)
        return errors

    def processInput(self, submittedValue):
        """
        """
        lines = submittedValue.replace('\r', '').split('\n')
        params = {}
        for l in lines:
            if "=" in l:
                (key, value) = l.split('=')
            else:
                key = l
                value = ''
            params[key] = value
        return params


for f in getFields(IGooglechartField).values():
    setattr(GooglechartField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IGooglechartField)


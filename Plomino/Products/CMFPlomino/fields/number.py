# -*- coding: utf-8 -*-
#
# File: number.py
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

from Products.Five.formlib.formbase import EditForm
from Products.CMFPlomino.PlominoUtils import PlominoTranslate

from base import IBaseField, BaseField

class INumberField(IBaseField):
    """
    Number field schema
    """
    type = Choice(vocabulary=SimpleVocabulary.fromItems([("Integer", "INTEGER"), ("Float", "FLOAT")]),
                    title=u'Type',
                    description=u'Number type',
                    default="INTEGER",
                    required=True)
    size = TextLine(title=u'Size',
                      description=u'Length',
                      required=False)

class NumberField(BaseField):
    """
    """
    implements(INumberField)

    def validate(self, submittedValue):
        """
        """
        errors=[]
        fieldname = self.context.id
        if self.type=="INTEGER":
            try:
                v = long(submittedValue)
            except:
                errors.append(fieldname+PlominoTranslate(" must be an integer (submitted value was: ", self.context)+submittedValue+")")
        if self.type=="FLOAT":
            try:
                v = float(submittedValue)
            except:
                errors.append(fieldname+PlominoTranslate(" must be a float (submitted value was: ", self.context)+submittedValue+")")
        
        return errors
    
    def processInput(self, submittedValue):
        """
        """
        if self.type=="INTEGER":
            return long(submittedValue)
        elif self.type=="FLOAT":
            return float(submittedValue)
        else:
            return submittedValue
    
for f in getFields(INumberField).values():
    setattr(NumberField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(EditForm):
    """
    """
    form_fields = form.Fields(INumberField)
    
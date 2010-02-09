# -*- coding: utf-8 -*-
#
# File: selection.py
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
from zope.schema import TextLine, Text, List, Choice
from zope.schema.vocabulary import SimpleVocabulary
from dictionaryproperty import DictionaryProperty

from Products.Five.formlib.formbase import EditForm

from base import IBaseField, BaseField

class ISelectionField(IBaseField):
    """
    Selection field schema
    """
    widget = Choice(vocabulary=SimpleVocabulary.fromItems([("Selection list", "SELECT"),
                                                           ("Multi-selection list", "MULTISELECT"),
                                                           ("Checkboxes", "CHECKBOX"),
                                                           ("Radio buttons", "RADIO")
                                                           ]),
                    title=u'Widget',
                    description=u'Field rendering',
                    default="SELECT",
                    required=True)
    selectionlist = List(title=u'Selection list',
                      description=u'List of values to select, one per line. Use | to separate label and value',
                      required=False,
                      default=[],
                      value_type=TextLine(title=u'Entry'))
    selectionlistformula = Text(title=u'Selection list formula',
                      description=u'Formula to compute the selection list elements',
                      required=False)
    separator = TextLine(title=u'Separator',
                      description=u'Only apply if multi-valued',
                      required=False)

class SelectionField(BaseField):
    """
    """
    implements(ISelectionField)
    
    def getSelectionList(self, doc):
        """return a list, format: label|value, use label as value if no label
        """

        #if formula available, use formula, else use manual entries
        f = self.selectionlistformula
        if f=='' or f is None:
            s = self.selectionlist
            if s=='':
                return []
        else:
            #if no doc provided (if OpenForm action), we use the PlominoForm
            if doc is None:
                obj = self.context
            else:
                obj = doc
            s = self.context.runFormulaScript("field_"+self.context.getParentNode().id+"_"+self.context.id+"_SelectionListFormula", obj, lambda: f)
            if s is None:
                s = []

        # if values not specified, use label as value
        proper = []
        for v in s:
            l = v.split('|')
            if len(l)==2:
                proper.append(v)
            else:
                proper.append(v+'|'+v)
        return proper
    
for f in getFields(ISelectionField).values():
    setattr(SelectionField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(EditForm):
    """
    """
    form_fields = form.Fields(ISelectionField)
    
# -*- coding: utf-8 -*-
#
# File: doclink.py
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
from zope.schema import TextLine, Text, List, Choice
from zope.schema.vocabulary import SimpleVocabulary
from dictionaryproperty import DictionaryProperty

from Products.Five.formlib.formbase import EditForm

from base import IBaseField, BaseField

class IDoclinkField(IBaseField):
    """
    Selection field schema
    """
    widget = Choice(vocabulary=SimpleVocabulary.fromItems([("Selection list", "SELECT"),
                                                           ("Multi-selection list", "MULTISELECT"),
                                                           ("Embedded view", "VIEW")
                                                           ]),
                    title=u'Widget',
                    description=u'Field rendering',
                    default="SELECT",
                    required=True)
    
    sourceview = TextLine(title=u'Source view',
                    description=u'View containing the linkable documents',
                    required=False)
    
    labelcolumn = TextLine(title=u'Label column',
                    description=u'View column used as label',
                    required=False)
    
    documentslistformula = Text(title=u'Documents list formula',
                      description=u'Formula to compute the linkable documents list (must return a list of label|path_to_doc)',
                      required=False)
    separator = TextLine(title=u'Separator',
                      description=u'Only apply if multi-valued',
                      required=False)
    
class DoclinkField(BaseField):
    """
    """
    implements(IDoclinkField)
    
    def getDocumentsList(self, doc):
        """return a list, format: label|path_to_doc, use value is used as label if no label
        """

        #if formula available, use formula, else use view entries
        f = self.documentslistformula
        if f is None or len(f)==0:
            if self.sourceview is not None:
                v = self.context.getParentDatabase().getView(self.sourceview)
            else:
                v = None
            if v is None:
                return []
            else:
                return [str(getattr(d, 'PlominoViewColumn_'+self.sourceview+'_'+self.labelcolumn))+"|"+d.getPath() for d in v.getAllDocuments()]
        else:
            #if no doc provided (if OpenForm action), we use the PlominoForm
            if doc is None:
                obj = self.context.getParentNode()
            else:
                obj = doc
            s = self.context.runFormulaScript("field_"+self.context.getParentNode().id+"_"+self.context.id+"_DocumentListFormula", obj, lambda: f)
            if s is None:
                s = []

        # if values not specified, use label as value
        proper = []
        for v in s:
            v = str(v)
            l = v.split('|')
            if len(l)==2:
                proper.append(v)
            else:
                proper.append(v+'|'+v)
        return proper
    
for f in getFields(IDoclinkField).values():
    setattr(DoclinkField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(EditForm):
    """
    """
    form_fields = form.Fields(IDoclinkField)
    
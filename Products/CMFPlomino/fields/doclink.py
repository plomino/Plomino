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

import simplejson as json

class IDoclinkField(IBaseField):
    """
    Selection field schema
    """
    widget = Choice(vocabulary=SimpleVocabulary.fromItems([("Selection list", "SELECT"),
                                                           ("Multi-selection list", "MULTISELECT"),
                                                           ("Embedded view", "VIEW"),
                                                           ("Dynamic table", "DYNAMICTABLE"),
                                                           ("Dynamic picklist", "PICKLIST")
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
    dynamictableparam = Text(
        title=u"Dynamic Table Parameters",
        description=u"Change these options to customize the dynamic table.",
        default=u"""
'bPaginate': true,
'bLengthChange': true,
'bFilter': true,
'bSort': true,
'bInfo': true,
'bAutoWidth': false"""
    )
    
class DoclinkField(BaseField):
    """
    """
    implements(IDoclinkField)
    
    def getSelectionList(self, doc):
        """return the documents list, format: label|path_to_doc, use value is used as label if no label
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
                result = []
                for d in v.getAllDocuments():
                    val = getattr(d, v.getIndexKey(self.labelcolumn), '')
                    if not val:
                        val = ''
                    result.append(val + "|" + d.getPath())
                return result
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
            l = v.split('|')
            if len(l)==2:
                proper.append(v)
            else:
                proper.append(v+'|'+v)
        return proper

    def processInput(self, submittedValue):
        """
        """
        if "|" in submittedValue:
            return submittedValue.split("|")
        else:
            return submittedValue
    
    def tojson(self, selectionlist):
        """Return a JSON table storing documents to be displayed
        """
        if self.sourceview is not None:
            sourceview = self.context.getParentDatabase().getView(self.sourceview)
            alldocs = sourceview.getAllDocuments()
            columns = sourceview.getColumns()
            column_ids = [col.id for col in columns]
            
            datatable = []
            for doc in alldocs:
                row = [doc.getPath()]
                for col in column_ids:
                    cell = getattr(doc, sourceview.getIndexKey(col))
                    if not cell:
                        cell = ''
                    row.append(cell)
                datatable.append(row)
        else:
            datatable = [v.split('|')[::-1] for v in selectionlist]
            
        return json.dumps(datatable)
    
    def getJQueryColumns(self):
        """Returns a JSON representation of columns headers, designed for JQuery DataTables
        """
        if self.sourceview is not None:
            sourceview = self.context.getParentDatabase().getView(self.sourceview)
            columns = sourceview.getColumns()
            column_labels = [col.Title() for col in columns]
        else:
            column_labels = [""]
            
        column_dicts = [{"sTitle": col} for col in column_labels]
        column_dicts.insert(0, {"bVisible": False, "bSearchable": False})
        
        return json.dumps(column_dicts)
    
    def getColumnLabelIndex(self):
        """Return the column index used to display the document label
        """
        if self.sourceview:
            return [col.id for col in self.context.getParentDatabase().getView(self.sourceview).getColumns()].index(self.labelcolumn);
        else:
            return 0
    
for f in getFields(IDoclinkField).values():
    setattr(DoclinkField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(EditForm):
    """
    """
    form_fields = form.Fields(IDoclinkField)
    

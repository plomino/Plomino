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
                                                           ("Dynamic table", "DYNAMICTABLE")
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
'bPaginate': false,
'bLengthChange': false,
'bFilter': true,
'bSort': true,
'bInfo': true,
'bAutoWidth': false"""
    )
    
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
                return [getattr(d, v.getIndexKey(self.labelcolumn), '')+"|"+d.getPath() for d in v.getAllDocuments()]
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

    def processInput(self, submittedValue):
        """
        """
        if "|" in submittedValue:
            return submittedValue.split("|")
        else:
            return submittedValue
    
    def jscode(self, selectionlist, selected):
        """ return Google visualization js code
        """
        field_id = self.context.id
        if self.sourceview is not None:
            sourceview = self.context.getParentDatabase().getView(self.sourceview)
            alldocs = sourceview.getAllDocuments()
            columns = sourceview.getColumns()
            column_ids = [col.id for col in columns]
            column_labels = [col.Title() for col in columns]
            paths = [doc.getPath() for doc in alldocs]
            datatable = [[doc.getPath()] + [getattr(doc, sourceview.getIndexKey(col)) for col in column_ids] for doc in alldocs]
        else:
            column_labels = [""]
            paths = [v.split('|')[1] for v in selectionlist]
            datatable = [v.split('|')[::-1] for v in selectionlist]
            
        column_dicts = [{"sTitle": col} for col in column_labels]
        column_dicts.insert(0, {"bVisible": False})
        
        js = """
var oDynamicTable;
$(document).ready(function() {
    o_%(id)s_DynamicTable = $('#%(id)s_table').dataTable( {
        'aaData': %(data)s,
        'aoColumns': %(cols)s,
        'aaSorting': [],
        'fnRowCallback': function (nRow, aData, iDisplayIndex) {
            var iId = aData[0];
            if ('%(selected)s'.indexOf(iId) != -1)
                $(nRow).addClass('row_selected');
            return nRow;
        },
        %(params)s
    });
 
    $('#%(id)s_table tbody tr').live('click', function () {
        var aData = o_%(id)s_DynamicTable.fnGetData( this );
        var iId = aData[0];
        
        var docInput = document.getElementById('%(id)s');
        
        var selectedDocs = docInput.value;
        selectedDocs = selectedDocs.indexOf(iId) == -1 ? selectedDocs + iId + '|' : selectedDocs.replace(iId + '|', '');
        docInput.value = selectedDocs;
        
        $(this).toggleClass('row_selected');
    } );
 });
""" % {"id": field_id,
       "data": json.dumps(datatable),
       "cols": json.dumps(column_dicts),
       "params": self.dynamictableparam,
       "selected": '|'.join(selected)}

        return js
    
for f in getFields(IDoclinkField).values():
    setattr(DoclinkField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(EditForm):
    """
    """
    form_fields = form.Fields(IDoclinkField)
    

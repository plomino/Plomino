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
                                                           ("Embedded view", "VIEW"),
                                                           ("Google Visualization table", "GTABLE")
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
    googletableparam = TextLine(title=u'Google table parameters',
                    description=u'See Google visualization documentation',
                    default=u"showRowNumber: false",
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
            datatable = [[getattr(doc, sourceview.getIndexKey(col)) for col in column_ids] for doc in alldocs]
        else:
            column_labels = [""]
            paths = [v.split('|')[1] for v in selectionlist]
            datatable = [[v.split('|')[0]] for v in selectionlist]
            
        loadjs = self.context.REQUEST.get('googlejsapi', False)
        if not loadjs:
            self.context.REQUEST.set('googlejsapi', True)
            
        js = """
google.load('visualization', '1', {packages:['table']});
google.setOnLoadCallback(drawTable);
function drawTable() {\n"""
        
        js = js + "var %s_mapping = new Array(%s);\n" % (field_id,  ", ".join(["'"+p+"'" for p in paths]) )
        if selected is None or len(selected)==0:
            js_selected = ""
        else:
            js_selected = ", ".join(['{row:%d, column: null}' % paths.index(s) for s in selected if s in paths])
            
        js = js + "var %s_selected = new Array(%s);\n" % (field_id, js_selected )
        
        js = js + "var %s_data = new google.visualization.DataTable();\n" % (field_id)
        
        for col in column_labels:
            #TODO: accept other types than string
            js = js + "  %s_data.addColumn('string', '%s');\n" % (field_id, col)

        js_table = ", ".join(["[" + ", ".join(["'"+str(cell)+"'" for cell in row]) + "]" for row in datatable])
        js = js + "  %s_data.addRows([%s]);\n" % (field_id, js_table)
#        i = 0
#        for row in datatable:
#            j = 0
#            for cell in row:
#                js = js + field_id +"_data.setCell(" + str(i) + ", " + str(j) + ", '" + cell + "');\n"
#                j = j + 1
#            i = i + 1
        js = js + """
 var %s_table = new google.visualization.Table(document.getElementById('%s_div'));
 %s_table.draw(%s_data, {%s});\n""" % (field_id, field_id, field_id, field_id, self.googletableparam)

        js = js + "%s_table.setSelection(%s_selected);\n" % (field_id, field_id)
        js = js + """
                google.visualization.events.addListener(%s_table, 'select',
                  function(event) {
                    selection = %s_table.getSelection();
                    v = ""
                    for(var i = 0; i < selection.length; i++) {
                        v = v + %s_mapping[selection[i].row] + "|";
                    }
                    field = document.getElementById('%s');
                    field.value = v;
                  });
        """ % (field_id, field_id, field_id, field_id)
        js = js + "}"
        return js
    
for f in getFields(IDoclinkField).values():
    setattr(DoclinkField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(EditForm):
    """
    """
    form_fields = form.Fields(IDoclinkField)
    

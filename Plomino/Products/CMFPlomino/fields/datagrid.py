# -*- coding: utf-8 -*-
#
# File: datagrid.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from zope.formlib import form
from zope.interface import implements
from zope import component
from zope.pagetemplate.pagetemplatefile import PageTemplateFile

from zope.schema import getFields
from zope.schema import Text, TextLine
from zope.schema.vocabulary import SimpleVocabulary

import simplejson as json

from Products.Five.formlib.formbase import EditForm

from Products.CMFPlomino.PlominoUtils import csv_to_array

from Products.CMFPlomino.interfaces import IPlominoField
from Products.CMFPlomino.fields.dictionaryproperty import DictionaryProperty

from Products.CMFPlomino.fields.base import IBaseField, BaseField

from Products.CMFPlomino.browser.javascript.dataTables.utils import get_language_path

class IDatagridField(IBaseField):
    """
    Text field schema
    """
    associated_form = TextLine(title=u'Associated form',
                description=u'Form to use to create/edit rows',
                required=False)
    
    field_mapping = TextLine(title=u'Columns/fields mapping',
                description=u'Field ids from the associated form, ordered as the columns, separated by commas',
                required=False)
        
    jssettings = Text(title=u'Javascript settings',
                      description=u'jQuery datatable parameters',
                      default=u"""
"aoColumns": [
    { "sTitle": "Column 1" },
    { "sTitle": "Column 2", "sClass": "center" }
],
"bPaginate": false,
"bLengthChange": false,
"bFilter": false,
"bSort": false,
"bInfo": false,
"bAutoWidth": false
""",
                      required=False)

class DatagridField(BaseField):
    """
    """
    implements(IDatagridField)
    
    plomino_field_parameters = {'interface': IDatagridField,
                                'label': "Datagrid",
                                'index_type': "ZCTextIndex"}
    
    read_template = PageTemplateFile('datagrid_read.pt')
    edit_template = PageTemplateFile('datagrid_edit.pt')
    
    def getParameters(self):
        """
        """
        return self.jssettings
    
    def processInput(self, submittedValue):
        """
        """
        try:
            return json.loads(submittedValue)
        except:
            return []
    
    def tojson(self, value):
        """
        """
        if value is None or value == "":
            value = []
        if isinstance(value, basestring):
            return value
        return json.dumps(value)
    
    def getLang(self):
        """
        """
        return get_language_path(self.context)
    
    def getFieldValue(self, form, doc, editmode, creation, request):
        """
        """
        fieldValue = BaseField.getFieldValue(self, form, doc, editmode, creation, request)
        
        mode = self.context.getFieldMode()
                        
        if not(mode=="EDITABLE" and editmode):
             # fieldValue is a array of arrays, where we must replace raw values with
             # rendered values
             try:
                 child_form_id = self.associated_form
                 if child_form_id is not None:
                     db = self.context.getParentDatabase()
                     child_form = db.getForm(child_form_id)
                     fields = self.field_mapping.split(',')
                     fields_obj = [child_form.getFormField(f) for f in fields]
                     # avoid bad field ids
                     fields_obj = [f for f in fields_obj if f is not None]
                     fields_to_render = [f.id for f in fields_obj if f.getFieldType() not in ["DATETIME", "NUMBER", "TEXT", "RICHTEXT"]]
                     
                     rendered_values = []
                     for row in fieldValue:
                         row_values = {}
                         j = 0
                         for v in row:
                             if fields[j] in fields_to_render:
                                 row_values[fields[j]] = v
                             j = j + 1
                         if len(row_values) > 0:
                             row_values['Plomino_Parent_Document'] = doc.id 
                             tmp = TemporaryDocument(db, child_form, row_values)
                             tmp.setItem('Form', child_form_id)
                         rendered_row = []
                         i = 0
                         for f in fields:
                             if f in fields_to_render:
                                 rendered_row.append(tmp.getRenderedItem(f))
                             else:
                                 rendered_row.append(row[i])
                             i = i + 1
                         rendered_values.append(rendered_row)
                     fieldValue = rendered_values
             except:
                 pass
        
        mapping = self.field_mapping
        if mapping:
            col_number = len(mapping.split(','))
            resized = []
            empty = ['']
            for row in fieldValue:
                if len(row) < col_number:
                    resized.append(row + empty * (col_number - len(row)))
                elif len(row) > col_number:
                    resized.append(row[:col_number])
                else:
                    resized.append(row)
            fieldValue = resized
        return fieldValue

component.provideUtility(DatagridField, IPlominoField, 'DATAGRID')

for f in getFields(IDatagridField).values():
    setattr(DatagridField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(EditForm):
    """
    """
    form_fields = form.Fields(IDatagridField)
    

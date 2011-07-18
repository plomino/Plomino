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

from DateTime import DateTime

from zope.formlib import form
from zope.interface import implements
from zope import component
from zope.pagetemplate.pagetemplatefile import PageTemplateFile

from zope.schema import getFields
from zope.schema import Text, TextLine
from zope.schema.vocabulary import SimpleVocabulary

import simplejson as json

from Products.CMFPlomino.PlominoUtils import csv_to_array, DateToString, PlominoTranslate
from Products.CMFPlomino.PlominoDocument import TemporaryDocument

from Products.CMFPlomino.interfaces import IPlominoField
from Products.CMFPlomino.fields.dictionaryproperty import DictionaryProperty

from Products.CMFPlomino.fields.base import IBaseField, BaseField, BaseForm

from Products.CMFPlomino.browser.javascript.dataTables.utils import get_language_path

import logging
logger = logging.getLogger('Plomino')

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

    def tojson(self, value, rendered=False):
        """
        """
        if value is None or value == "":
            value = []
        if isinstance(value, basestring):
            return value
        if isinstance(value, DateTime):
            value = DateToString(value)
        if isinstance(value, dict):
            if rendered:
                value = value['rendered']
            else:
                value = value['rawdata']
        return json.dumps(value)

    def getLang(self):
        """
        """
        return get_language_path(self.context)

    def getActionLabel(self, action_id):
        """
        """
        db = self.context.getParentDatabase()
        if action_id=="add":
            label = PlominoTranslate("datagrid_add_button_label", db)
            child_form_id = self.associated_form
            if child_form_id is not None:
                child_form = db.getForm(child_form_id)
                if child_form:
                    label += " "+child_form.Title()
            return label
        if action_id=="delete":
            return PlominoTranslate("datagrid_delete_button_label", db)
        if action_id=="edit":
            return PlominoTranslate("datagrid_edit_button_label", db)
        return ""

    def getFieldValue(self, form, doc, editmode, creation, request):
        """
        """
        fieldValue = BaseField.getFieldValue(self, form, doc, editmode, creation, request)
        if not fieldValue:
            return fieldValue

        # if doc is not a PlominoDocument, no processing needed
        if not doc or doc.isNewDocument():
            return fieldValue
        
        rawValue = fieldValue
        mode = self.context.getFieldMode()
        
        mapped_fields = []
        if self.field_mapping:
            mapped_fields = [
                f.strip() for f in self.field_mapping.split(',')]
        # item names is set by `PlominoForm.createDocument`
        item_names = doc.getItem(self.context.id+'_itemnames')

        if mapped_fields:
            if not item_names:
                item_names = mapped_fields

            # fieldValue is a array, where we must replace raw values with
            # rendered values
            child_form_id = self.associated_form
            if child_form_id is not None:
                db = self.context.getParentDatabase()
                child_form = db.getForm(child_form_id)
                # zip is procrustean: we get the longest of mapped_fields or
                # fieldValue
                mapped = []
                for row in fieldValue:
                    if len(row) < len(item_names):
                        row = (row + ['']*(len(item_names)-len(row)))
                    row = dict(zip(item_names, row))
                    mapped.append(row)
                fieldValue = mapped
                fields = {}
                for f in mapped_fields + item_names:
                    fields[f] = None
                fields = fields.keys()
                field_objs = [child_form.getFormField(f) for f in fields]
                # avoid bad field ids
                field_objs = [f for f in field_objs if f is not None]
                #DBG fields_to_render = [f.id for f in field_objs if f.getFieldType() not in ["DATETIME", "NUMBER", "TEXT", "RICHTEXT"]]
                #DBG fields_to_render = [f.id for f in field_objs if f.getFieldType() not in ["DOCLINK", ]]
                fields_to_render = [f.id for f in field_objs if f.getFieldMode() in ["DISPLAY", ] or f.getFieldType() not in ["TEXT", "RICHTEXT"]]

                if fields_to_render:
                    rendered_values = []
                    for row in fieldValue:
                        row['Form'] = child_form_id
                        row['Plomino_Parent_Document'] = doc.id 
                        tmp = TemporaryDocument(db, child_form, row, real_doc=doc)
                        tmp = tmp.__of__(db)
                        for f in fields:
                            if f in fields_to_render:
                                row[f] = tmp.getRenderedItem(f)
                        rendered_values.append(row)
                    fieldValue = rendered_values

            if mapped_fields and child_form_id:
                mapped = []
                for row in fieldValue:
                    mapped.append([row[c] for c in mapped_fields])
                fieldValue = mapped

        return {'rawdata': rawValue, 'rendered': fieldValue}

component.provideUtility(DatagridField, IPlominoField, 'DATAGRID')

for f in getFields(IDatagridField).values():
    setattr(DatagridField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IDatagridField)


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
# Standard
import logging
logger = logging.getLogger('Plomino')

# Third-party
from jsonutil import jsonutil as json

# Zope
from DateTime import DateTime
from zope.formlib import form
from zope.interface import implements
from zope import component
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.schema import getFields
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema import Text, TextLine, Choice

# Plomino
from Products.CMFPlomino.browser import PlominoMessageFactory as _
from Products.CMFPlomino.fields.base import IBaseField, BaseField, BaseForm
from Products.CMFPlomino.fields.dictionaryproperty import DictionaryProperty
from Products.CMFPlomino.interfaces import IPlominoField
from Products.CMFPlomino.PlominoDocument import TemporaryDocument
from Products.CMFPlomino.PlominoUtils import DateToString, PlominoTranslate


class IDatagridField(IBaseField):
    """ Text field schema
    """
    widget = Choice(
            vocabulary=SimpleVocabulary.fromItems(
                [("Always dynamic", "REGULAR"),
                    ("Static in read mode", "READ_STATIC"),
                    ]),
            title=u'Widget',
            description=u'Field rendering',
            default="REGULAR",
            required=True)

    associated_form = Choice(
            vocabulary='Products.CMFPlomino.fields.vocabularies.get_forms',
            title=u'Associated form',
            description=u'Form to use to create/edit rows',
            required=False)

    associated_form_rendering = Choice(
            vocabulary=SimpleVocabulary.fromItems(
                [("Modal", "MODAL"),
                    ("Inline editing", "INLINE"),
                    ]),
            title=u'Associate form rendering',
            description=u'Associate form rendering',
            default="MODAL",
            required=True)

    field_mapping = TextLine(
            title=u'Columns/fields mapping',
            description=u'Field ids from the associated form, '
                    'ordered as the columns, separated by commas',
            required=False)

    jssettings = Text(
            title=u'Javascript settings',
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
"bAutoWidth": false,
"plominoDialogOptions": {
        "width": 400,
        "height": 300
    }
""",
            required=False)

class DatagridField(BaseField):
    """
    """
    implements(IDatagridField)

    plomino_field_parameters = {
            'interface': IDatagridField,
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

    def rows(self, value, rendered=False):
        """
        """
        if value in [None, '']:
            value = []
        if isinstance(value, basestring):
            return value
        elif isinstance(value, DateTime):
            db = self.context.getParentDatabase()
            value = DateToString(value, db=db)
            # TODO does anything require that format here?
            # value = DateToString(value, '%Y-%m-%d')
        elif isinstance(value, dict):
            if rendered:
                value = value['rendered']
            else:
                value = value['rawdata']
        return value

    def tojson(self, value, rendered=False):
        """
        """
        rows = self.rows(value, rendered)

        return json.dumps(rows)

    def request_items_aoData(self, request):
        
        """ Return a string representing REQUEST.items as aoData.push calls.
        """
        aoData_templ = "aoData.push(%s); "
        aoDatas = []
        for k,v in request.form.items():
            j = json.dumps({'name': k, 'value': v})
            aoDatas.append(aoData_templ % j)
        return '\n'.join(aoDatas)

    def getActionLabel(self, action_id):
        """
        """
        db = self.context.getParentDatabase()
        if action_id == "add":
            label = PlominoTranslate(_("datagrid_add_button_label", default="Add"), db)
            child_form_id = self.associated_form
            if child_form_id:
                child_form = db.getForm(child_form_id)
                if child_form:
                    label += " "+child_form.Title()
            return label
        elif action_id == "delete":
            return PlominoTranslate(_("datagrid_delete_button_label", default="Delete"), db)
        elif action_id == "edit":
            return PlominoTranslate(_("datagrid_edit_button_label", default="Edit"), db)
        return ""

    def getColumnLabels(self):
        """
        """
        if not self.field_mapping:
            return []
        
        mapped_fields = [ f.strip() for f in self.field_mapping.split(',')]
        
        child_form_id = self.associated_form
        if not child_form_id:
            return mapped_fields

        db = self.context.getParentDatabase()

        # get child form
        child_form = db.getForm(child_form_id)
        if not child_form:
            return mapped_fields

        # return title for each mapped field if this one exists in the child form
        return [f.Title() for f in [child_form.getFormField(f) for f in mapped_fields] if f]

    def getRenderedFields(self, editmode=True, creation=False, request={}):
        """ Return an array of rows rendered using the associated form fields
        """
        if not self.field_mapping:
            return []

        db = self.context.getParentDatabase()

        mapped_fields = [ f.strip() for f in self.field_mapping.split(',')]

        #get associated form id
        child_form_id = self.associated_form
        if not child_form_id:
            return mapped_fields
 
        # get associated form object
        child_form = db.getForm(child_form_id)
        if not child_form:
            return mapped_fields

        target = TemporaryDocument(
                db,
                child_form,
                request, 
                validation_mode=False).__of__(db) 

        # return rendered field for each mapped field if this one exists in the child form
	child_form_fields = [f.getFieldRender(child_form, target, editmode=editmode, creation=creation, request=request) for f in [child_form.getFormField(f) for f in mapped_fields] if f]
	return json.dumps(child_form_fields)

    def getAssociateForm(self):
        child_form_id = self.associated_form;
        if child_form_id:
            db = self.context.getParentDatabase()
            return db.getForm(child_form_id)   

    def getFieldValue(self, form, doc=None, editmode_obsolete=False,
            creation=False, request=None):
        """
        """
        fieldValue = BaseField.getFieldValue(
                self, form, doc, editmode_obsolete, creation, request)
        if not fieldValue:
            return fieldValue

        # if doc is not a PlominoDocument, no processing needed
        if not doc or doc.isNewDocument():
            return fieldValue

        rawValue = fieldValue

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
            if child_form_id:
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
                fields_to_render = [f.id for f in field_objs 
                        if f.getFieldMode() in ["DISPLAY", ] or
                        f.getFieldType() not in ["TEXT", "RICHTEXT"]]

                if fields_to_render:
                    rendered_values = []
                    for row in fieldValue:
                        row['Form'] = child_form_id
                        row['Plomino_Parent_Document'] = doc.id 
                        # We want a new TemporaryDocument for every row
                        tmp = TemporaryDocument(
                                db, child_form, row, real_doc=doc)
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

class EditFieldsAsJson(object):
    """
    """
    def __call__(self):

        if hasattr(self.context, 'getParentDatabase') and self.context.FieldType == u'DATAGRID':
            self.request.RESPONSE.setHeader(
                        'content-type',
                        'application/json; charset=utf-8')

            self.field = self.context.getSettings()
            self.request.set("Plomino_Parent_Form",self.context.getForm().id)
            self.request.set("Plomino_Parent_Field",self.context.id)
            #DBG logger.info("%s --- %s --- %s"%(self.request["Plomino_Parent_Form"],self.request["Plomino_Parent_Field"],self.request["Plomino_datagrid_rowdata"]))
            return self.field.getRenderedFields(request=self.request)

        return ""

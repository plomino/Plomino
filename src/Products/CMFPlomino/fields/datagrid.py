# -*- coding: utf-8 -*-

from jsonutil import jsonutil as json
from DateTime import DateTime
from plone.autoform.interfaces import IFormFieldProvider, ORDER_KEY
from plone.supermodel import directives, model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from .. import _
from base import BaseField
from ..document import TemporaryDocument
from ..utils import DateToString, PlominoTranslate


@provider(IFormFieldProvider)
class IDatagridField(model.Schema):
    """ Datagrid field schema
    """

    widget = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Always dynamic", "REGULAR"),
            ("Static in read mode", "READ_STATIC"),
        ]),
        title=u'Widget',
        description=u'Field rendering',
        default="REGULAR",
        required=True)

    associated_form = schema.Choice(
        vocabulary='Products.CMFPlomino.fields.vocabularies.get_forms',
        title=u'Associated form',
        description=u'Form to use to create/edit rows',
        required=False)

    field_mapping = schema.TextLine(
        title=u'Fields/columns mapping',
        description=u'Field ids from the associated form, separated by commas.',
        required=False)

# bug in plone.autoform means order_after doesn't moves correctly
IDatagridField.setTaggedValue(ORDER_KEY,
                               [('widget', 'after', 'field_type'),
                                ('associated_form', 'after', ".widget"),
                                ('field_mapping', 'after', ".associated_form"),
                               ]
)


@implementer(IDatagridField)
class DatagridField(BaseField):
    """
    """

    read_template = PageTemplateFile('datagrid_read.pt')
    edit_template = PageTemplateFile('datagrid_edit.pt')

    def processInput(self, submittedValue):
        """
        """
        value = json.loads(submittedValue)
        mapping = self.getFieldMapping().split(',')
        if len(value) and isinstance(value[0], dict):
            # Need to convert to tuple for storage
            value = [[line[k] for k in mapping if k in line] for line in value]
        return value


    def tojson(self, value, rendered=False):
        """
        """
        if not value:
            return "[]"
        if type(value) is dict:
            if rendered and 'rendered' in value:
                value = value['rendered']
            if not(rendered) and 'rawdata' in value:
                value = value['rawdata']
        return json.dumps(value)

    def getColumnLabels(self):
        """
        """
        if not self.getFieldMapping():
            return []

        mapped_fields = [f.strip() for f in self.getFieldMapping().split(',')]

        child_form_id = self.context.associated_form
        if not child_form_id:
            return mapped_fields

        db = self.context.getParentDatabase()

        # get child form
        child_form = db.getForm(child_form_id)
        if not child_form:
            return mapped_fields

        # return title for each mapped field if this one exists in the
        # child form
        return [f.Title() for f in [child_form.getFormField(f)
            for f in mapped_fields] if f]

    def getRenderedFields(self, editmode=True, creation=False, request={}):
        """ Return an array of rows rendered using the associated form fields
        """
        if not self.getFieldMapping():
            return []

        db = self.context.getParentDatabase()

        mapped_fields = [f.strip() for f in self.getFieldMapping().split(',')]

        # get associated form id
        child_form_id = self.context.associated_form
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

        # return rendered field for each mapped field if this one exists in the
        # child form
        child_form_fields = [f.getFieldRender(
            child_form,
            target,
            editmode=editmode,
            creation=creation,
            request=request
        ) for f in [child_form.getFormField(f) for f in mapped_fields] if f]
        return json.dumps(child_form_fields)

    def getAssociatedForm(self):
        child_form_id = self.context.associated_form
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
        if not doc:
            return fieldValue

        rawValue = fieldValue or []

        mapped_fields = []
        if self.getFieldMapping():
            mapped_fields = [
                f.strip() for f in self.getFieldMapping().split(',')]
        # item names is set by `PlominoForm.createDocument`
        item_names = doc.getItem(self.context.id + '_itemnames')

        if mapped_fields:
            if not item_names:
                item_names = mapped_fields

            # fieldValue is a array, where we must replace raw values with
            # rendered values
            child_form_id = self.context.associated_form
            if child_form_id:
                db = self.context.getParentDatabase()
                child_form = db.getForm(child_form_id)
                # zip is procrustean: we get the longest of mapped_fields or
                # fieldValue
                mapped = []
                for row in fieldValue:
                    if len(row) < len(item_names):
                        row = (row + [''] * (len(item_names) - len(row)))
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
                fields_to_render = [f.id for f in field_objs
                        if f.field_mode in ["DISPLAY", ] or
                        f.field_type not in ["TEXT", "RICHTEXT"]]

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

                # raw value should be dict now
                rawValue = [dict(zip(item_names, row)) for row in rawValue]

        return {'rawdata': rawValue, 'rendered': fieldValue}


    def getFieldMapping(self):
        """ work out default mapping, if one is not set.
         """
        #TODO: problem with this is that if they subform changes then the data
        # that's saved will be read wrong.
        # Alternative is to set it by default, but then if you add more fields
        # you need to go update it manually.
        # TODO: shows all fields, even ones not on the subforms layout
        if self.context.field_mapping:
            return self.context.field_mapping
        child_form_id = self.context.associated_form
        if not child_form_id:
            return ""

        db = self.context.getParentDatabase()
        child_form = db.getForm(child_form_id)
        return ','.join([f.id for f in child_form.getFormFields(includesubforms=True)])

class EditFieldsAsJson(object):
    """
    """
    def __call__(self):
        context = self.context
        if (hasattr(context, 'getParentDatabase')
        and context.field_type == u'DATAGRID'):
            self.request.RESPONSE.setHeader(
                'content-type',
                'application/json; charset=utf-8')

            self.field = context.getSettings()
            self.request.set("Plomino_Parent_Form", context.getForm().id)
            self.request.set("Plomino_Parent_Field", context.id)
            return self.field.getRenderedFields(request=self.request)

        return ""

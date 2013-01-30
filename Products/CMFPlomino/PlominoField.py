# -*- coding: utf-8 -*-
#
# File: PlominoField.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT and Caroline ANSALDI <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'

# Standard
import logging
logger = logging.getLogger('Plomino')

# Zope
from AccessControl import ClassSecurityInfo
from persistent.dict import PersistentDict
from zope.annotation.interfaces import IAnnotations
from zope import component
from zope.interface import implements
from ZPublisher.HTTPRequest import FileUpload

# CMF / Archetypes / Plone
from Products.Archetypes.atapi import *
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

# Plomino
from Products.CMFPlomino.config import *
from Products.CMFPlomino.fields.datetime import IDatetimeField
from Products.CMFPlomino.fields.doclink import IDoclinkField
from Products.CMFPlomino.fields.name import INameField
from Products.CMFPlomino.fields.selection import ISelectionField
from Products.CMFPlomino.fields.text import ITextField
from Products.CMFPlomino import fields
from Products.CMFPlomino import plomino_profiler
import interfaces

schema = Schema((
    StringField(
        name='id',
        widget=StringField._properties['widget'](
            label="Id",
            description="The field id",
            label_msgid='CMFPlomino_label_field_id',
            description_msgid='CMFPlomino_help_field_id',
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='FieldType',
        default="TEXT",
        widget=SelectionWidget(
            label="Field type",
            description="The kind of this field",
            label_msgid='CMFPlomino_label_FieldType',
            description_msgid='CMFPlomino_help_FieldType',
            i18n_domain='CMFPlomino',
        ),
        vocabulary='type_vocabulary',
    ),
    StringField(
        name='FieldMode',
        default="EDITABLE",
        widget=SelectionWidget(
            label="Field mode",
            description="How content will be generated",
            label_msgid='CMFPlomino_label_FieldMode',
            description_msgid='CMFPlomino_help_FieldMode',
            i18n_domain='CMFPlomino',
        ),
        vocabulary=FIELD_MODES,
    ),
    TextField(
        name='Formula',
        widget=TextAreaWidget(
            label="Formula",
            description="How to calculate field content",
            label_msgid='CMFPlomino_label_FieldFormula',
            description_msgid='CMFPlomino_help_FieldFormula',
            i18n_domain='CMFPlomino',
            rows=10,
        ),
    ),
    StringField(
        name='FieldReadTemplate',
        widget=StringField._properties['widget'](
            label="Field read template",
            description="Custom rendering template in read mode",
            label_msgid='CMFPlomino_label_FieldReadTemplate',
            description_msgid='CMFPlomino_help_FieldReadTemplate',
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='FieldEditTemplate',
        widget=StringField._properties['widget'](
            label="Field edit template",
            description="Custom rendering template in edit mode",
            label_msgid='CMFPlomino_label_FieldEditTemplate',
            description_msgid='CMFPlomino_help_FieldEditTemplate',
            i18n_domain='CMFPlomino',
        ),
    ),

    BooleanField(
        name='Mandatory',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Mandatory",
            description=("Is this field mandatory? "
                "(empty value will not be allowed)"),
            label_msgid='CMFPlomino_label_FieldMandatory',
            description_msgid='CMFPlomino_help_FieldMandatory',
            i18n_domain='CMFPlomino',
        ),
    ),
    TextField(
        name='ValidationFormula',
        widget=TextAreaWidget(
            label="Validation formula",
            description="Evaluate the input validation",
            label_msgid='CMFPlomino_label_FieldValidation',
            description_msgid='CMFPlomino_help_FieldValidation',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='ToBeIndexed',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Add to index",
            description="The field will be searchable",
            label_msgid='CMFPlomino_label_FieldIndex',
            description_msgid='CMFPlomino_help_FieldIndex',
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='IndexType',
        default="DEFAULT",
        widget=SelectionWidget(
            label="Index type",
            description="The way the field values will be indexed",
            label_msgid='CMFPlomino_label_FieldIndexType',
            description_msgid='CMFPlomino_help_FieldIndexType',
            i18n_domain='CMFPlomino',
        ),
        vocabulary='index_vocabulary',
    ),
),
)

PlominoField_schema = BaseSchema.copy() + schema.copy()


def get_field_types():
    field_types = FIELD_TYPES
    for plugin_field in component.getUtilitiesFor(interfaces.IPlominoField):
        params = plugin_field[1].plomino_field_parameters
        field_types[str(plugin_field[0])] = [
                params['label'],
                params['index_type']]
    return field_types


class PlominoField(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoField)

    meta_type = 'PlominoField'
    _at_rename_after_creation = False

    schema = PlominoField_schema

    security.declarePublic('validateFormat')
    def validateFormat(self, submittedValue):
        """ Check if submitted value matches the expected field format
        """
        adapt = self.getSettings()
        return adapt.validate(submittedValue)

    security.declarePublic('processInput')
    def processInput(self, submittedValue, doc, process_attachments, validation_mode=False):
        """ Process submitted value according the field type
        """
        fieldtype = self.getFieldType()
        fieldname = self.id
        adapt = self.getSettings()
        if fieldtype == "ATTACHMENT" and process_attachments:
            if isinstance(submittedValue, FileUpload):
                current_files = doc.getItem(fieldname)
                if not current_files:
                    current_files = {}
                (new_file, contenttype) = doc.setfile(submittedValue)
                if new_file is not None:
                    if adapt.type == "SINGLE":
                        for filename in current_files.keys():
                            if filename != new_file:
                                doc.deletefile(filename)
                        current_files = {}
                    current_files[new_file]=contenttype
                v = current_files
            else:
                v = None
        else:
            try:
                v = adapt.processInput(submittedValue)
            except Exception, e:
                if validation_mode:
                    # when validating, submitted values are potentially bad
                    # but it must not break getHideWhens, getFormFields, etc.
                    v = submittedValue
                else:
                    raise e
        return v

    security.declareProtected(READ_PERMISSION, 'getFieldRender')
    @plomino_profiler('fields')
    def getFieldRender(self, form, doc, editmode, creation=False, request=None):
        """ Rendering the field
        """
        mode = self.getFieldMode()
        fieldname = self.id
        if doc:
            target = doc
        else:
            target = form

        adapt = self.getSettings()
        fieldvalue = adapt.getFieldValue(
                form, doc, editmode, creation, request)

        # get the rendering template
        pt = None
        if mode == "EDITABLE" and editmode:
            field_mode = "Edit"
            pt_id = self.getFieldEditTemplate()
            # if custom template, use it
            if pt_id:
                pt = getattr(self.resources, pt_id).__of__(self)
        else:
            field_mode = "Read"
            # if custom template, use it
            pt_id = self.getFieldReadTemplate()
            if pt_id:
                pt = getattr(self.resources, pt_id).__of__(self)

        # If no custom template provided, get the template associated with the field type
        if not pt:
            if field_mode == "Read" and hasattr(adapt, 'read_template'):
                pt = adapt.read_template
            elif field_mode == "Edit" and hasattr(adapt, 'edit_template'):
                pt = adapt.edit_template
            else:
                field_type = self.FieldType
                pt = self.getRenderingTemplate(
                        '%sField%s' % (field_type, field_mode))
                if not pt:
                    pt = self.getRenderingTemplate(
                            "DefaultField"+field_mode)

        selection = self.getSettings().getSelectionList(target)

        try:
            return pt(fieldname=fieldname,
                    fieldvalue=fieldvalue,
                    selection=selection,
                    field=self,
                    doc=target
                    )
        except Exception, e:
            self.traceRenderingErr(e, self)
            return ""

    def _setupConfigAnnotation(self):
        """ Make sure that we can store the field config.
        """
        annotations = IAnnotations(self)
        settings = annotations.get("PLOMINOFIELDCONFIG", None)
        if not settings:
            annotations["PLOMINOFIELDCONFIG"] = PersistentDict()

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        """ post edit
        """
        self._setupConfigAnnotation()
        self.cleanFormulaScripts(
                'field_%s_%s' % (
                    self.getParentNode().id,
                    self.id))
        self.cleanFormulaScripts(
                "field_%s_%s_ValidationFormula" % (
                    self.getParentNode().id,
                    self.id))
        db = self.getParentDatabase()
        if self.getToBeIndexed() and not db.DoNotReindex:
            db.getIndex().createFieldIndex(
                    self.id,
                    self.getFieldType(),
                    indextype=self.getIndexType())

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        """ post create
        """
        self._setupConfigAnnotation()
        db = self.getParentDatabase()
        if self.getToBeIndexed() and not db.DoNotReindex:
            db.getIndex().createFieldIndex(
                    self.id,
                    self.getFieldType(),
                    indextype=self.getIndexType())

    security.declarePublic('getSettings')
    def getSettings(self, key=None):
        """
        """
        fieldclass = component.queryUtility(
                interfaces.IPlominoField,
                self.FieldType,
                None)
        if fieldclass:
            fieldinterface = fieldclass.plomino_field_parameters['interface']
        else:
            if hasattr(fields, self.FieldType.lower()):
                # 1. Find the module for FieldType.
                # 2. Find the corresponding interface in that module.
                fieldinterface = getattr(
                        getattr(fields, self.FieldType.lower()),
                        "I"+self.FieldType.capitalize()+"Field")
            else:
                fieldinterface = getattr(
                        getattr(fields, "base"),
                        "IBaseField")

        if key:
            return getattr(fieldinterface(self), key, None)
        else:
            return fieldinterface(self)

    def type_vocabulary(self):
        ALL_FIELD_TYPES = get_field_types()
        l = [[f, ALL_FIELD_TYPES[f][0]] for f in ALL_FIELD_TYPES.keys()]
        l.sort(key=lambda f: f[1])
        return l
    
    def index_vocabulary(self):
        default_index = get_field_types()[self.getFieldType()][1]
        indexes = [['DEFAULT', 'Default (%s)' % default_index]]
        db = self.getParentDatabase()
        idx = db.getIndex()
        index_ids = [i['name'] for i in idx.Indexes.filtered_meta_types()]
        for i in index_ids:
            label = "%s (%s)" % (
                    i, {"FieldIndex": "match exact value", 
                        "ZCTextIndex": "match any contained words",
                        "KeywordIndex": "match list elements"
                        }.get(i)
                    )
            indexes.append([id, label])
        return indexes

    def getContentType(self, fieldname=None):
        # Make sure RICHTEXT fields are considered as HTML
        # (TinyMCE 1.1.8 tests if content is HTML
        # if not, it displays a basic textarea)
        if self.FieldType == "RICHTEXT":
            return "text/html"
        return "text/plain"
    
    @property
    def formula_ids(self):
        return {'Formula':  'field_%s_%s' % (
                    self.getParentNode().id, self.id),
                'ValidationFormula': 'field_%s_%s_ValidationFormula' % (
                    self.getParentNode().id, self.id)}

registerType(PlominoField, PROJECTNAME)

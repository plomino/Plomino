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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFPlomino import fields, plomino_profiler

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.CMFPlomino.config import *
from PlominoDocument import TemporaryDocument

from Products.CMFPlomino.PlominoUtils import StringToDate
from Products.CMFPlomino.browser import PlominoMessageFactory as _
from fields.selection import ISelectionField
from fields.text import ITextField
from fields.datetime import IDatetimeField
from fields.name import INameField
from fields.doclink import IDoclinkField
from ZPublisher.HTTPRequest import FileUpload
from zope import component
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict

import logging
logger = logging.getLogger('Plomino')

schema = Schema((

    StringField(
        name='id',
        widget=StringField._properties['widget'](
            label="Id",
            description="The field id",
            label_msgid=_('CMFPlomino_label_field_id', default="Id"),
            description_msgid=_('CMFPlomino_help_field_id', default="The field id"),
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='FieldType',
        default="TEXT",
        widget=SelectionWidget(
            label="Field type",
            description="The kind of this field",
            label_msgid=_('CMFPlomino_label_FieldType', default="Field type"),
            description_msgid=_('CMFPlomino_help_FieldType', default='The kind of this field'),
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
            label_msgid=_('CMFPlomino_label_FieldMode', default="Field mode"),
            description_msgid=_('CMFPlomino_help_FieldMode', default='How content will be generated'),
            i18n_domain='CMFPlomino',
        ),
        vocabulary= FIELD_MODES,
    ),
    TextField(
        name='Formula',
        widget=TextAreaWidget(
            label="Formula",
            description="How to calculate field content",
            label_msgid=_('CMFPlomino_label_FieldFormula', default="Formula"),
            description_msgid=_('CMFPlomino_help_FieldFormula', default='How to calculate field content'),
            i18n_domain='CMFPlomino',
            rows=10,
        ),
    ),
    StringField(
        name='FieldReadTemplate',
        widget=StringField._properties['widget'](
            label="Field read template",
            description="Custom rendering template in read mode",
            label_msgid=_('CMFPlomino_label_FieldReadTemplate', default="Field read template"),
            description_msgid=_('CMFPlomino_help_FieldReadTemplate', default='Custom rendering template in read mode'),
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='FieldEditTemplate',
        widget=StringField._properties['widget'](
            label="Field edit template",
            description="Custom rendering template in edit mode",
            label_msgid=_('CMFPlomino_label_FieldEditTemplate', default="Field edit template"),
            description_msgid=_('CMFPlomino_help_FieldEditTemplate', default='Custom rendering template in edit mode'),
            i18n_domain='CMFPlomino',
        ),
    ),

    BooleanField(
        name='Mandatory',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Mandatory",
            description="Is this field mandatory? (empty value will not be allowed)",
            label_msgid=_('CMFPlomino_label_FieldMandatory', default="Mandatory"),
            description_msgid=_('CMFPlomino_help_FieldMandatory', default='Is this field mandatory? (empty value will not be allowed)'),
            i18n_domain='CMFPlomino',
        ),
    ),
    TextField(
        name='ValidationFormula',
        widget=TextAreaWidget(
            label="Validation formula",
            description="Evaluate the input validation",
            label_msgid=_('CMFPlomino_label_FieldValidation', default="Validation formula"),
            description_msgid=_('CMFPlomino_help_FieldValidation', default='Evaluate the input validation'),
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='ToBeIndexed',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Add to index",
            description="The field will be searchable",
            label_msgid=_('CMFPlomino_label_FieldIndex', default="Add to index"),
            description_msgid=_('CMFPlomino_help_FieldIndex', default='The field will be searchable'),
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='IndexType',
        default="DEFAULT",
        widget=SelectionWidget(
            label="Index type",
            description="The way the field values will be indexed",
            label_msgid=_('CMFPlomino_label_FieldIndexType'),
            description_msgid=_('CMFPlomino_help_FieldIndexType', default='The way the field values will be indexed'),
            i18n_domain='CMFPlomino',
        ),
        vocabulary='index_vocabulary',
    ),
),
)

PlominoField_schema = BaseSchema.copy() + \
    schema.copy()

def get_field_types():
    field_types = FIELD_TYPES
    for plugin_field in component.getUtilitiesFor(interfaces.IPlominoField):
        params = plugin_field[1].plomino_field_parameters
        field_types[str(plugin_field[0])] = [params['label'], params['index_type']]
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
        """check if submitted value match the field expected format
        """
        adapt = self.getSettings()
        return adapt.validate(submittedValue)

    security.declarePublic('processInput')
    def processInput(self, submittedValue, doc, process_attachments, validation_mode=False):
        """process submitted value according the field type
        """
        fieldtype = self.getFieldType()
        fieldname = self.id
        adapt = self.getSettings()
        if fieldtype=="ATTACHMENT" and process_attachments:
            if isinstance(submittedValue, FileUpload):
                current_files=doc.getItem(fieldname)
                if not current_files:
                    current_files = {}
                (new_file, contenttype) = doc.setfile(submittedValue)
                if new_file is not None:
                    if adapt.type == "SINGLE":
                        for filename in current_files.keys():
                            if filename != new_file:
                                doc.deletefile(filename)
                        current_files={}
                    current_files[new_file]=contenttype
                v=current_files
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
        if doc is None:
            target = form
        else:
            target = doc

        adapt = self.getSettings()
        fieldvalue = adapt.getFieldValue(form, doc, editmode, creation, request)

        # get the rendering template
        pt = None
        if mode=="EDITABLE" and editmode:
            templatemode = "Edit"
            t = self.getFieldEditTemplate()
            # if custom template, use it
            if t:
                pt = getattr(self.resources, t).__of__(self)
        else:
            templatemode = "Read"
            # if custom template, use it
            t = self.getFieldReadTemplate()
            if t:
                pt = getattr(self.resources, t).__of__(self)

        # If no custom template provided, get the template associated with the field type
        if not pt:
            if templatemode=="Read" and hasattr(adapt, 'read_template'):
                pt = adapt.read_template
            elif templatemode=="Edit" and hasattr(adapt, 'edit_template'):
                pt = adapt.edit_template
            else:
                fieldType = self.FieldType
                pt = self.getRenderingTemplate(fieldType+"Field"+templatemode)
                if not pt:
                    pt = self.getRenderingTemplate("DefaultField"+templatemode)

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
        self.cleanFormulaScripts(self.id)
        db = self.getParentDatabase()
        if self.getToBeIndexed() and not db.DoNotReindex:
            db.getIndex().createFieldIndex(self.id, self.getFieldType(), indextype=self.getIndexType())

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        """post create
        """
        self._setupConfigAnnotation()
        db = self.getParentDatabase()
        if self.getToBeIndexed() and not db.DoNotReindex:
            db.getIndex().createFieldIndex(self.id, self.getFieldType(), indextype=self.getIndexType())

    security.declarePublic('getSettings')
    def getSettings(self, key=None):
        """
        """
        fieldclass = component.queryUtility(interfaces.IPlominoField, self.FieldType, None)
        if fieldclass is None:
            if hasattr(fields, self.FieldType.lower()):
                fieldinterface = getattr(getattr(fields, self.FieldType.lower()), "I"+self.FieldType.capitalize()+"Field")
            else:
                fieldinterface = getattr(getattr(fields, "base"), "IBaseField")
        else:
            fieldinterface = fieldclass.plomino_field_parameters['interface']

        if key is None:
            return fieldinterface(self)
        else:
            return getattr(fieldinterface(self), key, None)

    def type_vocabulary(self):
        ALL_FIELD_TYPES = get_field_types()
        l = [[f, ALL_FIELD_TYPES[f][0]] for f in ALL_FIELD_TYPES.keys()]
        l.sort(key=lambda f:f[1])
        return l
    
    def index_vocabulary(self):
        """ Vocabulary for the 'Index type' dropdown.
        """
        default_index = get_field_types()[self.getFieldType()][1]
        indexes = {'DEFAULT': 'Default (%s)' % default_index}
        db = self.getParentDatabase()
        idx = db.getIndex()
        index_ids = [i['name'] for i in idx.Indexes.filtered_meta_types()]
        for i in index_ids:
            if i in ['GopipIndex', 'UUIDIndex']:
                # Index types internal to Plone
                continue
            label = "%s%s" % (
                    i, {"FieldIndex": " (match exact value)", 
                        "ZCTextIndex": " (match any contained words)",
                        "KeywordIndex": " (match list elements)"
                        }.get(i, '')
                    )
            indexes[i] = label
        indexes = indexes.items()
        indexes.sort()
        return indexes

    def getContentType(self, fieldname=None):
        # Make sure RICHTEXT fields are considered as html
        # (TinyMCE 1.1.8 tests if content is HTML
        # if not, it displays a basic textarea)
        if self.FieldType == "RICHTEXT":
            return "text/html"
        return "text/plain"
    
    @property
    def formula_ids(self):
        return {'Formula':  "field_"+self.getParentNode().id+"_"+self.id,
                'ValidationFormula': "field_"+self.getParentNode().id+"_"+self.id+"_ValidationFormula"}
registerType(PlominoField, PROJECTNAME)

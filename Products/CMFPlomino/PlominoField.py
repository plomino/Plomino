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

from Products.CMFPlomino import fields

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.CMFPlomino.config import *
from PlominoDocument import TemporaryDocument

##code-section module-header #fill in your manual code here
from Products.CMFPlomino.PlominoUtils import StringToDate
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

##/code-section module-header

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
        vocabulary= FIELD_MODES,
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
            description="Is this field mandatory? (empty value will not be allowed)",
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
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoField_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
def get_field_types():
    field_types = FIELD_TYPES
    for plugin_field in component.getUtilitiesFor(interfaces.IPlominoField):
        params = plugin_field[1].plomino_field_parameters
        field_types[str(plugin_field[0])] = [params['label'], params['index_type']]
    return field_types

##/code-section after-schema

class PlominoField(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoField)

    meta_type = 'PlominoField'
    _at_rename_after_creation = False

    schema = PlominoField_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('validateFormat')
    def validateFormat(self, submittedValue):
        """check if submitted value match the field expected format
        """
        adapt = self.getSettings()
        return adapt.validate(submittedValue)

    security.declarePublic('processInput')
    def processInput(self, submittedValue, doc, process_attachments):
        """process submitted value according the field type
        """
        fieldtype = self.getFieldType()
        fieldname = self.id
        adapt = self.getSettings()
        if fieldtype=="ATTACHMENT" and process_attachments:
            if isinstance(submittedValue, FileUpload):
                current_files=doc.getItem(fieldname)
                if current_files=='':
                    current_files={}
                (new_file, contenttype) = doc.setfile(submittedValue)
                if new_file is not None:
                    current_files[new_file]=contenttype
                v=current_files
            else:
                v = None
        else:
            v = adapt.processInput(submittedValue)
        return v

    security.declareProtected(READ_PERMISSION, 'getFieldRender')
    def getFieldRender(self, form, doc, editmode, creation=False, request=None):
        """Rendering the field
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
        pt=None
        if mode=="EDITABLE" and editmode:
            templatemode="Edit"
            # if custom template, use it
            if not self.getFieldEditTemplate()=="":
                pt=getattr(self.resources, self.getFieldEditTemplate()).__of__(self)
        else:
            templatemode="Read"
            # if custom template, use it
            if not self.getFieldReadTemplate()=="":
                pt=getattr(self.resources, self.getFieldReadTemplate()).__of__(self)

        # if no custom template provided, get the template associated to the field type
        if pt is None:
            if templatemode=="Read" and hasattr(adapt, 'read_template'):
                pt = adapt.read_template
            elif templatemode=="Edit" and hasattr(adapt, 'edit_template'):
                pt = adapt.edit_template
            else:
                fieldType = self.FieldType
                pt=self.getRenderingTemplate(fieldType+"Field"+templatemode)
                if pt is None:
                    pt=self.getRenderingTemplate("DefaultField"+templatemode)

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
        self.cleanFormulaScripts("field_"+self.getParentNode().id+"_"+self.id)
        db = self.getParentDatabase()
        if self.getToBeIndexed() and not db.DoNotReindex:
            db.getIndex().createFieldIndex(self.id, self.getFieldType())

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        """post create
        """
        self._setupConfigAnnotation()
        db = self.getParentDatabase()
        if self.getToBeIndexed() and not db.DoNotReindex:
            db.getIndex().createFieldIndex(self.id, self.getFieldType())

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

    def getContentType(self, fieldname=None):
        # Make sure RICHTEXT fields are considered as html
        # (TinyMCE 1.1.8 tests if content is HTML
        # if not, it displays a basic textarea)
        if self.FieldType == "RICHTEXT":
            return "text/html"
        return "text/plain"
        
registerType(PlominoField, PROJECTNAME)
# end of class PlominoField

##code-section module-footer #fill in your manual code here
##/code-section module-footer




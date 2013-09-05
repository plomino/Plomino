# -*- coding: utf-8 -*-
#
# File: PlominoColumn.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.CMFPlomino.config import PROJECTNAME
from Products.CMFPlomino.browser import PlominoMessageFactory as _
from validator import isValidPlominoId

schema = Schema((

    StringField(
        name='id',
        widget=StringField._properties['widget'](
            label="Id",
            description="Column id",
            label_msgid=_('CMFPlomino_label_column_id', default="Id"),
            description_msgid=_('CMFPlomino_help_column_id', default="Column id"),
            i18n_domain='CMFPlomino',
        ),
        validators=("isValidId", isValidPlominoId),
    ),
    StringField(
        name='SelectedField',
        widget=SelectionWidget(
            label="Fields list",
            description=("Field value to display in the column. "
                "(It does not apply if Formula is provided)."),
#            label_msgid=_('CMFPlomino_label_FieldType'),
#            description_msgid=_('CMFPlomino_help_FieldType'),
#            i18n_domain='CMFPlomino',
        ),
        vocabulary='getFormFields',
    ),
    TextField(
        name='Formula',
        widget=TextAreaWidget(
            label="Formula",
            description="Python code returning the column value.",
            label_msgid=_('CMFPlomino_label_ColumnFormula', default="Formula"),
            description_msgid=_('CMFPlomino_help_ColumnFormula', default='Python code returning the column value.'),
            i18n_domain='CMFPlomino',
        ),
    ),
#    IntegerField(
#        name='Position',
#        widget=IntegerField._properties['widget'](
#            label="Position",
#            description="Position in view",
#            label_msgid=_('CMFPlomino_label_ColumnPosition'),
#            description_msgid=_('CMFPlomino_help_ColumnPosition'),
#            i18n_domain='CMFPlomino',
#        ),
#    ),
    BooleanField(
        name='HiddenColumn',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Hidden column",
            label_msgid=_('CMFPlomino_label_HiddenColumn', default="Hidden column"),
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='DisplaySum',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Display column sum",
            label_msgid=_('CMFPlomino_label_DisplaySum', default="Display column sum"),
            i18n_domain='CMFPlomino',
        ),
    ),
),
)

PlominoColumn_schema = BaseSchema.copy() + \
    schema.copy()


class PlominoColumn(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoColumn)

    meta_type = 'PlominoColumn'
    _at_rename_after_creation = False

    schema = PlominoColumn_schema

    # Methods
    security.declarePublic('getFormFields')
    def getFormFields(self):
        """ Get a list of all the fields in the database
        """
        fields = []
        for form in self.getParentView().getParentDatabase().getForms():
            fields.append(['', '=== ' + form.id + ' ==='])
            fields.extend(
                    [(form.id + '/' + field.id, field.id)
                        for field in form.getFormFields()])
        return fields

    security.declarePublic('getColumnName')
    def getColumnName(self):
        """ Get column name
        """
        return self.id

    security.declarePublic('getParentView')
    def getParentView(self):
        """ Get parent view
        """
        return self.getParentNode()

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        """post edit
        """
        v = self.getParentView()
        v.declareColumn(self.getColumnName(), self)
        self.cleanFormulaScripts('column_%s_%s' % (v.id, self.id))
        db = self.getParentDatabase()
        if not db.DoNotReindex:
            db.getIndex().refresh()

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        """ Standard AT post create hook.
        """
        v = self.getParentView()
        v.declareColumn(self.getColumnName(), self)
        db = self.getParentDatabase()
        if not db.DoNotReindex:
            db.getIndex().refresh()

    security.declarePublic('post_validate')
    def post_validate(self, REQUEST, errors={}):
        """ Ensure we have either a field or a formula
        """
        form = REQUEST.form
        formula = form.get('Formula', None)
        if formula:
            return errors
        selected_field = form.get('SelectedField', None)
        if not selected_field:
            errors['SelectedField'] = u"If you don't specify a column formula, you need to select a field."
        return errors


registerType(PlominoColumn, PROJECTNAME)
# end of class PlominoColumn

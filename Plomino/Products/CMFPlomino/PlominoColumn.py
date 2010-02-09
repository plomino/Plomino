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

from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='id',
        widget=StringField._properties['widget'](
            label="Id",
            description="Column id",
            label_msgid='CMFPlomino_label_column_id',
            description_msgid='CMFPlomino_help_column_id',
            i18n_domain='CMFPlomino',
        ),
    ),
    TextField(
        name='Formula',
        widget=TextAreaWidget(
            label="Formula",
            description="Python code returning the column value.",
            label_msgid='CMFPlomino_label_ColumnFormula',
            description_msgid='CMFPlomino_help_ColumnFormula',
            i18n_domain='CMFPlomino',
        ),
    ),
    IntegerField(
        name='Position',
        widget=IntegerField._properties['widget'](
            label="Position",
            description="Position in view",
            label_msgid='CMFPlomino_label_ColumnPosition',
            description_msgid='CMFPlomino_help_ColumnPosition',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='HiddenColumn',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Hidden column",
            label_msgid='CMFPlomino_label_HiddenColumn',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='DisplaySum',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Display column sum",
            label_msgid='CMFPlomino_label_DisplaySum',
            i18n_domain='CMFPlomino',
        ),
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoColumn_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoColumn(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoColumn)

    meta_type = 'PlominoColumn'
    _at_rename_after_creation = True

    schema = PlominoColumn_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('getColumnName')
    def getColumnName(self):
        """get column name
        """
        return self.id

    security.declarePublic('getParentView')
    def getParentView(self):
        """get parent view
        """
        return self.getParentNode()

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        """post edit
        """
        v = self.getParentView()
        v.declareColumn(self.getColumnName(), self)
        self.cleanFormulaScripts("column_"+v.id+"_"+self.id)
        self.getParentDatabase().getIndex().refresh()

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        """post create
        """
        v = self.getParentView()
        v.declareColumn(self.getColumnName(), self)
        self.getParentDatabase().getIndex().refresh()


registerType(PlominoColumn, PROJECTNAME)
# end of class PlominoColumn

##code-section module-footer #fill in your manual code here
##/code-section module-footer




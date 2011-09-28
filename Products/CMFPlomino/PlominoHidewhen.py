# -*- coding: utf-8 -*-
#
# File: PlominoHidewhen.py
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
            description="The hide-when id",
            label_msgid='CMFPlomino_label_hidewhen_id',
            description_msgid='CMFPlomino_help_hidewhen_id',
            i18n_domain='CMFPlomino',
        ),
    ),
    TextField(
        name='Formula',
        widget=TextAreaWidget(
            label="Formula",
            description="If returning True, the block will be hidden.",
            label_msgid='CMFPlomino_label_HidewhenFormula',
            description_msgid='CMFPlomino_help_HidewhenFormula',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='isDynamicHidewhen',
        default=False,
        widget=BooleanField._properties['widget'](
            label="Dynamic Hide-when",
            description="Hide-when are evaluated dynamically when the user enters information",
            label_msgid='CMFPlomino_label_isDynamicHidewhen',
            description_msgid='CMFPlomino_help_isDynamicHidewhen',
            i18n_domain='CMFPlomino',
        ),
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoHidewhen_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoHidewhen(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoHidewhen)

    meta_type = 'PlominoHidewhen'
    _at_rename_after_creation = False

    schema = PlominoHidewhen_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        """
        """
        self.cleanFormulaScripts("hidewhen_"+self.getParentNode().id+"_"+self.id)


registerType(PlominoHidewhen, PROJECTNAME)
# end of class PlominoHidewhen

##code-section module-footer #fill in your manual code here
##/code-section module-footer




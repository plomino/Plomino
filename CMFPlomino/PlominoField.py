# -*- coding: utf-8 -*-
#
# File: PlominoField.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:38 2006
# Generator: ArchGenXML Version 1.5.1-svn
#            http://plone.org/products/archgenxml
#
# Zope Public License (ZPL)
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

__author__ = """[Eric BREHAULT] <[ebrehault@gmail.com]>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
##/code-section module-header

schema = Schema((

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
        vocabulary= [["TEXT", "Text"],["NUMBER", "Number"],["RICHTEXT", "Rich text"],["DATETIME", "Date/Time"],["SELECTION", "Selection list"],["MULTISELECTION", "Multi-Selection list"],["CHECKBOX", "Check boxes"],["RADIO", "Radio buttons"]]
    ),

    StringField(
        name='FieldMode',
        default="EDITABLE",
        widget=SelectionWidget(
            label="Field mode",
            description="How conten will be generated",
            label_msgid='CMFPlomino_label_FieldMode',
            description_msgid='CMFPlomino_help_FieldMode',
            i18n_domain='CMFPlomino',
        ),
        vocabulary= [["EDITABLE", "Editable"], ["COMPUTED", "Computed"], ["DISPLAY", "Computed for display"]]
    ),

    TextField(
        name='Formula',
        widget=TextAreaWidget(
            label="Formula",
            description="How to calculate field content",
            label_msgid='CMFPlomino_label_Formula',
            description_msgid='CMFPlomino_help_Formula',
            i18n_domain='CMFPlomino',
        )
    ),

    LinesField(
        name='SelectionList',
        widget=LinesWidget(
            label="Selection list",
            description="Listo of values to select, one for line",
            label_msgid='CMFPlomino_label_SelectionList',
            description_msgid='CMFPlomino_help_SelectionList',
            i18n_domain='CMFPlomino',
        )
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoField_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoField(BaseContent):
    """Plomino Field
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'PlominoField'

    meta_type = 'PlominoField'
    portal_type = 'PlominoField'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    content_icon = 'PlominoField.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "PlominoField"
    typeDescMsgId = 'description_edit_plominofield'

    _at_rename_after_creation = True

    schema = PlominoField_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('getProperSelectionList')
    def getProperSelectionList(self):
        """if value not specified (format: label|value), use label as value
        (return label|label)
        """
	s = self.getSelectionList()
	proper = []
	for v in s:
		l = v.split('|')
		if len(l)==2:
			proper.append(v)
		else:
			proper.append(v+'|'+v)
	return proper

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        """Post edit
        """
	if not self.getFieldMode()=="DISPLAY":
		db = self.getParentDatabase()
		db.getIndex().createIndex(self.Title())

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        """Post creation
        """
	if not self.getFieldMode()=="DISPLAY":
		db = self.getParentDatabase()
		db.getIndex().createIndex(self.Title())


registerType(PlominoField, PROJECTNAME)
# end of class PlominoField

##code-section module-footer #fill in your manual code here
##/code-section module-footer




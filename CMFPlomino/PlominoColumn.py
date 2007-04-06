# -*- coding: utf-8 -*-
#
# File: PlominoColumn.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:38 2006
# Generator: ArchGenXML Version 1.5.1-svn
#			http://plone.org/products/archgenxml
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

from Products.CMFPlomino.config import PROJECTNAME
##/code-section module-header

schema = Schema((
	StringField(
		name='id',
		widget=StringWidget(
			label="Id",
			description="Column id",
			label_msgid='CMFPlomino_label_ColumnId',
			description_msgid='CMFPlomino_help_ColumnId',
			i18n_domain='CMFPlomino',
		)
	),
	
	TextField(
		name='Formula',
		widget=TextAreaWidget(
			label="Formula",
			description="A column formula is a line of python which should return a value.",
			label_msgid='CMFPlomino_label_Formula',
			description_msgid='CMFPlomino_help_Formula',
			i18n_domain='CMFPlomino',
		)
	),

	IntegerField(
		name='Position',
		widget=IntegerWidget(
			label="Position",
			description="Position in view",
			label_msgid='CMFPlomino_label_Position',
			description_msgid='CMFPlomino_help_Position',
			i18n_domain='CMFPlomino',
		)
	),
	
	BooleanField(
		name='HiddenColumn',
		default="0",
		widget=BooleanWidget(
			label="Hidden column",
			description="The column is hidden or not in the view",
			label_msgid='CMFPlomino_label_HiddenColumn',
			description_msgid='CMFPlomino_help_HiddenColumn',
			i18n_domain='CMFPlomino',
		)
	),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoColumn_schema = BaseSchema.copy() + \
	schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoColumn(BaseContent):
	"""Plomino view column
	"""
	security = ClassSecurityInfo()
	__implements__ = (getattr(BaseContent,'__implements__',()),)

	# This name appears in the 'add' box
	archetype_name = 'PlominoColumn'

	meta_type = 'PlominoColumn'
	portal_type = 'PlominoColumn'
	allowed_content_types = []
	filter_content_types = 0
	global_allow = 0
	content_icon = 'PlominoColumn.gif'
	immediate_view = 'base_view'
	default_view = 'base_view'
	suppl_views = ()
	typeDescription = "PlominoColumn"
	typeDescMsgId = 'description_edit_plominocolumn'

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

	security.declarePublic('at_post_create_script')
	def at_post_create_script(self):
		"""post create
		"""
		v = self.getParentView()
		v.declareColumn(self.getColumnName(), self)


registerType(PlominoColumn, PROJECTNAME)
# end of class PlominoColumn

##code-section module-footer #fill in your manual code here
##/code-section module-footer




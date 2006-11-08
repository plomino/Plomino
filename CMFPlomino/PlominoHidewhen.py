# -*- coding: utf-8 -*-
#
# File: PlominoHidewhen.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:39 2006
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
from Products.CMFCore import CMFCorePermissions

from Products.CMFPlomino.config import PROJECTNAME
##/code-section module-header

schema = Schema((

	TextField(
		name='Formula',
		widget=TextAreaWidget(
			label="Formula",
			description="hide-when formula",
			label_msgid='CMFPlomino_label_Formula',
			description_msgid='CMFPlomino_help_Formula',
			i18n_domain='CMFPlomino',
		)
	),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoHidewhen_schema = BaseSchema.copy() + \
	schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoHidewhen(BaseContent):
	"""Plomino hide-when formula
	"""
	security = ClassSecurityInfo()
	__implements__ = (getattr(BaseContent,'__implements__',()),)

	# This name appears in the 'add' box
	archetype_name = 'PlominoHidewhen'

	meta_type = 'PlominoHidewhen'
	portal_type = 'PlominoHidewhen'
	allowed_content_types = []
	filter_content_types = 0
	global_allow = 0
	content_icon = 'PlominoHidewhen.gif'
	immediate_view = 'base_view'
	default_view = 'base_view'
	suppl_views = ()
	typeDescription = "PlominoHidewhen"
	typeDescMsgId = 'description_edit_plominohidewhen'

	_at_rename_after_creation = True

	schema = PlominoHidewhen_schema

	##code-section class-header #fill in your manual code here
	##/code-section class-header

	# Methods
	security.declarePublic('at_post_create_script')
	def at_post_create_script(self):
		"""Post creation
		"""
		# replace Title with its normalized equivalent (stored in id)
		self.setTitle(self.id)
		self.reindexObject()


registerType(PlominoHidewhen, PROJECTNAME)
# end of class PlominoHidewhen

##code-section module-footer #fill in your manual code here
##/code-section module-footer




# -*- coding: utf-8 -*-
#
# File: PlominoAgent.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:37 2006
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
from Products.CMFPlomino.PlominoUtils import *
##/code-section module-header

schema = Schema((
	TextField(
		name='Content',
		widget=TextAreaWidget(
			label="Parameter or code",
			description="Code or parameter depending on the action type",
			label_msgid='CMFPlomino_label_Content',
			description_msgid='CMFPlomino_help_Content',
			i18n_domain='CMFPlomino',
		)
	),
),
)

##code-section after-local-schema #fill in your manual code here
ACTION_TYPES = [["OPENFORM", "Open form"], ["OPENVIEW", "Open view"], ["CLOSE", "Close"], ["SAVE", "Save"], ["PYTHON", "Python script"]]
ACTION_DISPLAY = [["LINK", "Link"], ["SUBMIT", "Submit button"], ["BUTTON", "Button"]]
##/code-section after-local-schema

PlominoAgent_schema = BaseSchema.copy() + \
	schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoAgent(BaseContent):
	"""
	"""
	security = ClassSecurityInfo()
	__implements__ = (getattr(BaseContent,'__implements__',()),)

	# This name appears in the 'add' box
	archetype_name = 'PlominoAgent'

	meta_type = 'PlominoAgent'
	portal_type = 'PlominoAgent'
	allowed_content_types = []
	filter_content_types = 0
	global_allow = 0
	content_icon = 'PlominoAction.gif'
	immediate_view = 'base_view'
	default_view = 'base_view'
	suppl_views = ()
	typeDescription = "PlominoAgent"
	typeDescMsgId = 'description_edit_plominoagent'

	_at_rename_after_creation = True

	schema = PlominoAgent_schema

	##code-section class-header #fill in your manual code here
	##/code-section class-header

	# Methods
	security.declareProtected(CMFCorePermissions.View, 'runAgent')
	def runAgent(self,REQUEST=None):
		"""execute the python code
		"""
		plominoContext = self
		plominoReturnURL = self.getParentDatabase().absolute_url()
		try:
			RunFormula(plominoContext, self.Content())
			if REQUEST != None:
				REQUEST.RESPONSE.redirect(plominoReturnURL)
		except Exception, e:
			return "Error: %s \nCode->\n%s" % (e, self.Content())
	
	security.declarePublic('at_post_create_script')
	def at_post_create_script(self):
		"""Post creation
		"""
		# replace Title with its normalized equivalent (stored in id)
		self.setTitle(self.id)
		self.reindexObject()

	security.declarePublic('getParentDatabase')
	def getParentDatabase(self):
		"""Get the database containing this form
		"""
		return self.getParentNode()

	def process_timer(self):
		self.runAgent()
		
registerType(PlominoAgent, PROJECTNAME)
# end of class PlominoAgent

##code-section module-footer #fill in your manual code here
##/code-section module-footer




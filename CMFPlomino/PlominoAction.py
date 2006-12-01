# -*- coding: utf-8 -*-
#
# File: PlominoAction.py
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

	StringField(
		name='Label',
		widget=StringWidget(
			label="Label",
			description="The action name",
			label_msgid='CMFPlomino_label_Label',
			description_msgid='CMFPlomino_help_Label',
			i18n_domain='CMFPlomino',
		)
	),

	StringField(
		name='ActionType',
		widget=SelectionWidget(
			label="Action type",
			description="Select the type for this action",
			label_msgid='CMFPlomino_label_ActionType',
			description_msgid='CMFPlomino_help_ActionType',
			i18n_domain='CMFPlomino',
		),
		vocabulary=  [["OPENFORM", "Open form"], ["OPENVIEW", "Open view"], ["CLOSE", "Close"], ["SAVE", "Save"], ["PYTHON", "Python script"]]
	),

	StringField(
		name='ActionDisplay',
		widget=SelectionWidget(
			label="Action display",
			description="How the action is shown",
			label_msgid='CMFPlomino_label_ActionDisplay',
			description_msgid='CMFPlomino_help_ActionDisplay',
			i18n_domain='CMFPlomino',
		),
		vocabulary= [["LINK", "Link"], ["SUBMIT", "Submit button"], ["BUTTON", "Button"]]
	),
	
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
	
	TextField(
		name='Hidewhen',
		widget=TextAreaWidget(
			label="Hide-when formula",
			description="Action is hiden if formula return True",
			label_msgid='CMFPlomino_label_actionhidewhen',
			description_msgid='CMFPlomino_help_actionhidewhen',
			i18n_domain='CMFPlomino',
		)
	),
	
	BooleanField(
		name='InActionBar',
		default="1",
		widget=BooleanWidget(
			label="Display action in action bar",
			description="Display action in action bar (yes/no)",
			label_msgid='CMFPlomino_label_ActionInActionBar',
			description_msgid='CMFPlomino_help_ActionInActionBar',
			i18n_domain='CMFPlomino',
		)
	),
),
)

##code-section after-local-schema #fill in your manual code here
ACTION_TYPES = [["OPENFORM", "Open form"], ["OPENVIEW", "Open view"], ["CLOSE", "Close"], ["SAVE", "Save"], ["PYTHON", "Python script"]]
ACTION_DISPLAY = [["LINK", "Link"], ["SUBMIT", "Submit button"], ["BUTTON", "Button"]]
##/code-section after-local-schema

PlominoAction_schema = BaseSchema.copy() + \
	schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoAction(BaseContent):
	"""
	"""
	security = ClassSecurityInfo()
	__implements__ = (getattr(BaseContent,'__implements__',()),)

	# This name appears in the 'add' box
	archetype_name = 'PlominoAction'

	meta_type = 'PlominoAction'
	portal_type = 'PlominoAction'
	allowed_content_types = []
	filter_content_types = 0
	global_allow = 0
	content_icon = 'PlominoAction.gif'
	immediate_view = 'base_view'
	default_view = 'base_view'
	suppl_views = ()
	typeDescription = "PlominoAction"
	typeDescMsgId = 'description_edit_plominoaction'

	_at_rename_after_creation = True

	schema = PlominoAction_schema

	##code-section class-header #fill in your manual code here
	##/code-section class-header

	# Methods

	security.declareProtected(CMFCorePermissions.View, 'executeAction')
	def executeAction(self,target):
		"""return the action resulting url
		"""
		db = self.getParentDatabase()
		if self.ActionType == "OPENFORM":
			form = db.getForm(self.Content())
			return form.absolute_url() + '/OpenForm'
		elif self.ActionType == "OPENVIEW":
			view = db.getView(self.Content())
			return view.absolute_url() + '/OpenView'
		elif self.ActionType == "CLOSE":
			return db.absolute_url() + '/OpenDatabase'
		elif self.ActionType == "PYTHON":
			if target is None:
				targetid="None"
			else:
				targetid=target.id
			return self.absolute_url() + '/runScript?target='+targetid
		else:
			return '.'

	security.declareProtected(CMFCorePermissions.View, 'runScript')
	def runScript(self,REQUEST):
		"""execute the python code
		"""
		target = REQUEST.get('target')
		if target == "None":
			plominoContext = self.getParentDatabase()
		else:
			plominoContext = self.getParentDatabase()._getOb(target)
		plominoReturnURL = plominoContext.absolute_url()
		try:
			RunFormula(plominoContext, self.Content())
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


registerType(PlominoAction, PROJECTNAME)
# end of class PlominoAction

##code-section module-footer #fill in your manual code here
##/code-section module-footer




# -*- coding: utf-8 -*-
#
# File: PlominoForm.py
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
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.utils import make_uuid
from Products.CMFPlomino.PlominoUtils import *
from ZPublisher.HTTPResponse import HTTPResponse
from zLOG import LOG, ERROR

import re

import PlominoDocument
##/code-section module-header

schema = Schema((

	StringField(
		name='DocumentTitle',
		widget=StringWidget(
			label="Document title formula",
			description="Compute the document title",
			label_msgid='CMFPlomino_label_DocumentTitle',
			description_msgid='CMFPlomino_help_DocumentTitle',
			i18n_domain='CMFPlomino',
		)
	),
	
	TextField(
		name='onCreateDocument',
		widget=TextAreaWidget(
			label="On create document",
			description="Action to take when the document is created",
			label_msgid='CMFPlomino_label_onCreateDocument',
			description_msgid='CMFPlomino_help_onCreateDocument',
			i18n_domain='CMFPlomino',
		)
	),
	
	TextField(
		name='onOpenDocument',
		widget=TextAreaWidget(
			label="On open document",
			description="Action to take when the document is opened",
			label_msgid='CMFPlomino_label_onOpenDocument',
			description_msgid='CMFPlomino_help_onOpenDocument',
			i18n_domain='CMFPlomino',
		)
	),

	TextField(
		name='onSaveDocument',
		widget=TextAreaWidget(
			label="On save document",
			description="Action to take when saving the document",
			label_msgid='CMFPlomino_label_onSaveDocument',
			description_msgid='CMFPlomino_help_onSaveDocument',
			i18n_domain='CMFPlomino',
		)
	),

	StringField(
		name='ActionBarPosition',
		default="TOP",
		widget=SelectionWidget(
			label="Position of the action bar",
			description="Select the position of the action bar",
			label_msgid='CMFPlomino_label_ActionBarPosition',
			description_msgid='CMFPlomino_help_ActionBarPosition',
			i18n_domain='CMFPlomino',
		),
		vocabulary=  [["TOP", "At the top of the page"], ["BOTTOM", "At the bottom of the page"], ["BOTH", "At the top and at the bottom of the page "]]
	),
	
	TextField(
		name='FormLayout',
		allowable_content_types=('text/html',),
		widget=RichWidget(
			label="Form layout",
			description="The form layout. text with 'Plominofield' style correspond to the contained field elements",
			label_msgid='CMFPlomino_label_FormLayout',
			description_msgid='CMFPlomino_help_FormLayout',
			i18n_domain='CMFPlomino',
		),
		default_output_type='text/html'
	),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoForm_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
	schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoForm(ATFolder):
	"""
	"""
	security = ClassSecurityInfo()
	__implements__ = (getattr(ATFolder,'__implements__',()),)

	# This name appears in the 'add' box
	archetype_name = 'PlominoForm'

	meta_type = 'PlominoForm'
	portal_type = 'PlominoForm'
	allowed_content_types = ['PlominoField', 'PlominoAction', 'PlominoHidewhen'] + list(getattr(ATFolder, 'allowed_content_types', []))
	filter_content_types = 1
	global_allow = 0
	content_icon = 'PlominoForm.gif'
	immediate_view = 'base_view'
	default_view = 'base_view'
	suppl_views = ()
	typeDescription = "PlominoForm"
	typeDescMsgId = 'description_edit_plominoform'


	actions =  (


	   {'action': "string:${object_url}/OpenForm",
		'category': "object",
		'id': 'compose',
		'name': 'Compose',
		'permissions': (CREATE_PERMISSION,),
		'condition': 'python:1'
	   },


	)

	_at_rename_after_creation = True

	schema = PlominoForm_schema

	##code-section class-header #fill in your manual code here
	##/code-section class-header

	# Methods

	security.declareProtected(CREATE_PERMISSION, 'createDocument')
	def createDocument(self,REQUEST):
		"""create a document using the forms submitted content
		"""
		db = self.getParentDatabase()
		doc = db.createDocument()
		doc.setItem('Form', self.getFormName())

		# execute the onCreateDocument code of the form
		try:
			RunFormula(doc, self.getOnCreateDocument())
		except Exception:
			pass
			
		doc.saveDocument(REQUEST, True)

	security.declarePublic('getFields')
	def getFields(self):
		"""get fields
		"""
		return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoField']})
		
	security.declarePublic('getFormField')
	def getFormField(self, fieldname):
		"""return the field
		"""
		return self._getOb(fieldname)

	security.declarePublic('hasDateTimeField')
	def hasDateTimeField(self):
		"""return true if the form contains at least one DateTime field
		"""
		fields=[f.getObject() for f in self.getFields()]
		for f in fields:
			if f.getFieldType()=="DATETIME":
				return True
		return False
		
	security.declarePublic('getHidewhenFormulas')
	def getHidewhenFormulas(self):
		"""Get hidden formulae
		"""
		return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoHidewhen']})

	security.declarePublic('getFormName')
	def getFormName(self):
		"""Return the form name
		"""
		return self.Title()

	security.declarePublic('getParentDatabase')
	def getParentDatabase(self):
		"""Get the database containing this form
		"""
		return self.getParentNode()

	security.declareProtected(READ_PERMISSION, 'getFieldRender')
	def getFieldRender(self,doc,field,editmode,creation=False):
		"""Rendering the field
		"""
		mode = field.getFieldMode()
		fieldName = field.Title()
		
		# compute the value
		if mode=="EDITABLE":
			if doc is None:
				fieldValue = ""
			else:
				fieldValue = doc.getItem(fieldName)

		if mode=="DISPLAY" or mode=="COMPUTED":
			try:
				fieldValue = RunFormula(doc, field.getFormula())
			except Exception:
				fieldValue = ""
		
		if mode=="CREATION":
			if creation:
				# Note: on creation, there is no doc, we use self as param
				# in formula
				fieldValue = RunFormula(self, field.getFormula())
			else:
				fieldValue = doc.getItem(fieldName)
			
		# render according the field type
		if mode=="EDITABLE" and editmode:
			ptsuffix="Edit"
		else:
			ptsuffix="Read"

		fieldType = field.FieldType
		try:
			exec "pt = self."+fieldType+"Field"+ptsuffix
		except Exception:
			exec "pt = self.DefaultField"+ptsuffix
		req = self.REQUEST
		# NOTE: for some reasons, sometimes, REQUEST does not have a RESPONSE
		# and it causes pt_render to fail (KeyError 'RESPONSE')
		# why ? I don't know (If you know, tell me please (ebrehault@gmail.com), 
		# I would be happy to understand.
		# Anyhow, here is a small fix to avoid that.
		try:
			rep=self.REQUEST['RESPONSE']
		except Exception:
			self.REQUEST['RESPONSE']=HTTPResponse()
		return pt(fieldname=fieldName,
			fieldvalue=fieldValue,
			selection=field.getProperSelectionList(doc)
			)


	security.declareProtected(READ_PERMISSION, 'displayDocument')
	def displayDocument(self,doc,editmode=False, creation=False):
		"""display the document using the form's layout
		"""
		html_content = self.getField('FormLayout').get(self, mimetype='text/html')
		html_content = html_content.replace('\n', '')

		# remove the hidden content
		for hidewhen in self.getHidewhenFormulas():
			hidewhenName = hidewhen.Title
			try:
				result = RunFormula(doc, hidewhen.getObject().getFormula())
			except Exception:
				#if error, we hide anyway
				result = True
			start = '<span class="plominoHidewhenClass">start:'+hidewhenName+'</span>'
			end = '<span class="plominoHidewhenClass">end:'+hidewhenName+'</span>'
			if result:
				regexp = start+'.+'+end
				html_content = re.sub(regexp,'', html_content)
			else:
				html_content = html_content.replace(start, '')
				html_content = html_content.replace(end, '')

		#if editmode, we had a hidden field to handle the Form item value
		if editmode:
			html_content = "<input type='hidden' name='Form' value='"+self.getFormName()+"' />" + html_content

		# insert the fields with proper value and rendering
		for field in self.getFields():
			fieldName = field.Title
			#html_content = html_content.replace('#'+fieldName+'#', self.getFieldRender(doc, field.getObject(), editmode))
			html_content = html_content.replace('<span class="plominoFieldClass">'+fieldName+'</span>', self.getFieldRender(doc, field.getObject(), editmode, creation))

		# insert the actions
		for action in self.getActions(doc, False):
			actionName = action.Title()
			actionDisplay = action.ActionDisplay
			try:
				exec "pt = self."+actionDisplay+"Action"
			except Exception:
				pt = self.LINKAction
			action_render = pt(plominoaction=action, plominotarget=doc)
			#html_content = html_content.replace('#Action:'+actionName+'#', action_render)
			html_content = html_content.replace('<span class="plominoActionClass">'+actionName+'</span>', action_render)

		return html_content

	security.declarePublic('formLayout')
	def formLayout(self):
		"""return the form layout in edit mode (used to compose a new
		document)
		"""
		return self.displayDocument(None, True, True)

	security.declarePublic('getActions')
	def getActions(self, target, hide=True):
		"""Get actions
		"""
		all = self.getFolderContents(contentFilter = {'portal_type' : ['PlominoAction']})
		
		filtered = []
		for a in all:
			obj_a=a.getObject()
			if hide:
				try:
					result = RunFormula(target, obj_a.getHidewhen())
				except Exception:
					#if error, we hide anyway
					result = True
				if not result:
					filtered.append(obj_a)
			else:
				filtered.append(obj_a)
		return filtered

	security.declarePublic('at_post_create_script')
	def at_post_create_script(self):
		"""Post creation
		"""
		# replace Title with its normalized equivalent (stored in id)
		self.setTitle(self.id)
		self.reindexObject()
	
	security.declarePublic('at_post_edit_script')
	def at_post_edit_script(self):
		"""clean up the layout before saving
		"""
		# clean up the form layout field
		html_content = self.getField('FormLayout').get(self, mimetype='text/html')
		regexp = '<span class="plominoFieldClass"></span>'
		html_content = re.sub(regexp,'', html_content)
		regexp = '<span class="plominoActionClass"></span>'
		html_content = re.sub(regexp,'', html_content)
		regexp = '<span class="plominoHidewhenClass"></span>'
		self.setFormLayout(html_content)



registerType(PlominoForm, PROJECTNAME)
# end of class PlominoForm

##code-section module-footer #fill in your manual code here
##/code-section module-footer




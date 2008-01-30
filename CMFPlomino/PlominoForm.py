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
from Products.Archetypes.utils import make_uuid
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.HTTPRequest import FileUpload

import re

import PlominoDocument
from Products.CMFPlomino.PlominoUtils import StringToDate
from PlominoDesignManager import TemporaryDocument
import logging
logger=logging.getLogger("Plomino")

##/code-section module-header

schema = Schema((
	StringField(
		name='id',
		widget=StringWidget(
			label="Id",
			description="The form id",
			label_msgid='CMFPlomino_label_FormId',
			description_msgid='CMFPlomino_help_FormId',
			i18n_domain='CMFPlomino',
		)
	),
	StringField(
		name='DocumentTitle',
		schemata='Parameters',
		widget=StringWidget(
			label="Document title formula",
			description="Compute the document title",
			label_msgid='CMFPlomino_label_DocumentTitle',
			description_msgid='CMFPlomino_help_DocumentTitle',
			i18n_domain='CMFPlomino',
		)
	),
		
	StringField(
		name='ActionBarPosition',
		default="TOP",
		schemata='Parameters',
		widget=SelectionWidget(
			label="Position of the action bar",
			description="Select the position of the action bar",
			label_msgid='CMFPlomino_label_ActionBarPosition',
			description_msgid='CMFPlomino_help_ActionBarPosition',
			i18n_domain='CMFPlomino',
		),
		vocabulary=  [["TOP", "At the top of the page"], ["BOTTOM", "At the bottom of the page"], ["BOTH", "At the top and at the bottom of the page "]]
	),
	
	BooleanField(
		name='SearchForm',
		schemata='Parameters',
		default="0",
		widget=BooleanWidget(
			label="Search form",
			description="A search form is only used to search documents, it cannot be saved.",
			label_msgid='CMFPlomino_label_SearchForm',
			description_msgid='CMFPlomino_help_SearchForm',
			i18n_domain='CMFPlomino',
		)
	),
	
	StringField(
		name='SearchView',
		schemata='Parameters',
		widget=StringWidget(
			label="Search view",
			description="View used to display the search results",
			label_msgid='CMFPlomino_label_SearchView',
			description_msgid='CMFPlomino_help_SearchView',
			i18n_domain='CMFPlomino',
		)
	),
	
	TextField(
		name='SearchFormula',
		schemata='Parameters',
		widget=TextAreaWidget(
			label="Search formula",
			description="Leave blank to use default Zcatalog search",
			label_msgid='CMFPlomino_label_SearchFormula',
			description_msgid='CMFPlomino_help_SearchFormula',
			i18n_domain='CMFPlomino',
		)
	),
	
	TextField(
		name='onCreateDocument',
		schemata='Events',
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
		schemata='Events',
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
		schemata='Events',
		widget=TextAreaWidget(
			label="On save document",
			description="Action to take when saving the document",
			label_msgid='CMFPlomino_label_onSaveDocument',
			description_msgid='CMFPlomino_help_onSaveDocument',
			i18n_domain='CMFPlomino',
		)
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
		errors=self.validateInputs(REQUEST)
		if len(errors)>0:
			return self.notifyErrors(errors)
		doc = db.createDocument()
		doc.setItem('Form', self.getFormName())

		# execute the onCreateDocument code of the form
		try:
			#RunFormula(doc, self.getOnCreateDocument())
			self.runFormulaScript("form_"+self.id+"_oncreate", doc, self.getOnCreateDocument)
		except Exception:
			pass
			
		doc.saveDocument(REQUEST, True)

	security.declarePublic('getFields')
	def getFields(self, includesubforms=False):
		"""get fields
		"""
		fieldlist = self.getFolderContents(contentFilter = {'portal_type' : ['PlominoField']})
		result = [f.getObject() for f in fieldlist]
		if includesubforms:
			for subformname in self.getSubforms():
				result=result+self.getParentdatanse().getForm(subformname).getFields(True)
		return result
		
	security.declarePublic('getFormField')
	def getFormField(self, fieldname):
		"""return the field
		"""
		return self._getOb(fieldname)

	security.declarePublic('hasDateTimeField')
	def hasDateTimeField(self):
		"""return true if the form contains at least one DateTime field
		"""
		fields=self.getFields(includesubforms=True)
		for f in fields:
			if f.getFieldType()=="DATETIME":
				return True
		return False
		
	security.declarePublic('getHidewhenFormulas')
	def getHidewhenFormulas(self):
		"""Get hidden formulae
		"""
		list = self.getFolderContents(contentFilter = {'portal_type' : ['PlominoHidewhen']})
		return [h.getObject() for h in list]

	security.declarePublic('getFormName')
	def getFormName(self):
		"""Return the form name
		"""
		return self.id

	security.declarePublic('getParentDatabase')
	def getParentDatabase(self):
		"""Get the database containing this form
		"""
		return self.getParentNode()

	security.declarePublic('getSubforms')
	def getSubforms(self):
		"""return the names of the subforms embedded in the form
		"""
		html_content = self.getField('FormLayout').get(self, mimetype='text/html')
		html_content = html_content.replace('\n', '')
		r = re.compile('<span class="plominoSubformClass">([^<]+)</span>')
		return [i.strip() for i in r.findall(html_content)]
			
	security.declarePublic('readInputs')
	def readInputs(self, doc, REQUEST, process_attachments=False):
		""" read submitted values in REQUEST and store them in document according
		fields definition
		"""
		for f in self.getFields(includesubforms=True):
			mode = f.getFieldMode()
			fieldName = f.id
			if mode=="EDITABLE":
				submittedValue = REQUEST.get(fieldName)
				if submittedValue is not None:
					if submittedValue=='':
						doc.removeItem(fieldName)
					else:
						# if non-text field, convert the value
						if f.getFieldType()=="NUMBER":
							v = long(submittedValue)
						elif f.getFieldType()=="DATETIME":
							#v = strptime(submittedValue, "%d/%m/%Y")
							v = StringToDate(submittedValue, '%Y-%m-%d %H:%M')
						elif f.getFieldType()=="ATTACHMENT" and process_attachments:
							if isinstance(submittedValue, FileUpload):
								filename=submittedValue.filename
								current_files=doc.getItem(fieldName)
								contenttype=''
								if filename!='':
									if current_files=='':
										current_files={}
									if filename in doc.objectIds():
										new_file="ERROR: "+filename+" already exists"
									else:
										doc.manage_addFile(filename, submittedValue)
										new_file=filename
										contenttype=getattr(doc,filename).getContentType()
									current_files[new_file]=contenttype
								v=current_files
						else:
							v = submittedValue
						doc.setItem(fieldName, v)
						
	security.declareProtected(READ_PERMISSION, 'getFieldRender')
	def getFieldRender(self,doc,field,editmode,creation=False, request=None):
		"""Rendering the field
		"""
		mode = field.getFieldMode()
		fieldName = field.id
		
		if doc is None:
			target = self
		else:
			target = doc
			
		# compute the value
		if mode=="EDITABLE":
			if doc is None:
				if request is None:
					fieldValue = ""
				else:
					fieldValue = request.get(fieldName)
					if field.getFieldType()=="DATETIME" and not (fieldValue=='' or fieldValue is None):
						fieldValue = StringToDate(fieldValue, '%Y-%m-%d %H:%M')
			else:
				fieldValue = doc.getItem(fieldName)

		if mode=="DISPLAY" or mode=="COMPUTED":
			try:
				#fieldValue = RunFormula(doc, field.getFormula())
				fieldValue = self.runFormulaScript("field_"+self.id+"_"+field.id+"_formula", target, field.getFormula)
			except Exception:
				fieldValue = ""
		
		if mode=="CREATION":
			if creation:
				# Note: on creation, there is no doc, we use self as param
				# in formula
				#fieldValue = RunFormula(self, field.getFormula())
				fieldValue = self.runFormulaScript("field_"+self.id+"_"+field.id+"_formula", self, field.getFormula)
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
			selection=field.getProperSelectionList(target)
			)


	security.declareProtected(READ_PERMISSION, 'displayDocument')
	def displayDocument(self,doc,editmode=False, creation=False, subform=False, request=None):
		"""display the document using the form's layout
		"""
		html_content = self.getField('FormLayout').get(self, mimetype='text/html')
		html_content = html_content.replace('\n', '')

		# remove the hidden content
		for hidewhen in self.getHidewhenFormulas():
			hidewhenName = hidewhen.id
			try:
				#result = RunFormula(doc, hidewhen.getFormula())
				result = self.runFormulaScript("hidewhen_"+self.id+"_"+hidewhen.id+"_formula", doc, hidewhen.getFormula)
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
		if editmode and not subform:
			html_content = "<input type='hidden' name='Form' value='"+self.getFormName()+"' />" + html_content

		# insert the fields with proper value and rendering
		for field in self.getFields():
			fieldName = field.id
			html_content = html_content.replace('<span class="plominoFieldClass">'+fieldName+'</span>', self.getFieldRender(doc, field, editmode, creation, request=request))
		
		# insert subforms
		for subformname in self.getSubforms():
			subformrendering=self.getParentDatabase().getForm(subformname).displayDocument(doc, editmode, creation, subform=True)
			html_content = html_content.replace('<span class="plominoSubformClass">'+subformname+'</span>', subformrendering)
		
		# insert the actions
		for action in self.getActions(doc, False):
			actionName = action.id
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
	def formLayout(self, request=None):
		"""return the form layout in edit mode (used to compose a new
		document)
		"""
		return self.displayDocument(None, True, True, request=request)


	security.declareProtected(READ_PERMISSION, 'searchDocuments')
	def searchDocuments(self,REQUEST):
		"""search documents in the view matching the submitted form fields values
		"""
		db = self.getParentDatabase()
		searchview = db.getView(self.getSearchView())
		index = db.getIndex()
		query={'PlominoViewFormula_'+searchview.getViewName() : True}
		
		for f in self.getFields(includesubforms=True):
			fieldName = f.id
			submittedValue = REQUEST.get(fieldName)
			if submittedValue is not None:
				if not submittedValue=='':
					# if non-text field, convert the value
					if f.getFieldType()=="NUMBER":
						v = long(submittedValue)
					elif f.getFieldType()=="DATETIME":
						#v = strptime(submittedValue, "%d/%m/%Y")
						#v = StringToDate(submittedValue, '%Y-%m-%d %H:%M')
						v = submittedValue
					else:
						v = submittedValue
					query[fieldName]=v
		results=index.dbsearch(query, None)
		return self.OpenForm(searchresults=results)
		
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
					#result = RunFormula(target, obj_a.getHidewhen())
					result = self.runFormulaScript("action_"+self.id+"_"+obj_a.id+"_hidewhen", target, obj_a.getHidewhen)
				except Exception:
					#if error, we hide anyway
					result = True
				if not result:
					filtered.append(obj_a)
			else:
				filtered.append(obj_a)
		return filtered
	
	security.declarePublic('at_post_edit_script')
	def at_post_edit_script(self):
		"""clean up the layout before saving
		"""
		self.cleanFormulaScripts("form_"+self.id)
		# clean up the form layout field
		html_content = self.getField('FormLayout').get(self, mimetype='text/html')
		regexp = '<span class="plominoFieldClass"></span>'
		html_content = re.sub(regexp,'', html_content)
		regexp = '<span class="plominoActionClass"></span>'
		html_content = re.sub(regexp,'', html_content)
		regexp = '<span class="plominoHidewhenClass"></span>'
		self.setFormLayout(html_content)

	security.declarePublic('validateInputs')
	def validateInputs(self, REQUEST):
		errors=[]
		for f in self.getFields(includesubforms=True):
			fieldname = f.id
			fieldtype = f.getFieldType()
			submittedValue = REQUEST.get(fieldname)
			
			# STEP 1: check mandatory fields
			if submittedValue is None or submittedValue=='':
				if f.getMandatory()==True:
					errors.append(fieldname+" is mandatory")
			else:
				# STEP 2: check data types
				if fieldtype=="NUMBER":
					try:
						v = long(submittedValue)
					except:
						errors.append(fieldname+" must be a number (submitted value was: "+submittedValue+")")
				if fieldtype=="DATETIME":
					try:
						v = StringToDate(submittedValue, '%Y-%m-%d %H:%M')
					except:
						errors.append(fieldname+" must be a date/time (submitted value was: "+submittedValue+")")
		
		# STEP 3: check validation formula
		tmp = TemporaryDocument(self.getParentDatabase(), self, REQUEST)
		for f in self.getFields(includesubforms=True):
			formula = f.getValidationFormula()
			if not formula=='':
				s=''
				try:
					s = self.runFormulaScript("field_"+self.id+"_"+f.id+"_ValidationFormula", tmp, f.getValidationFormula)
				except:
					pass
				if not s=='':
					errors.append(s)
								
		return errors
	
	security.declarePublic('notifyError')
	def notifyErrors(self, errors):
		msg="<html><body><script>"
		for e in errors:
			msg=msg+"alert('"+e+"');"
		msg=msg+"history.back()</script></body></html>"
		return msg
	
registerType(PlominoForm, PROJECTNAME)
# end of class PlominoForm

##code-section module-footer #fill in your manual code here
	
##/code-section module-footer




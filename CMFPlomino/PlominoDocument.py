# -*- coding: utf-8 -*-
#
# File: PlominoDocument.py
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
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFPlomino.config import *


##code-section module-header #fill in your manual code here
from Products.Archetypes.public import *
from AccessControl import Unauthorized
from time import strptime
from DateTime import DateTime
from Products.CMFPlomino.PlominoUtils import StringToDate, sendMail
from Acquisition import *
from ZPublisher.HTTPRequest import FileUpload

import PlominoDatabase
import PlominoView

import logging
logger=logging.getLogger("Plomino")
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoDocument_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
	schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoDocument(ATFolder):
	"""Plomino Document
	"""
	security = ClassSecurityInfo()
	__implements__ = (getattr(ATFolder,'__implements__',()),)

	# This name appears in the 'add' box
	archetype_name = 'PlominoDocument'

	meta_type = 'PlominoDocument'
	portal_type = 'PlominoDocument'
	allowed_content_types = []
	filter_content_types = 1
	global_allow = 0
	content_icon = 'PlominoDocument.gif'
	immediate_view = 'base_view'
	default_view = 'checkBeforeOpenDocument'
	suppl_views = ()
	typeDescription = "PlominoDocument"
	typeDescMsgId = 'description_edit_plominodocument'


	actions =  (


	   {'action': "string:${object_url}/checkBeforeOpenDocument",
		'category': "object",
		'id': 'view',
		'name': 'View',
		'permissions': ("View",),
		'condition': 'python:1'
	   },


	   {'action': "string:${object_url}/EditDocument",
		'category': "object",
		'id': 'edit',
		'name': 'Edit',
		'permissions': (EDIT_PERMISSION,),
		'condition': 'python:1'
	   },
	   
	   {'action': "string:${object_url}/DocumentProperties",
		'category': "object",
		'id': 'metadata',
		'name': 'Properties',
		'permissions': (DESIGN_PERMISSION,),
		'condition': 'python:1'
	   },


	)

	_at_rename_after_creation = True

	schema = PlominoDocument_schema

	##code-section class-header #fill in your manual code here
	##/code-section class-header

	# Methods

	security.declarePublic('checkBeforeOpenDocument')
	def checkBeforeOpenDocument(self):
		"""check read permission and open view  NOTE: if READ_PERMISSION
		set on the 'view' action itself, it causes error 'maximum
		recursion depth exceeded' if user hasn't permission
		"""
		if self.checkUserPermission(READ_PERMISSION):
			return self.OpenDocument()
		else:
			raise Unauthorized, "You cannot read this content"

	security.declarePublic('__init__')
	def __init__(self,oid,**kw):
		"""initialization
		"""
		ATFolder.__init__(self, oid, **kw)
		self.items={}
		self.views_dict={}
		
	security.declarePublic('setItem')
	def setItem(self,name,value):
		"""
		"""
		items = self.items
		items[name] = value
		self.items = items

	security.declarePublic('getItem')
	def getItem(self,name):
		"""
		"""
		if(self.items.has_key(name)):
			return self.items[name]
		else:
			return ''
	
	security.declarePublic('getItemType')
	def getItemClassname(self,name):
		"""
		"""
		return self.getItem(name).__class__.__name__

	security.declarePublic('hasItem')
	def hasItem(self,name):
		"""
		"""
		return self.items.has_key(name)

	security.declarePublic('removeItem')
	def removeItem(self,name):
		"""
		"""
		if(self.items.has_key(name)):
			items = self.items
			del items[name]
			self.items = items

	security.declarePublic('getItems')
	def getItems(self):
		"""
		"""
		return self.items.keys()

	security.declarePublic('getRenderedItem')
	def getRenderedItem(self, itemname, form=None, convertattachments=False):
		""" return the item value rendered according the field defined in the given form
		(use default doc form if None)
		"""
		db=self.getParentDatabase()
		if form is None:
			form = db.getForm(self.Form)
		field=form.getFormField(itemname)
		if not field is None:
			content = form.getFieldRender(self, field, False)
			if field.getFieldType()=='ATTACHMENT':
				content = content+' '+db.getIndex().convertFileToText(self,itemname)
			return content
		else:
			return ''

	security.declarePublic('getParentDatabase')
	def getParentDatabase(self):
		"""
		"""
		return self.getParentNode()

	security.declarePublic('isAuthor')
	def isAuthor(self):
		"""
		"""
		return self.getParentDatabase().isCurrentUserAuthor(self)

	security.declareProtected(EDIT_PERMISSION, 'delete')
	def delete(self,REQUEST=None):
		"""delete the current doc
		"""
		db = self.getParentDatabase()
		db.deleteDocument(self)
		if not REQUEST is None:
			return_url = REQUEST.get('returnurl')
			REQUEST.RESPONSE.redirect(return_url)

	security.declareProtected(EDIT_PERMISSION, 'saveDocument')
	def saveDocument(self,REQUEST, creation=False):
		"""save a document using the form submitted content
		"""
		db = self.getParentDatabase()
		form = db.getForm(REQUEST.get('Form'))
		
		errors=form.validateInputs(REQUEST)
		if len(errors)>0:
			return form.notifyErrors(errors)
		
		self.setItem('Form', form.getFormName())

		# process editable fields (we read the submitted value in the request)
		try:
			for f in form.getFields(includesubforms=True):
				mode = f.getFieldMode()
				fieldName = f.id
				if mode=="EDITABLE":
					submittedValue = REQUEST.get(fieldName)
					if submittedValue is not None:
						if submittedValue=='':
							self.removeItem(fieldName)
						else:
							# if non-text field, convert the value
							if f.getFieldType()=="NUMBER":
								v = long(submittedValue)
							elif f.getFieldType()=="DATETIME":
								#v = strptime(submittedValue, "%d/%m/%Y")
								v = StringToDate(submittedValue, '%Y-%m-%d %H:%M')
							elif f.getFieldType()=="ATTACHMENT":
								if isinstance(submittedValue, FileUpload):
									filename=submittedValue.filename
									current_files=self.getItem(fieldName)
									contenttype=''
									if filename!='':
										if current_files=='':
											current_files={}
										if filename in self.objectIds():
											new_file="ERROR: "+filename+" already exists"
										else:
											self.manage_addFile(filename, submittedValue)
											new_file=filename
											contenttype=getattr(self,filename).getContentType()
										current_files[new_file]=contenttype
									v=current_files
							else:
								v = submittedValue
							self.setItem(fieldName, v)
		except Exception, e:
			return "<html><body><script>alert('"+str(e)+"'); history.back()</script></body></html>"

		# refresh computed values, run onSave, reindex
		self.save(form, creation)
		
		REQUEST.RESPONSE.redirect(self.absolute_url())

	security.declareProtected(EDIT_PERMISSION, 'save')
	def save(self, form=None, creation=False):
		"""refresh values according form, and reindex the document
		"""
		# we process computed fields (refresh the value)
		# TODO: manage computed fields dependencies
		if form is None:
			form = self.getForm()
		
		db=self.getParentDatabase()
		for f in form.getFields(includesubforms=True):
			mode = f.getFieldMode()
			fieldName = f.id
			if mode=="COMPUTED" or (mode=="CREATION" and creation):
				try:
					#result = RunFormula(self, f.getFormula())
					result = self.runFormulaScript("field_"+f.getParentNode().id+"_"+f.id+"_formula", self, f.getFormula)
				except Exception:
					result = "Error"
				self.setItem(fieldName, result)
			else:
				# computed for display field are not stored
				pass
				
		# compute the document title
		try:
			#result = RunFormula(self, form.getDocumentTitle())
			result = self.runFormulaScript("form_"+form.id+"_title", self, form.getDocumentTitle)
		except Exception:
			result = "Document"
		self.setTitle(result)
		
		# update the Plomino_Authors field with the current user name
		authors = self.getItem('Plomino_Authors')
		name = db.getCurrentUser().getUserName()
		if authors == '':
			authors = []
			authors.append(name)
		elif name in authors:
			pass
		else:
			authors.append(name)
		self.setItem('Plomino_Authors', authors)

		# execute the onSaveDocument code of the form
		try:
			#RunFormula(self, form.getOnSaveDocument())
			self.runFormulaScript("form_"+form.id+"_onsave", self, form.getOnSaveDocument)
		except Exception:
			pass
			
		# update index
		db.getIndex().indexDocument(self)
		# update portal_catalog
		self.reindexObject()
		
	security.declareProtected(READ_PERMISSION, 'openWithForm')
	def openWithForm(self,form,editmode=False):
		"""display the document using the given form's layout - first,
		check if the user has proper access rights
		"""
		if editmode:
			db = self.getParentDatabase()
			if not db.isCurrentUserAuthor(self):
				raise Unauthorized, "You cannot edit this document."

		# execute the onOpenDocument code of the form
		try:
			if not form.getOnOpenDocument()=="":
				#RunFormula(self, form.getOnOpenDocument())
				self.runFormulaScript("form_"+form.id+"_onopen", self, form.getOnOpenDocument)
		except Exception:
			pass

		# we use the specified form's layout
		html_content = form.displayDocument(self, editmode)
		return html_content

	security.declareProtected(EDIT_PERMISSION, 'editWithForm')
	def editWithForm(self,form):
		"""
		"""
		return self.openWithForm(form, True)

	security.declarePublic('send')
	def send(self,recipients,title,formname=''):
		"""Send current doc by mail
		"""
		db = self.getParentDatabase()
		if formname=='':
			formname = self.getItem('Form')
		form = db.getForm(formname)
		message = self.openWithForm(form)
		sendMail(db, recipients, title, message)

	security.declarePublic('getForm')
	def getForm(self):
		"""try to acquire the formname using the parent view form formula,
		if nothing, use the Form item
		"""
		if hasattr(self, 'evaluateViewForm'):
			formname = self.evaluateViewForm(self)
			if formname == "" or formname is None:
				formname = self.getItem('Form')
		else:
			formname = self.getItem('Form')
		return self.getParentDatabase().getForm(formname)

	security.declarePrivate('manage_afterClone')
	def manage_afterClone(self,item):
		"""after cloning
		"""
		# changed from BaseFolder to ATFolder because now inherits fron ATFolder
		ATFolder.manage_afterClone(self, item)

	security.declarePublic('__getattr__')
	def __getattr__(self,name):
		"""Overloads getattr to return item values as attibutes
		"""
		if(self.items.has_key(name)):
			return self.items[name]
		else:
			#raise AttributeError, name
			return BaseObject.__getattr__(self, name)

	security.declareProtected(READ_PERMISSION, 'isSelectedInView')
	def isSelectedInView(self,viewname):
		"""
		"""
		db = self.getParentDatabase()
		v = db.getView(viewname)
		try:
			#result = RunFormula(self, v.SelectionFormula())
			result = self.runFormulaScript("view_"+v.id+"_selection", self, v.SelectionFormula)
		except Exception:
			result = False
		return result

	security.declareProtected(READ_PERMISSION, 'computeColumnValue')
	def computeColumnValue(self,viewname,columnname):
		"""
		"""
		db = self.getParentDatabase()
		v = db.getView(viewname)
		try:
			c = v.getColumn(columnname)
			#result = RunFormula(self, c.Formula())
			result = self.runFormulaScript("column_"+v.id+"_"+c.id+"_formula", self, c.Formula)
		except Exception:
			result = None
		return result

	security.declareProtected(EDIT_PERMISSION, 'deleteAttachment')
	def deleteAttachment(self,REQUEST):
		"""remove file object and update corresponding item value
		"""
		fieldname=REQUEST.get('field')
		filename=REQUEST.get('filename')
		if filename in self.objectIds():
			self.manage_delObjects(filename)
		current_files=self.getItem(fieldname)
		if current_files.has_key(filename):
			del current_files[filename]
			self.setItem(fieldname, current_files)
			
		REQUEST.RESPONSE.redirect(self.absolute_url()+"/EditDocument")
	
	security.declarePublic('SearchableText')
	def SearchableText(self):
		values=[]
		index_attachments=self.getParentDatabase().getIndexAttachments()
		for itemname in self.items.keys():
			try:
				v=str(self.getRenderedItem(itemname,form=None, convertattachments=index_attachments))
				values.append(v)
			except:
				pass
		return ' '.join(values)
			
		
registerType(PlominoDocument, PROJECTNAME)
# end of class PlominoDocument

##code-section module-footer #fill in your manual code here
##/code-section module-footer




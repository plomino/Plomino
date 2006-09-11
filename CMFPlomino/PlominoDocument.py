#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from time import strptime
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

from Acquisition import *
from zLOG import LOG, ERROR

from Products.CMFPlomino.config import *

import PlominoDatabase
import PlominoView
		
class PlominoDocument(Implicit, BaseFolder):
	""" Plomino Document """
	schema = BaseFolderSchema
	
	content_icon = "PlominoDocument.gif"
	
	actions = (
		{
		'id': 'view',
		'name': 'View',
		'action': 'string:${object_url}/OpenDocument',
		},
		{
		'id': 'edit',
		'name': 'Edit',
		'action': "python:here.navigationParent(here)+'/'+here.id+'/EditDocument'",
		'permissions': (DESIGN_PERMISSION)
		},)
	
	security = ClassSecurityInfo()
	
	security.declareProtected(READ_PERMISSION, 'OpenDocument')

	def __init__(self, oid, **kw):
		BaseFolder.__init__(self, oid, **kw)
		self.items={}
		self._parentdatabase=None
		
	def setItem(self, name, value):
		items = self.items
		items[name] = value
		self.items = items
	
	def getItem(self, name):
		if(self.items.has_key(name)):
			return self.items[name]
		else:
			return ''
	
	def hasItem(self, name):
		return self.items.has_key(name)
		
	def removeItem(self, name):
		if(self.items.has_key(name)):
			items = self.items
			del items[name]
			self.items = items
			
	def getItems(self):
		return self.items.keys()
    
	def getParentDatabase(self):
		if aq_parent(self) is not None:
			return self.getParentNode()
		else:
			return self._parentdatabase
		
	def setParentDatabase(self, db):
		self._parentdatabase = db
		
	def isAuthor(self):
		return self.getParentDatabase().isCurrentUserAuthor(self)
	
	security.declareProtected(EDIT_PERMISSION, 'delete')
	def delete(self, REQUEST):
		""" delete the current doc """
		return_url = REQUEST.get('returnurl')
		db = self.getParentDatabase()
		db.deleteDocument(self)
		REQUEST.RESPONSE.redirect(return_url) 
		
	security.declareProtected(EDIT_PERMISSION, 'saveDocument')
	def saveDocument(self, REQUEST):
		""" save a document using the form submitted content """
		db = self.getParentDatabase()
		form = db.getForm(REQUEST.get('Form'))
		self.setItem('Form', form.getFormName())
		
		# for editable field, we read the submitted value in the request,
		# for computed fields we refresh the value
		for field in form.getFields():
			f = field.getObject()
			mode = f.getFieldMode()
			fieldName = f.Title()
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
							# TO BE MODIFIED: support different date/time format
							v = strptime(submittedValue, "%d/%m/%Y")
						else:
							v = submittedValue
						self.setItem(fieldName, v)
			elif mode=="COMPUTED":
				# plominoDocument is the reserved name used in field formulae
				plominoDocument = self
				try:
					exec "result = " + f.getFormula()
				except Exception:
					result = "Error"
				self.setItem(fieldName, result)
			else:
				# computed for display field are not stored
				pass
				
		# update the Plomino_Authors field with the current user name
		authors = self.getItem('Plomino_Authors')
		name = db.getCurrentUser().getUserName()
		if authors == '':
			authors = []
		elif name in authors:
			pass
		else:
			authors.append(name)
		self.setItem('Plomino_Authors', authors)
		
		# execute the onSaveDocument code of the form
		# plominoDocument is the reserved name used in events code
		plominoDocument = self
		try:
			exec form.getOnSaveDocument()
		except Exception:
			pass
			
		db.getIndex().indexDocument(self)
		REQUEST.RESPONSE.redirect(self.absolute_url())
	
	security.declareProtected(READ_PERMISSION, 'getFieldRender')
	def getFieldRender(self, form, field, editmode):
		mode = field.getFieldMode()
		fieldName = field.Title()
		if mode=="EDITABLE":
			fieldValue = self.getItem(fieldName)
			if editmode:
				fieldType = field.FieldType
				try:
					exec "pt = self."+fieldType+"FieldEdit"
				except Exception:
					pt = self.DefaultFieldEdit
				return pt(fieldname=fieldName, fieldvalue=fieldValue)
			else:	
				return fieldValue
			
		if mode=="DISPLAY" or mode=="COMPUTED":
			# plominoDocument is the reserved name used in field formulae
			plominoDocument = self
			try:
				exec "result = " + field.getFormula()
			except Exception:
				result = "Error"
			return result
	
	security.declareProtected(READ_PERMISSION, 'openWithForm')
	def openWithForm(self, form, editmode=False):
		""" display the document using the given form's layout """
		# first, check if the user has proper access rights
		if editmode:
			db = self.getParentDatabase()
			if not db.isCurrentUserAuthor(self):
				raise Unauthorized, "You cannot edit this document."
		
		# execute the onOpenDocument code of the form
		# plominoDocument is the reserved name used in events code
		plominoDocument = self
		try:
			exec form.getOnOpenDocument()
		except Exception:
			pass
		
		# we use the specified form's layout
		html_content = form.displayDocument(self, editmode)
		return html_content
	
	security.declareProtected(EDIT_PERMISSION, 'editWithForm')
	def editWithForm(self, form):
		return self.openWithForm(form, True)
		
	def send(self, recipients, title, formname=''):
		host = getToolByName(self, 'MailHost')
		db = self.getParentDatabase()
		if formname=='':
			formname = self.getItem('Form')
		form = db.getForm(formname)
		message = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
		message = message + "<html>"
		message = message + self.openWithForm(form)
		message = message + "</html>"
		sender = db.getCurrentUser().getProperty("email")
		mail = "From: "+sender+'\n'
		mail = mail + "To: "+recipients+'\n'
		mail = mail + "Subject: "+ title + '\n'
		mail = mail + "Content-type: text/html\n\n"
		mail = mail + message
		#host.send(message, recipients, sender, title)
		host.send(mail)
	
	def getForm(self):
		""" try to acquire the formname using the parent view form formula, if nothing, use the Form item """
		if hasattr(self, 'evaluateViewForm'):
			formname = self.evaluateViewForm(self)
			if formname == "":
				formname = self.getItem('Form')
		else:
			formname = self.getItem('Form')
		return self.getParentDatabase().getForm(formname)
	
	security.declarePrivate('manage_afterClone')
	def manage_afterClone(self, item):
		BaseFolder.manage_afterClone(self, item)
        
	security.declarePrivate('manage_beforeDelete')
	def manage_beforeDelete(self, item, container):
		db = self.getParentDatabase()
		db.getIndex().unindexDocument(self)
		BaseFolder.manage_beforeDelete(self, item, container)
		
	def __getattr__(self, name):
		"""Overloads getattr to return item values, view selection formula evaluation
		   and views columns values as attibutes (so ZCatalog can read them)
		"""
		if(name.startswith("PlominoViewFormula_")):
			param = name.split('_')
			viewname=param[1]
			return self.isSelectedInView(viewname)
		elif(name.startswith("PlominoViewColumn_")):
			param = name.split('_')
			viewname=param[1]
			columnname=param[2]
			return self.computeColumnValue(viewname, columnname)
		else:
			if(self.items.has_key(name)):
				return self.items[name]
			else:
				return BaseFolder.__getattr__(self, name)
        
	security.declareProtected(READ_PERMISSION, 'isSelectedInView')
	def isSelectedInView(self, viewname):
		db = self.getParentDatabase()
		v = db.getView(viewname)
		# plominoDocument is the reserved name used in selection formulae
		plominoDocument = self
		try:
			exec "result = " + v.getSelectionFormula()
		except Exception:
			result = False
		return result
		
	security.declareProtected(READ_PERMISSION, 'isSelectedInView')
	def computeColumnValue(self, viewname, columnname):
		db = self.getParentDatabase()
		v = db.getView(viewname)
		# plominoDocument is the reserved name used in column formulae
		plominoDocument = self
		try:
			exec "result = " + v.getColumn(columnname).getFormula()
		except Exception:
			result = False
		return result
		
registerType(PlominoDocument, PROJECTNAME)

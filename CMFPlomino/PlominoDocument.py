#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
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
		'action': 'string:${object_url}/EditDocument',
		'permissions': (EDIT_PERMISSION)
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
		
	def getItems(self):
		return self.items.keys()
    
	def getParentDatabase(self):
		if aq_parent(self) is not None:
			return self.getParentNode()
		else:
			return self._parentdatabase
		
	def setParentDatabase(self, db):
		self._parentdatabase = db
	
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
				self.setItem(fieldName, submittedValue)
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
		membershiptool = getToolByName(self, 'portal_membership')
		name = membershiptool.getAuthenticatedMember().getUserName()
		if authors == '':
			authors = []
		elif name in authors:
			pass
		else:
			authors.append(name)
		LOG('Plomino', ERROR, name)
		self.setItem('Plomino_Authors', authors)
		
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
		html_content = form.getField('Layout').get(form, mimetype='text/html')
		if editmode:
			html_content = "<input type='hidden' name='Form' value='"+form.getFormName()+"' />" + html_content
			
		for field in form.getFields():
			fieldName = field.Title
			html_content = html_content.replace('#'+fieldName+'#', self.getFieldRender(form, field.getObject(), editmode))
			
		for action in form.getActions():
			actionName = action.Title
			actionDisplay = action.getObject().ActionDisplay
			try:
				exec "pt = self."+actionDisplay+"Action"
			except Exception:
				pt = self.LINKAction
			action_render = pt(plominoaction=action, plominotarget=self)
			html_content = html_content.replace('#Action:'+actionName+'#', action_render)
			
		return html_content
	
	security.declareProtected(EDIT_PERMISSION, 'editWithForm')
	def editWithForm(self, form):
		return self.openWithForm(form, True)
	
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
		   and views columns values as attibutes
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

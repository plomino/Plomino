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
from ZPublisher import xmlrpc
from zLOG import LOG, ERROR

from Products.CMFPlomino.config import PROJECTNAME

import PlominoDatabase
import PlominoView
        
class PlominoDocument(Implicit, BaseFolder):
	""" Plomino Document """
	schema = BaseFolderSchema
	
	content_icon = "PlominoDocument.gif"
	
	__allow_access_to_unprotected_subobjects__ = 1
	
	actions = (
		{
		'id': 'view',
		'name': 'View',
		'action': 'string:${object_url}/OpenDocument',
		'permissions': (CMFCorePermissions.View,)
		},
		{
		'id': 'edit',
		'name': 'Edit',
		'action': 'string:${object_url}/EditDocument',
		'permissions': (CMFCorePermissions.View,)
		},)
		
	security = ClassSecurityInfo()
        
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
	
	security.declareProtected(CMFCorePermissions.View, 'evaluate')
	def evaluate(self, formula):
		try:
			exec "result = " + formula
		except Exception:
			result = "Error"
		return result

	security.declareProtected(CMFCorePermissions.View, 'saveDocument')
	def saveDocument(self, REQUEST):
		""" save a document using the form submitted content """
		db = self.getParentDatabase()
		form = db.getForm(REQUEST.get('Form'))
		self.setItem('Form', form.getFormName())
		
		for field in form.getFields():
			fieldName = field.Title
			submittedValue = REQUEST.get(fieldName)
			self.setItem(fieldName, submittedValue)
		
		db.getIndex().indexDocument(self)
		
		REQUEST.RESPONSE.redirect('./OpenDocument')
	
	security.declareProtected(CMFCorePermissions.View, 'openWithForm')
	def openWithForm(self, form):
		""" display the document using the given form's layout """
		html_content = form.getField('Layout').get(form, mimetype='text/html')
		for field in form.getFields():
			fieldName = field.Title
			html_content = html_content.replace('#'+fieldName+'#', self.getItem(fieldName))
			
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
		
	security.declareProtected(CMFCorePermissions.View, 'editWithForm')
	def editWithForm(self, form):
		""" edit the document using the given form's layout """
		html_content = form.getField('Layout').get(form, mimetype='text/html')
			
		for field in form.getFields():
			fieldName = field.Title
			fieldValue = self.getItem(fieldName)
			fieldType = field.getObject().FieldType
			try:
				exec "pt = self."+fieldType+"FieldEdit"
			except Exception:
				pt = self.DefaultFieldEdit
			field_render = pt(fieldname=fieldName, fieldvalue=fieldValue)
			html_content = html_content.replace('#'+fieldName+'#', field_render)
			
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
        
	security.declareProtected(CMFCorePermissions.View, 'isSelectedInView')
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
		
	security.declareProtected(CMFCorePermissions.View, 'isSelectedInView')
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

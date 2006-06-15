#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo

from Products.CMFPlomino.config import PROJECTNAME

class PlominoDocument(BaseFolder):
	""" Plomino Document """
	schema = BaseFolderSchema
	
	content_icon = "PlominoDocument.gif"
	
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
		return self.getParentNode()
	
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
			
registerType(PlominoDocument, PROJECTNAME)
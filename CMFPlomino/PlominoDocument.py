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
		'id': 'OpenDocument',
		'name': 'Open',
		'action': 'string:${object_url}/OpenDocument',
		'permissions': (CMFCorePermissions.View,)
		},
		{
		'id': 'EditDocument',
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
		return self.items[name]
		
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
			
registerType(PlominoDocument, PROJECTNAME)
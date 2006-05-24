#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.Archetypes.utils import make_uuid

from Products.CMFPlomino.config import *

import PlominoDocument

class PlominoForm(BaseFolder):
	""" Plomino Form """
	schema = BaseFolderSchema + Schema((
		StringField('Description', widget=TextAreaWidget(label='Description')),
		TextField('Layout', widget=RichWidget(label='Form layout'))
		))
	
	content_icon = "PlominoForm.gif"
	
	actions = (
		{
		'id': 'test',
		'name': 'Test Form',
		'action': 'string:${object_url}/OpenForm',
		'permissions': (CMFCorePermissions.View,)
		},)
		
	security = ClassSecurityInfo()
	
	security.declareProtected(CREATE_PERMISSION, 'createDocument')
	def createDocument(self, REQUEST):
		""" create a document using the forms submitted content """
		db = self.getParentDatabase()
		doc = db.createDocument()
		doc.setTitle( doc.id )
		doc.setItem('Form', self.getFormName())
	
		for field in self.getFields():
			fieldName = field.Title
			submittedValue = REQUEST.get(fieldName)
			doc.setItem(fieldName, submittedValue)
		
		REQUEST.RESPONSE.redirect('../'+doc.id+'/OpenDocument')
		
	def getFields(self):
		return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoField']})
		
	def getFormName(self):
		return self.Title()
		
	def getParentDatabase(self):
		return self.getParentNode()
	
	security.declareProtected(CMFCorePermissions.View, 'formLayout')
	def formLayout(self):
		""" return the form layout in edit mode """
		html_content = self.getField('Layout').get(self, mimetype='text/html')
			
		for field in self.getFields():
			fieldName = field.Title
			fieldValue = ''
			fieldType = field.getObject().FieldType
			try:
				exec "pt = self."+fieldType+"FieldEdit"
			except Exception:
				pt = self.DefaultFieldEdit
			field_render = pt(fieldname=fieldName, fieldvalue=fieldValue)
			html_content = html_content.replace('#'+fieldName+'#', field_render)
		
		return html_content
		
registerType(PlominoForm, PROJECTNAME)
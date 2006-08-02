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
from zLOG import LOG, ERROR

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
		'id': 'compose',
		'name': 'Compose',
		'action': 'string:${object_url}/OpenForm',
		'permissions': (CREATE_PERMISSION)
		},)
		
	security = ClassSecurityInfo()
	
	security.declareProtected(CREATE_PERMISSION, 'createDocument')
	def createDocument(self, REQUEST):
		""" create a document using the forms submitted content """
		db = self.getParentDatabase()
		doc = db.createDocument()
		doc.setTitle( doc.id )
		doc.setItem('Form', self.getFormName())
		doc.saveDocument(REQUEST)
		
	def getFields(self):
		return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoField']})
	
	def getFormName(self):
		""" return the form name """
		return self.Title()
		
	def getParentDatabase(self):
		return self.getParentNode()
	
	def formLayout(self):
		""" return the form layout in edit mode """
		html_content = self.getField('Layout').get(self, mimetype='text/html')
		html_content = "<input type='hidden' name='Form' value='"+self.getFormName()+"' />" + html_content
		
		for field in self.getFields():
			fieldName = field.Title
			fieldValue = ''
			f = field.getObject()
			mode = f.getFieldMode()
			fieldType = f.FieldType
			if mode=='EDITABLE':
				try:
					exec "pt = self."+fieldType+"FieldEdit"
				except Exception:
					pt = self.DefaultFieldEdit
				field_render = pt(fieldname=fieldName, fieldvalue=fieldValue)
			else:
				# plominoDocument is the reserved name used in field formulae
				# we set it to None, so formulae dependent from plominoDocument
				# will return null, and other ones will be computed
				plominoDocument = None
				try:
					exec "field_render = " + field.getFormula()
				except Exception:
					field_render = ""
			html_content = html_content.replace('#'+fieldName+'#', field_render)
		
		for action in self.getActions():
			actionName = action.Title
			actionDisplay = action.getObject().ActionDisplay
			try:
				exec "pt = self."+actionDisplay+"Action"
			except Exception:
				pt = self.LINKAction
			action_render = pt(plominoaction=action, plominotarget=self)
			html_content = html_content.replace('#Action:'+actionName+'#', action_render)
			
		return html_content
		
	def getActions(self):
		return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoAction']})
		
	def at_post_edit_script(self):
		db = self.getParentDatabase()
		db.declareDesign('forms', self.getFormName(), self)
	
	def at_post_create_script(self):
		db = self.getParentDatabase()
		db.declareDesign('forms', self.getFormName(), self)
		
	security.declarePrivate('manage_beforeDelete')
	def manage_beforeDelete(self, item, container):
		db = self.getParentDatabase()
		db.undeclareDesign('forms', self.getFormName())
		BaseFolder.manage_beforeDelete(self, item, container)
		
registerType(PlominoForm, PROJECTNAME)
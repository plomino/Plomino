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

import re

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
	
	def getHidewhenFormulas(self):
		return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoHidewhen']})
	
	def getFormName(self):
		""" return the form name """
		return self.Title()
		
	def getParentDatabase(self):
		return self.getParentNode()
	
	security.declareProtected(READ_PERMISSION, 'getFieldRender')
	def getFieldRender(self, doc, field, editmode):
		mode = field.getFieldMode()
		fieldName = field.Title()
		if mode=="EDITABLE":
			if doc is None:
				fieldValue = ""
			else:
				fieldValue = doc.getItem(fieldName)
				
			if editmode:
				ptsuffix="Edit"
			else:
				ptsuffix="Read"
				
			fieldType = field.FieldType
			try:
				exec "pt = self."+fieldType+"Field"+ptsuffix
			except Exception:
				exec "pt = self.DefaultField"+ptsuffix
				
			return pt(fieldname=fieldName, fieldvalue=fieldValue, selection=field.getProperSelectionList())
			
		if mode=="DISPLAY" or mode=="COMPUTED":
			# plominoDocument is the reserved name used in field formulae
			plominoDocument = doc
			try:
				exec "result = " + field.getFormula()
			except Exception:
				result = "Error"
			return str(result)
	
	security.declareProtected(READ_PERMISSION, 'displayDocument')
	def displayDocument(self, doc, editmode=False):
		""" display the document using the form's layout """
		html_content = self.getField('Layout').get(self, mimetype='text/html')
		
		# remove the hiden content
		for hidewhen in self.getHidewhenFormulas():
			hidewhenName = hidewhen.Title
			# plominoDocument is the reserved name used in field formulae
			plominoDocument = doc
			try:
				exec "result = " + hidewhen.getObject().getFormula()
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
			html_content = html_content.replace('<span class="plominoFieldClass">'+fieldName+'</span>', self.getFieldRender(doc, field.getObject(), editmode))
			
		# insert the actions
		for action in self.getActions():
			actionName = action.Title
			actionDisplay = action.getObject().ActionDisplay
			try:
				exec "pt = self."+actionDisplay+"Action"
			except Exception:
				pt = self.LINKAction
			action_render = pt(plominoaction=action, plominotarget=doc)
			#html_content = html_content.replace('#Action:'+actionName+'#', action_render)
			html_content = html_content.replace('<span class="plominoActionClass">'+actionName+'</span>', action_render)
			
		return html_content
	
	def formLayout(self):
		""" return the form layout in edit mode (used to compose a new document) """
		return self.displayDocument(None, True)
		
	def getActions(self):
		return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoAction']})
		
	def at_post_edit_script(self):
		# declare the form in the db (useful if Title has changed)
		db = self.getParentDatabase()
		db.declareDesign('forms', self.getFormName(), self)
		# clean up the form layout field
		html_content = self.getField('Layout').get(self, mimetype='text/html')
		regexp = '<span class="plominoFieldClass"></span>'
		html_content = re.sub(regexp,'', html_content)
		regexp = '<span class="plominoActionClass"></span>'
		html_content = re.sub(regexp,'', html_content)
		regexp = '<span class="plominoHidewhenClass"></span>'
		self.setLayout(html_content)
		
	def at_post_create_script(self):
		db = self.getParentDatabase()
		db.declareDesign('forms', self.getFormName(), self)
		
	security.declarePrivate('manage_beforeDelete')
	def manage_beforeDelete(self, item, container):
		db = self.getParentDatabase()
		db.undeclareDesign('forms', self.getFormName())
		BaseFolder.manage_beforeDelete(self, item, container)
		
registerType(PlominoForm, PROJECTNAME)
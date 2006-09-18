#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.utils import make_uuid
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

import string

from Products.CMFPlomino.config import *
from zLOG import LOG, ERROR

from PlominoIndex import PlominoIndex
from PlominoAccessControl import PlominoAccessControl
        
class PlominoDatabase(BaseFolder, PlominoAccessControl):
	""" Plomino DB """
	
	schema = BaseFolderSchema + Schema(
		StringField('Description',
		widget=TextAreaWidget(label='Description')
		))
	
	content_icon = "PlominoDatabase.gif"
	
	security = ClassSecurityInfo()

	actions = (
		{
		'id': 'view',
		'name': 'View',
		'action': 'string:${object_url}/OpenDatabase',
		},
		{
		'id': 'forms',
		'name': 'Forms',
		'action': 'string:${object_url}/DatabaseForms',
		'permissions': (DESIGN_PERMISSION)
		},
		{
		'id': 'views',
		'name': 'Views',
		'action': 'string:${object_url}/DatabaseViews',
		'permissions': (DESIGN_PERMISSION)
		},
		{
		'id': 'acl',
		'name': 'ACL',
		'action': 'string:${object_url}/DatabaseACL',
		'permissions': (ACL_PERMISSION)
		},)
	
	#Cannot protect OpenDatabase because initializeACL fail (because 'view' is default access to obj)
	#so we test READ_PERMISSION in OpenDatabase template directly
	
	def __init__(self, oid, **kw):
		BaseFolder.__init__(self, oid, **kw)
		PlominoAccessControl.__init__(self)
		index = PlominoIndex()
		self._setObject(index.getId(), index)
		design = {}
		design['views'] = {}
		design['forms'] = {}
		self._design = design
		
	def at_post_create_script(self):
		self.initializeACL()
		
	def getForms(self):
		""" return the database forms list """
		return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoForm']})
		
	def getViews(self):
		""" return the database views list """
		return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoView']})
	
	def getForm(self, formname):
		""" return a PlominoForm """
		#f = self.getFolderContents(contentFilter = {'portal_type' : ['PlominoForm'], 'title' : ['fTest']})
		#return self._getOb(f[0].id)
		forms = self._design['forms']
		if forms.has_key(formname):
			f = forms[formname]
			if hasattr(f, '__of__'):
				f = f.__of__(self)
			return f
		else:
			return None
			
	def getView(self, viewname):
		""" return a PlominoView """
		#v = self.getFolderContents(contentFilter = {'portal_type' : ['PlominoView'], 'title' : viewname})
		#return self._getOb(v[0].id)
		views = self._design['views']
		if views.has_key(viewname):
			v = views[viewname]
			if hasattr(v, '__of__'):
				v = v.__of__(self)
			return v
		else:
			return None
		
	security.declareProtected(CREATE_PERMISSION, 'createDocument')
	def createDocument(self):
		""" create a unique ID and invoke PlominoDocument factory """
		newid = make_uuid()
		self.invokeFactory( type_name='PlominoDocument', id=newid)
		doc = self._getOb( newid )
		doc.setParentDatabase(self)
		return doc
		
	security.declareProtected(EDIT_PERMISSION, 'deleteDocument')
	def deleteDocument(self, doc):
		""" delete the document from database """
		# first, check if the user has proper access rights
		if not self.isCurrentUserAuthor(doc):
			raise Unauthorized, "You cannot edit this document."
		else:
			self.manage_delObjects(doc.id)
				
	def getIndex(self):
		""" return the database index """
		return self._getOb('plomino_index')
	
	security.declareProtected(DESIGN_PERMISSION, 'declareDesign')
	def declareDesign(self, design_type, design_name, design_obj):
		""" declare a design element """
		design = self._design
		elements = design[design_type]
		elements[design_name] = design_obj
		design[design_type] = elements
		self._design = design
	
	security.declareProtected(DESIGN_PERMISSION, 'undeclareDesign')
	def undeclareDesign(self, design_type, design_name):
		""" undeclare a design element """
		design = self._design
		elements = design[design_type]
		del elements[design_name]
		design[design_type] = elements
		self._design = design
		
registerType(PlominoDatabase, PROJECTNAME)
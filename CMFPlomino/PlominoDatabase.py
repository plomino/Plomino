#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import _checkPermission as checkPerm
from AccessControl.PermissionRole import rolesForPermissionOn
from Products.Archetypes.utils import make_uuid
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName

import string

from Products.CMFPlomino.config import *
from zLOG import LOG, ERROR

from PlominoIndex import PlominoIndex
        
class PlominoDatabase(BaseFolder):
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
	
	security.declareProtected(READ_PERMISSION, 'OpenDatabase')
	
	def __init__(self, oid, **kw):
		BaseFolder.__init__(self, oid, **kw)
		self.ACL_initialized=0
		index = PlominoIndex()
		self._setObject(index.getId(), index)
		design = {}
		design['views'] = {}
		design['forms'] = {}
		self._design = design
		
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
		
	def getRoles(self):
		""" return the database roles list """
		roles = self.valid_roles()
		return roles
		
	def getUsersForRight(self, role):
		""" return the users having the given Plomino access right """
		return self.users_with_local_role(role)
		
	def initializeACL(self):
		""" create the default Plomino access rights """
		self._addRole("PlominoReader")
		self.manage_role("PlominoReader", permissions=[
			READ_PERMISSION,
			CMFCorePermissions.View])
		self._addRole("PlominoAuthor")
		self.manage_role("PlominoAuthor", permissions=[
			READ_PERMISSION,
			EDIT_PERMISSION,
			REMOVE_PERMISSION,
			CREATE_PERMISSION,
			ADD_CONTENT_PERMISSION,
			CMFCorePermissions.View,
			CMFCorePermissions.ModifyPortalContent])
		self._addRole("PlominoEditor")
		self.manage_role("PlominoEditor", permissions=[
			READ_PERMISSION,
			EDIT_PERMISSION,
			REMOVE_PERMISSION,
			CREATE_PERMISSION,
			ADD_CONTENT_PERMISSION,
			CMFCorePermissions.View,
			CMFCorePermissions.ModifyPortalContent])
		self._addRole("PlominoDesigner")
		self.manage_role("PlominoDesigner", permissions=[
			READ_PERMISSION,
			EDIT_PERMISSION,
			REMOVE_PERMISSION,
			CREATE_PERMISSION,
			DESIGN_PERMISSION,
			ADD_CONTENT_PERMISSION,
			ADD_DESIGN_PERMISSION,
			CMFCorePermissions.View,
			CMFCorePermissions.ModifyPortalContent])
		self._addRole("PlominoManager")
		self.manage_role("PlominoManager", permissions=[
			READ_PERMISSION,
			EDIT_PERMISSION,
			REMOVE_PERMISSION,
			CREATE_PERMISSION,
			DESIGN_PERMISSION,
			ADD_CONTENT_PERMISSION,
			ADD_DESIGN_PERMISSION,
			ACL_PERMISSION,
			CMFCorePermissions.View,
			CMFCorePermissions.ModifyPortalContent])
		self.ACL_initialized=1

	def at_post_create_script(self):
		self.initializeACL()
    		
	def getRolesForPermission(self, perm, obj):
		if perm=='test':
			_ident_chars = string.ascii_letters + string.digits + "_"
			name_trans = filter(lambda c, an=_ident_chars: c not in an,
                    map(chr, range(256)))
			name_trans = string.maketrans(''.join(name_trans), '_' * len(name_trans))
			perm='CMFPlomino: Read documents'
			t = '_' + string.translate(perm, name_trans) + "_Permission"
			return getattr(self, t)
		if perm=='actions':
			portal_actions=getToolByName(self,'portal_actions')
			return portal_actions.listFilteredActionsFor(self)
		return rolesForPermissionOn(perm, obj)
	
	def checkUserPermission(self, perm, context):
		#if self.checkPermission(perm, context):
		if checkPerm(perm, context):
			return 1
		return 0
    
	security.declareProtected(ACL_PERMISSION, 'addACLEntry')
	def addACLEntry(self, REQUEST):
		""" add an entry in the ACL """
		user=REQUEST.get('newuser')
		accessright=REQUEST.get('accessright')
		self.manage_setLocalRoles(user, [accessright])
		REQUEST.RESPONSE.redirect('./DatabaseACL')

	security.declareProtected(ACL_PERMISSION, 'removeACLEntries')
	def removeACLEntries(self, REQUEST):
		""" remove entries in the ACL """
		users=REQUEST.get('users')
		self.manage_delLocalRoles(users)
		REQUEST.RESPONSE.redirect('./DatabaseACL')
	
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
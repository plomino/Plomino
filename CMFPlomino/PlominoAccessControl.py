#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import _checkPermission as checkPerm
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName

from Products.CMFPlomino.config import *
from zLOG import LOG, ERROR

        
class PlominoAccessControl:
	""" Plomino access control utilities """
	
	PLOMINO_PERMISSIONS = {
		"NoAccess" : [],
		"PlominoReader" : [
			READ_PERMISSION,
			CMFCorePermissions.View],
		"PlominoAuthor" : [
			READ_PERMISSION,
			EDIT_PERMISSION,
			REMOVE_PERMISSION,
			CREATE_PERMISSION,
			ADD_CONTENT_PERMISSION,
			CMFCorePermissions.View,
			CMFCorePermissions.AddPortalContent,
			CMFCorePermissions.ModifyPortalContent],
		"PlominoEditor" : [
			READ_PERMISSION,
			EDIT_PERMISSION,
			REMOVE_PERMISSION,
			CREATE_PERMISSION,
			ADD_CONTENT_PERMISSION,
			CMFCorePermissions.View,
			CMFCorePermissions.AddPortalContent,
			CMFCorePermissions.ModifyPortalContent],
		"PlominoDesigner" : [
			READ_PERMISSION,
			EDIT_PERMISSION,
			REMOVE_PERMISSION,
			CREATE_PERMISSION,
			DESIGN_PERMISSION,
			ADD_CONTENT_PERMISSION,
			ADD_DESIGN_PERMISSION,
			CMFCorePermissions.View,
			CMFCorePermissions.AddPortalContent,
			CMFCorePermissions.ModifyPortalContent],
		"PlominoManager" : [
			READ_PERMISSION,
			EDIT_PERMISSION,
			REMOVE_PERMISSION,
			CREATE_PERMISSION,
			DESIGN_PERMISSION,
			ADD_CONTENT_PERMISSION,
			ADD_DESIGN_PERMISSION,
			ACL_PERMISSION,
			CMFCorePermissions.View,
			CMFCorePermissions.AddPortalContent,
			CMFCorePermissions.ModifyPortalContent]
	}
	
	security = ClassSecurityInfo()
			
	def __init__(self):
		self.ACL_initialized=0
		self.UserRoles={}
		
	def getUserRoles(self):
		""" return the db Plomino roles """
		return self.UserRoles.keys()
		
	def getUsersForRoles(self, role):
		""" return the users having the given Plomino user role """
		if self.UserRoles.has_key(role):
			return self.UserRoles[role]
		else:
			return ''
			
	def hasUserRole(self, user, role):
		""" test if the given user has the given Plomino user role """
		if self.UserRoles.has_key(role):
			return user in self.UserRoles[role]
		else:
			return False
	
	def getUsersForRight(self, right):
		""" return the users having the given Plomino access right """
		return self.users_with_local_role(right)
	
	def getCurrentUser(self):
		membershiptool = getToolByName(self, 'portal_membership')
		return membershiptool.getAuthenticatedMember()
		
	def getCurrentUserRights(self):
		userid = self.getCurrentUser().getMemberId()
		return self.get_local_roles_for_userid(userid)
		
	def getCurrentUserRoles(self):
		userid = self.getCurrentUser().getUserName()
		allroles = self.getUserRoles()
		roles = []
		for r in allroles:
			if self.hasUserRole(userid, r):
				roles.append(r)
		return roles
		
	def isCurrentUserAuthor(self, doc):
		if not self.checkUserPermission(EDIT_PERMISSION):
			return False
		if 'PlominoAuthor' in self.getCurrentUserRights():
			authors = doc.getItem('Plomino_Authors')
			name = self.getCurrentUser().getUserName()
			if name in authors:
				return True
			roles = self.getCurrentUserRoles()
			for r in roles:
				if r in authors:
					return True
			return False
		else:
			return True
				
	def initializeACL(self):
		""" create the default Plomino access rights """
		self._addRole("PlominoReader")
		self.setPlominoPermissions("PlominoReader", "PlominoReader")
		self._addRole("PlominoAuthor")
		self.setPlominoPermissions("PlominoAuthor", "PlominoAuthor")
		self._addRole("PlominoEditor")
		self.setPlominoPermissions("PlominoEditor", "PlominoEditor")
		self._addRole("PlominoDesigner")
		self.setPlominoPermissions("PlominoDesigner", "PlominoDesigner")
		self._addRole("PlominoManager")
		self.setPlominoPermissions("PlominoManager", "PlominoManager")
		self.AnomynousAccessRight="NoAccess"
		self.setPlominoPermissions("Anonymous", "NoAccess")
		self.AuthenticatedAccessRight="NoAccess"
		self.setPlominoPermissions("Authenticated", "NoAccess")
		self.ACL_initialized=1
		
	security.declarePrivate('setPlominoPermissions')
	def setPlominoPermissions(self, right, p):
		# Note: be careful, Zope 'roles' are different than Plomino 'roles'
		# Plomino access rights are implemented using Zope roles
		# and Plomino roles are just a dictionnary handled by Plomino db
		# with no impact in the Zope security 
		self.manage_role(right, permissions=self.PLOMINO_PERMISSIONS[p])
	
	def checkUserPermission(self, perm):
		return checkPerm(perm, self)
    
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
	
	security.declareProtected(ACL_PERMISSION, 'setGenericAccess')
	def setGenericAccess(self, REQUEST):
		""" set the generic users access rights """
		anonymousaccessright=REQUEST.get('anonymousaccessright')
		self.AnomynousAccessRight=anonymousaccessright
		self.setPlominoPermissions("Anonymous", anonymousaccessright)
		
		authenticatedaccessright=REQUEST.get('authenticatedaccessright')
		self.AuthenticatedAccessRight=authenticatedaccessright
		self.setPlominoPermissions("Authenticated", authenticatedaccessright)
		REQUEST.RESPONSE.redirect('./DatabaseACL')
		
	def addPlominoUserRole(self, REQUEST):
		""" add a user role in the ACL """
		newrole=REQUEST.get('newrole')
		# roles names must be enclosed in brackets wo they can be distinguished
		# from users names in Authors fields
		newrole='['+newrole+']'
		roles = self.UserRoles
		if not(roles.has_key(newrole)):
			roles[newrole] = {}
			self.UserRoles = roles
		REQUEST.RESPONSE.redirect('./DatabaseACL')
			
	def removePlominoUserRole(self, REQUEST):
		""" remove a user role from the ACL """
		role=REQUEST.get('role')
		LOG('Plomino', ERROR, 'role='+role)
		roles = self.UserRoles
		if roles.has_key(role):
			LOG('Plomino', ERROR, 'role found')
			del roles[role]
			self.UserRoles = roles
		REQUEST.RESPONSE.redirect('./DatabaseACL')
	
	def addPlominoRoleToUser(self, REQUEST):
		""" give a role to a user """
		role=REQUEST.get('role')
		user=REQUEST.get('user')
		roles = self.UserRoles
		if roles.has_key(role):
			userslist = roles[role]
			userslist[user]=1
			roles[role] = userslist
			self.UserRoles = roles
		REQUEST.RESPONSE.redirect('./DatabaseACL')
		
	def removePlominoRoleFromUser(self, REQUEST):
		""" remove a role from a user """
		role=REQUEST.get('role')
		user=REQUEST.get('user')
		roles = self.UserRoles
		if roles.has_key(role):
			userslist = roles[role]
			if userslist.has_key(user):
				del userslist[user]
				roles[role] = userslist
				self.UserRoles = roles
		REQUEST.RESPONSE.redirect('./DatabaseACL')
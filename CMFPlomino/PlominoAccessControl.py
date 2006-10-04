# -*- coding: utf-8 -*-
#
# File: PlominoAccessControl.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:39 2006
# Generator: ArchGenXML Version 1.5.1-svn
#            http://plone.org/products/archgenxml
#
# Zope Public License (ZPL)
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

__author__ = """[Eric BREHAULT] <[ebrehault@gmail.com]>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from Products.CMFCore import CMFCorePermissions
from Products.CMFCore.utils import _checkPermission as checkPerm
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName

from zLOG import LOG, ERROR
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoAccessControl_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoAccessControl(ATFolder):
    """Plomino access control utilities
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'PlominoAccessControl'

    meta_type = 'PlominoAccessControl'
    portal_type = 'PlominoAccessControl'
    allowed_content_types = [] + list(getattr(ATFolder, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 0
    #content_icon = 'PlominoAccessControl.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "PlominoAccessControl"
    typeDescMsgId = 'description_edit_plominoaccesscontrol'

    _at_rename_after_creation = True

    schema = PlominoAccessControl_schema

    ##code-section class-header #fill in your manual code here
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
    ##/code-section class-header

    # Methods

    security.declarePublic('__init__')
    def __init__(self):
        """
        """
	self.ACL_initialized=0
	self.UserRoles={}

    security.declarePublic('getUserRoles')
    def getUserRoles(self):
        """return the db Plomino roles
        """
	return self.UserRoles.keys()

    security.declarePublic('getUsersForRoles')
    def getUsersForRoles(self,role):
        """return the users having the given Plomino user role
        """
	if self.UserRoles.has_key(role):
		return self.UserRoles[role]
	else:
		return ''

    security.declarePublic('hasUserRole')
    def hasUserRole(self,user,role):
        """test if the given user has the given Plomino user role
        """
	if self.UserRoles.has_key(role):
		return user in self.UserRoles[role]
	else:
		return False

    security.declarePublic('getUsersForRight')
    def getUsersForRight(self,right):
        """return the users having the given Plomino access right
        """
	return self.users_with_local_role(right)

    security.declarePublic('getCurrentUser')
    def getCurrentUser(self):
        """get the current user
        """
	membershiptool = getToolByName(self, 'portal_membership')
	return membershiptool.getAuthenticatedMember()

    security.declarePublic('getCurrentUserRights')
    def getCurrentUserRights(self):
        """get the current user rights
        """
	try:
		userid = self.getCurrentUser().getMemberId()
		return self.get_local_roles_for_userid(userid)
	except Exception:
		return [self.AnomynousAccessRight]

    security.declarePublic('getCurrentUserRoles')
    def getCurrentUserRoles(self):
        """get current user roles
        """
	userid = self.getCurrentUser().getUserName()
	allroles = self.getUserRoles()
	roles = []
	for r in allroles:
		if self.hasUserRole(userid, r):
			roles.append(r)
	return roles

    security.declarePublic('isCurrentUserAuthor')
    def isCurrentUserAuthor(self,doc):
        """is the current user the document's author?
        """
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

    security.declarePublic('hasReadPermission')
    def hasReadPermission(self):
        """has read permission?
        """
	return self.checkUserPermission(READ_PERMISSION)

    security.declarePublic('initializeACL')
    def initializeACL(self):
        """create the default Plomino access rights
        """
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
    def setPlominoPermissions(self,right,p):
        """Note: be careful, Zope 'roles' are different than Plomino
        'roles' Plomino access rights are implemented using Zope roles
        and Plomino roles are just a dictionnary handled by Plomino db
        with no impact in the Zope security
        """
	self.manage_role(right, permissions=self.PLOMINO_PERMISSIONS[p])

    security.declarePublic('checkUserPermission')
    def checkUserPermission(self,perm):
        """check user's permission
        """
	return checkPerm(perm, self)

    security.declareProtected(ACL_PERMISSION, 'addACLEntry')
    def addACLEntry(self,REQUEST):
        """add an entry in the ACL
        """
	user=REQUEST.get('newuser')
	accessright=REQUEST.get('accessright')
	self.manage_setLocalRoles(user, [accessright])
	REQUEST.RESPONSE.redirect('./DatabaseACL')

    security.declareProtected(ACL_PERMISSION, 'removeACLEntries')
    def removeACLEntries(self,REQUEST):
        """remove entries in the ACL
        """
	users=REQUEST.get('users')
	self.manage_delLocalRoles(users)
	REQUEST.RESPONSE.redirect('./DatabaseACL')

    security.declareProtected(ACL_PERMISSION, 'setGenericAccess')
    def setGenericAccess(self,REQUEST):
        """set the generic users access rights
        """
	anonymousaccessright=REQUEST.get('anonymousaccessright')
	self.AnomynousAccessRight=anonymousaccessright
	self.setPlominoPermissions("Anonymous", anonymousaccessright)

	authenticatedaccessright=REQUEST.get('authenticatedaccessright')
	self.AuthenticatedAccessRight=authenticatedaccessright
	self.setPlominoPermissions("Authenticated", authenticatedaccessright)
	REQUEST.RESPONSE.redirect('./DatabaseACL')

    security.declarePublic('addPlominoUserRole')
    def addPlominoUserRole(self,REQUEST):
        """add a user role in the ACL
        """
	newrole=REQUEST.get('newrole')
	# roles names must be enclosed in brackets wo they can be distinguished
	# from users names in Authors fields
	newrole='['+newrole+']'
	roles = self.UserRoles
	if not(roles.has_key(newrole)):
		roles[newrole] = {}
		self.UserRoles = roles
	REQUEST.RESPONSE.redirect('./DatabaseACL')

    security.declarePublic('removePlominoUserRole')
    def removePlominoUserRole(self,REQUEST):
        """remove a user role from the ACL
        """
	role=REQUEST.get('role')
	roles = self.UserRoles
	if roles.has_key(role):
		del roles[role]
		self.UserRoles = roles
	REQUEST.RESPONSE.redirect('./DatabaseACL')

    security.declarePublic('addPlominoRoleToUser')
    def addPlominoRoleToUser(self,REQUEST):
        """give a role to a user
        """
	role=REQUEST.get('role')
	user=REQUEST.get('user')
	roles = self.UserRoles
	if roles.has_key(role):
		userslist = roles[role]
		userslist[user]=1
		roles[role] = userslist
		self.UserRoles = roles
	REQUEST.RESPONSE.redirect('./DatabaseACL')

    security.declarePublic('removePlominoRoleFromUser')
    def removePlominoRoleFromUser(self,REQUEST):
        """
        """
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

    security.declarePublic('getPortalMembersIds')
    def getPortalMembersIds(self):
        """return all members id
        """
        membershiptool = getToolByName(self, 'portal_membership')
	return membershiptool.listMemberIds ()


registerType(PlominoAccessControl, PROJECTNAME)
# end of class PlominoAccessControl

##code-section module-footer #fill in your manual code here
##/code-section module-footer




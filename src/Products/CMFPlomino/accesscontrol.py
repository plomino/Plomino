# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from AccessControl import getSecurityManager
from plone import api
from Products.CMFCore import permissions
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
import warnings

import config
from utils import asList


class AccessControl:
    """ Plomino access control utilities
    """
    security = ClassSecurityInfo()

    PLOMINO_PERMISSIONS = {
        "NoAccess": [],
        "PlominoReader": [
            config.READ_PERMISSION,
            permissions.View,
            permissions.AccessContentsInformation],
        "PlominoAuthor": [
            config.READ_PERMISSION,
            config.EDIT_PERMISSION,
            config.REMOVE_PERMISSION,
            config.CREATE_PERMISSION,
            config.ADD_CONTENT_PERMISSION,
            permissions.View,
            permissions.AccessContentsInformation,
            'Copy or Move', ],
        "PlominoEditor": [
            config.READ_PERMISSION,
            config.EDIT_PERMISSION,
            config.REMOVE_PERMISSION,
            config.CREATE_PERMISSION,
            config.ADD_CONTENT_PERMISSION,
            permissions.View,
            permissions.AccessContentsInformation,
            'Copy or Move',
            permissions.DeleteObjects, ],
        "PlominoDesigner": [
            config.READ_PERMISSION,
            config.EDIT_PERMISSION,
            config.REMOVE_PERMISSION,
            config.CREATE_PERMISSION,
            config.DESIGN_PERMISSION,
            config.ADD_CONTENT_PERMISSION,
            config.ADD_DESIGN_PERMISSION,
            permissions.View,
            permissions.AccessContentsInformation,
            'Copy or Move',
            permissions.AddPortalContent,
            permissions.ModifyPortalContent, ],
        "PlominoManager": [
            config.READ_PERMISSION,
            config.EDIT_PERMISSION,
            config.REMOVE_PERMISSION,
            config.CREATE_PERMISSION,
            config.DESIGN_PERMISSION,
            config.ADD_CONTENT_PERMISSION,
            config.ADD_DESIGN_PERMISSION,
            config.ACL_PERMISSION,
            permissions.View,
            permissions.AccessContentsInformation,
            'Copy or Move',
            permissions.AddPortalContent,
            permissions.ModifyPortalContent, ]
    }

    PLOMINO_RIGHTS_PRIORITY = [
        "NoAccess",
        "PlominoReader",
        "PlominoAuthor",
        "PlominoEditor",
        "PlominoDesigner",
        "PlominoManager",
        "Owner"]

    def _redirectIfResponse(self, target):
        request = getattr(self, 'REQUEST', None)
        response = getattr(request, 'RESPONSE', None)
        if response:
            response.redirect(target)

    security.declarePublic('getUserRoles')

    def getUserRoles(self):
        """ Return the Plomino roles for the database
        """
        return self.UserRoles.keys()

    security.declarePublic('getUsersForRole')

    def getUsersForRole(self, role):
        """ Return the users having the given Plomino user role
        """
        if role in self.UserRoles:
            return self.UserRoles[role].keys()
        else:
            return []

    security.declarePublic('hasUserRole')

    def hasUserRole(self, userid, role):
        """ Returns ``True`` if the given userid has the given Plomino user role.
        """
        if role in self.UserRoles:
            role_people = self.UserRoles[role].keys()
            if userid in role_people:
                return True
            else:
                groupstool = self.portal_groups
                usergroups = [g.id for g in
                    groupstool.getGroupsByUserId(userid)]
                test = False
                for u in role_people:
                    if u in usergroups:
                        test = True
                return test
        else:
            return False

    security.declarePublic('getUsersForRight')

    def getUsersForRight(self, right):
        """ Return the users having the given Plomino access right
        """
        return self.users_with_local_role(right)

    security.declarePublic('getCurrentMember')

    def getCurrentMember(self):
        """ Returns the current member.
        """
        membershiptool = api.portal.get().portal_membership
        return membershiptool.getAuthenticatedMember()

    security.declarePublic('getCurrentUserId')

    def getCurrentUserId(self):
        """ Returns the current user id.
        """
        return self.getCurrentMember().getUserName()

    security.declarePublic('getCurrentUserGroups')

    def getCurrentUserGroups(self):
        """ Get the current user groups
        """
        member = self.getCurrentMember()
        return member.getGroups()

    security.declarePublic('getCurrentUserRights')

    def getCurrentUserRights(self):
        """ Returns the current user Plomino rights.
        """
        try:
            userid = self.getCurrentUserId()
            rights = self.get_local_roles_for_userid(userid)

            # we append group rights
            groupstool = self.portal_groups
            usergroups = [g.id for g in groupstool.getGroupsByUserId(userid)]
            for g in usergroups:
                rights = rights + self.get_local_roles_for_userid(g)

            if not rights:
                # still no specific rights, so return the rights configured
                # as AuthenticatedAccessRight
                default_right = getattr(
                    self,
                    "AuthenticatedAccessRight",
                    "NoAccess")
                rights = [default_right]
            return rights
        except Exception, e:
            # XXX: Log the exception.
            warnings.warn("Access error: %s" % e)
            return [getattr(self, "AnomynousAccessRight", "NoAccess")]

    security.declarePublic('hasCurrentUserRight')

    def hasCurrentUserRight(self, right):
        """ Test whether the current user has the given role, or a higher role.
        """
        rights = self.getCurrentUserRights()
        levels = [self.PLOMINO_RIGHTS_PRIORITY.index(r) for r in rights
                if r in self.PLOMINO_RIGHTS_PRIORITY]
        if levels:
            maxlevel = max(levels)
            return maxlevel >= self.PLOMINO_RIGHTS_PRIORITY.index(right)
        else:
            return False

    security.declarePublic('getCurrentUserRoles')

    def getCurrentUserRoles(self):
        """ Get current user roles
        """
        userid = self.getCurrentMember().getUserName()
        allroles = self.getUserRoles()
        roles = []
        for r in allroles:
            if self.hasUserRole(userid, r):
                roles.append(r)
        return roles

    security.declarePublic('isCurrentUserReader')

    def isCurrentUserReader(self, doc):
        """ Does the current user have read permission on the db
        (so Plone security is preserved)?

        If Plomino_Readers is defined on the doc, is he part of it?
        """
        isreader = False
        if self.checkUserPermission(config.READ_PERMISSION, doc):
            allowed_readers = set(doc.getPlominoReaders())
            if ('*' in allowed_readers or
                    self.checkUserPermission(config.ACL_PERMISSION)):
                isreader = True
            else:
                username = self.getCurrentMember().getUserName()
                if username == "Anonymous User":
                    user_groups_roles = set(['Anonymous'])
                else:
                    user_groups_roles = set(
                        ['Anonymous', username] +
                        self.getCurrentUserGroups() +
                        self.getCurrentUserRoles())
                if allowed_readers.intersection(user_groups_roles):
                    isreader = True
        return isreader

    security.declarePublic('isCurrentUserAuthor')

    def isCurrentUserAuthor(self, doc):
        """ Does the current user have the author role on doc?

        This is True if:
        - they have the Owner or Manager Plone roles, OR
        - if they have the PlominoDesigner, PlominoEditor or PlominoManager
          role globally, OR
        - if they have the PlominoAuthor role, AND
          - they are in the Plomino_Authors item on doc, OR
          - they have a *role* which is in the Plomino_Authors item, OR
          - they belong to a *group* which is in the Plomino_Authors item.
        """
        # the user must at least have edit permission
        if not self.checkUserPermission(config.EDIT_PERMISSION):
            return False

        # the user must at least be an allowed reader
        if not self.isCurrentUserReader(doc):
            return False

        # if the user is Owner of the db or Manager, no problem
        general_plone_rights = self.getCurrentMember().getRolesInContext(
            doc.getParentDatabase())
        for r in ['Owner', 'Manager']:
            if r in general_plone_rights:
                return True

        # check if the user is more powerful than a regular PlominoAuthor
        current_rights = self.getCurrentUserRights()
        for r in ['PlominoEditor', 'PlominoDesigner', 'PlominoManager']:
            if r in current_rights:
                return True

        # if he is just a PlominoAuthor, check if he is author of this very
        # document
        if 'PlominoAuthor' in current_rights:

            authors = asList(doc.getItem('Plomino_Authors') or [])
            if not authors:
                return False

            if '*' in authors:
                return True

            name = self.getCurrentMember().getUserName()
            if name in authors:
                return True

            roles = self.getCurrentUserRoles()
            for r in roles:
                if r in authors:
                    return True

            groupstool = self.portal_groups
            usergroups = [g.id for g in groupstool.getGroupsByUserId(name)]
            for u in authors:
                if u in usergroups:
                    return True

            return False

        return False

    security.declarePublic('hasReadPermission')

    def hasReadPermission(self, obj=None):
        """ Has read permission on obj?
        """
        if obj is None:
            return self.checkUserPermission(config.READ_PERMISSION)

        return getSecurityManager().checkPermission(
            config.READ_PERMISSION, obj)

    security.declarePublic('hasCreatePermission')

    def hasCreatePermission(self, obj=None):
        """ Has create permission on obj?
        """
        if obj is None:
            obj = self

        sm = getSecurityManager()

        for p in [config.CREATE_PERMISSION, config.ADD_CONTENT_PERMISSION]:
            if not sm.checkPermission(p, obj):
                return False

        return True

    security.declarePublic('hasEditPermission')

    def hasEditPermission(self, obj=None):
        """ Has edit permission on obj?
        """
        if obj is None:
            obj = self

        return getSecurityManager().checkPermission(
            config.EDIT_PERMISSION, obj)

    security.declarePublic('hasRemovePermission')

    def hasRemovePermission(self, obj=None):
        """ Has remove permission for obj?
        """
        if obj is None:
            obj = self

        return getSecurityManager().checkPermission(
            config.REMOVE_PERMISSION, obj)

    security.declarePublic('hasDesignPermission')

    def hasDesignPermission(self, obj=None):
        """ Has design permission on obj?
        """
        if obj is None:
            obj = self

        return getSecurityManager().checkPermission(
            config.DESIGN_PERMISSION, obj)

    security.declarePublic('initializeACL')

    def initializeACL(self):
        """ Create the default Plomino access rights
        """
        self._addRole("PlominoReader")
        self._addRole("PlominoAuthor")
        self._addRole("PlominoEditor")
        self._addRole("PlominoDesigner")
        self._addRole("PlominoManager")
        self.refreshPlominoRolesPermissions()
        self.AnomynousAccessRight = "NoAccess"
        self.setPlominoPermissions("Anonymous", "NoAccess")
        self.AuthenticatedAccessRight = "NoAccess"
        self.setPlominoPermissions("Authenticated", "NoAccess")
        self.ACL_initialized = 1

    security.declarePublic('refreshPlominoRolesPermissions')

    def refreshPlominoRolesPermissions(self):
        """ Set the default Plomino access rights
        """
        self.setPlominoPermissions("PlominoReader", "PlominoReader")
        self.setPlominoPermissions("PlominoAuthor", "PlominoAuthor")
        self.setPlominoPermissions("PlominoEditor", "PlominoEditor")
        self.setPlominoPermissions("PlominoDesigner", "PlominoDesigner")
        self.setPlominoPermissions("PlominoManager", "PlominoManager")
        self.setPlominoPermissions("Manager", "PlominoManager")
        self.setPlominoPermissions("Owner", "PlominoManager")

    security.declarePrivate('setPlominoPermissions')

    def setPlominoPermissions(self, right, p):
        """ Note: be careful, Zope 'roles' are different than Plomino
        'roles'. Plomino access rights are implemented using Zope roles
        and Plomino roles are just a dictionary handled by Plomino db
        with no impact on Zope security.
        """
        self.manage_role(right, permissions=self.PLOMINO_PERMISSIONS[p])

    security.declarePublic('checkUserPermission')

    def checkUserPermission(self, perm, obj=None):
        """ Check user's permission
        """
        if obj is None:
            obj = self

        return getSecurityManager().checkPermission(perm, obj)

    security.declareProtected(config.ACL_PERMISSION, 'addACLEntry')

    def addACLEntry(self, REQUEST):
        """ Add an entry in the ACL
        """
        # TODO: Remove assumption that we have a request.
        user = REQUEST.get('newuser')
        accessright = REQUEST.get('accessright')
        self.manage_setLocalRoles(user, [accessright])
        self._redirectIfResponse('./DatabaseACL')

    security.declareProtected(config.ACL_PERMISSION, 'removeACLEntries')

    def removeACLEntries(self, REQUEST):
        """ Remove entries from the ACL
        """
        # TODO: Remove assumption that we have a request.
        users = REQUEST.get('users')
        if type(users) == str:
            users = [users]

        self.manage_delLocalRoles(users)
        self._redirectIfResponse('./DatabaseACL')

    security.declareProtected(config.ACL_PERMISSION, 'setGenericAccess')

    def setGenericAccess(self, REQUEST):
        """ Set the generic users access rights
        """
        anonymousaccessright = REQUEST.get('anonymousaccessright')
        self.AnomynousAccessRight = anonymousaccessright
        self.setPlominoPermissions("Anonymous", anonymousaccessright)

        authenticatedaccessright = REQUEST.get('authenticatedaccessright')
        self.AuthenticatedAccessRight = authenticatedaccessright
        self.setPlominoPermissions("Authenticated", authenticatedaccessright)

        # update Plone workflow mappings
        workflow_tool = api.portal.get().portal_workflow
        wfs = workflow_tool.getWorkflowsFor(self)
        for wf in wfs:
            if not isinstance(wf, DCWorkflowDefinition):
                continue
            wf.updateRoleMappingsFor(self)

        self._redirectIfResponse('./DatabaseACL')

    security.declareProtected(config.ACL_PERMISSION, 'addPlominoUserRole')

    def addPlominoUserRole(self, REQUEST):
        """ Add a user role in the ACL
        """
        # TODO: Remove assumption that we have a request.
        newrole = REQUEST.get('newrole')
        # roles names must be enclosed in brackets so they can be
        # distinguished from users names in Authors fields
        newrole = '[%s]' % newrole
        roles = self.UserRoles
        if newrole not in roles:
            roles[newrole] = {}
            self.UserRoles = roles
        self._redirectIfResponse('./DatabaseACL')

    security.declareProtected(config.ACL_PERMISSION, 'removePlominoUserRole')

    def removePlominoUserRole(self, REQUEST):
        """ Remove a user role from the ACL
        """
        # TODO: Remove assumption that we have a request.
        role = REQUEST.get('role')
        roles = self.UserRoles
        if role in roles:
            del roles[role]
            self.UserRoles = roles
        self._redirectIfResponse('./DatabaseACL')

    security.declareProtected(config.ACL_PERMISSION, 'addPlominoRoleToUser')

    def addPlominoRoleToUser(self, REQUEST):
        """ Give a role to a user
        """
        # TODO: Remove assumption that we have a request.
        role = REQUEST.get('role')
        user = REQUEST.get('user')
        roles = self.UserRoles
        if role in roles:
            userslist = roles[role]
            userslist[user] = 1
            roles[role] = userslist
            self.UserRoles = roles
        self._redirectIfResponse('./DatabaseACL')

    security.declareProtected(
        config.ACL_PERMISSION, 'removePlominoRoleFromUser')

    def removePlominoRoleFromUser(self, REQUEST):
        """ Remove a role from a user
        """
        # TODO: Remove assumption that we have a request.
        role = REQUEST.get('role')
        user = REQUEST.get('user')
        roles = self.UserRoles
        if role in roles:
            userslist = roles[role]
            if user in userslist:
                del userslist[user]
                roles[role] = userslist
                self.UserRoles = roles
        self._redirectIfResponse('./DatabaseACL')

    security.declarePublic('getPortalMembers')

    def getPortalMembers(self):
        """ Return all members
        """
        membershiptool = api.portal.get().portal_membership
        return membershiptool.searchForMembers(sort_by='userid')

    security.declarePublic('getPortalMembersIds')

    def getPortalMembersIds(self):
        """ Return all member ids
        """
        return [m.getId() for m in self.getPortalMembers()]

    security.declarePublic('getPortalGroups')

    def getPortalGroups(self):
        """ Return all groups
        """
        groupstool = api.portal.get().portal_groups
        return groupstool.listGroups()

    security.declarePublic('getPortalMembersGroupsIds')

    def getPortalMembersGroupsIds(self):
        """ Return all member and group ids
        """
        # XXX: This returns members and groups, not ids.
        return self.getPortalMembers() + self.getPortalGroups()

    security.declarePublic('getSpecificRights')

    def getSpecificRights(self, key=None):
        """
        """
        if not hasattr(self, 'specific_rights'):
            self.specific_rights = {
                'specific_deletedocument': 'PlominoAuthor'}
        if key:
            return self.specific_rights.get(key, None)
        else:
            return self.specific_rights

    security.declarePublic('setSpecificRights')

    def setSpecificRights(self, right, key):
        """
        """
        s = self.getSpecificRights()
        s[right] = key
        self.specific_rights = s

    security.declareProtected(config.ACL_PERMISSION, 'manage_specificrights')

    def manage_specificrights(self, REQUEST):
        """
        """
        deletedocument = REQUEST.get('specific_deletedocument', None)
        if deletedocument:
            self.setSpecificRights('specific_deletedocument', deletedocument)
        self._redirectIfResponse('./DatabaseACL')

    security.declareProtected(config.ACL_PERMISSION, 'getWorkflowStates')

    def getWorkflowStates(self):
        """
        """
        wftool = self._getWorkflowTool()
        if not wftool:
            return {}

        ob = self
        states = {}
        wf_ids = wftool.getChainFor(ob)
        for wf_id in wf_ids:

            wf = wftool.getWorkflowById(wf_id)
            if not wf:
                continue

            # XXX a standard API would be nice
            if hasattr(wf, 'getReviewStateOf'):
                # Default Workflow
                state = wf.getReviewStateOf(ob)
            elif hasattr(wf, '_getWorkflowStateOf'):
                # DCWorkflow
                state = wf._getWorkflowStateOf(ob, id_only=1)
            else:
                state = '(Unknown)'
            states[wf_id] = state

        return states

    security.declareProtected(config.READ_PERMISSION, 'checkReadPermission')

    def checkReadPermission(self):
        """ Called from templates to check access permission
        """
        # The point of this method is the security declaration above.
        pass

    security.declareProtected(config.EDIT_PERMISSION, 'checkEditPermission')

    def checkEditPermission(self):
        """ Called from templates to check access permission
        """
        pass

    security.declareProtected(
        config.REMOVE_PERMISSION, 'checkRemovePermission')

    def checkRemovePermission(self):
        """ Called from templates to check access permission
        """
        pass

    security.declareProtected(
        config.CREATE_PERMISSION, 'checkCreatePermission')

    def checkCreatePermission(self):
        """ Called from templates to check access permission
        """
        pass

    security.declareProtected(
        config.DESIGN_PERMISSION, 'checkDesignPermission')

    def checkDesignPermission(self):
        """ Called from templates to check access permission
        """
        pass

    security.declareProtected(config.ACL_PERMISSION, 'checkACLPermission')

    def checkACLPermission(self):
        """ Called from templates to check access permission
        """
        pass

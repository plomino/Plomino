# -*- coding: utf-8 -*-
#
# File: PlominoDatabase.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:37 2006
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
from Products.CMFPlomino.PlominoAccessControl import PlominoAccessControl
from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.utils import make_uuid
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

import string

from zLOG import LOG, ERROR

from PlominoIndex import PlominoIndex
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoDatabase_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    getattr(PlominoAccessControl, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoDatabase(ATFolder, PlominoAccessControl):
    """
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder,'__implements__',()),) + (getattr(PlominoAccessControl,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'PlominoDatabase'

    meta_type = 'PlominoDatabase'
    portal_type = 'PlominoDatabase'
    allowed_content_types = ['PlominoForm', 'PlominoView', 'PlominoDocument'] + list(getattr(ATFolder, 'allowed_content_types', [])) + list(getattr(PlominoAccessControl, 'allowed_content_types', []))
    filter_content_types = 1
    global_allow = 1
    content_icon = 'PlominoDatabase.gif'
    immediate_view = 'base_view'
    default_view = 'OpenDatabase'
    suppl_views = ()
    typeDescription = "PlominoDatabase"
    typeDescMsgId = 'description_edit_plominodatabase'


    actions =  (


       {'action': "string:${object_url}/OpenDatabase",
        'category': "object",
        'id': 'view',
        'name': 'View',
        'permissions': ("View",),
        'condition': 'python:1'
       },


       {'action': "string:${object_url}/DatabaseForms",
        'category': "object",
        'id': 'forms',
        'name': 'Forms',
        'permissions': (DESIGN_PERMISSION,),
        'condition': 'python:1'
       },


       {'action': "string:${object_url}/DatabaseViews",
        'category': "object",
        'id': 'views',
        'name': 'Views',
        'permissions': (DESIGN_PERMISSION,),
        'condition': 'python:1'
       },

       {'action': "string:${object_url}/base_edit",
        'category': "object",
        'id': 'edit',
        'name': 'Edit',
        'permissions': (DESIGN_PERMISSION,),
        'condition': 'python:1'
       },

       {'action': "string:${object_url}/DatabaseACL",
        'category': "object",
        'id': 'acl',
        'name': 'ACL',
        'permissions': (ACL_PERMISSION,),
        'condition': 'python:1'
       },


    )

    _at_rename_after_creation = True

    schema = PlominoDatabase_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        """ACL setup
        """
	self.initializeACL()

    security.declarePublic('getForms')
    def getForms(self):
        """return the database forms list
        """
	return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoForm']})

    security.declarePublic('getViews')
    def getViews(self):
        """return the database views list
        """
	return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoView']})

    security.declarePublic('getForm')
    def getForm(self,formname):
        """return a PlominoForm
        """
	return self._getOb( formname.lower() )

    security.declarePublic('getView')
    def getView(self,viewname):
        """return a PlominoView
        """
	return self._getOb( viewname.lower() )

    security.declareProtected(CREATE_PERMISSION, 'createDocument')
    def createDocument(self):
        """create a unique ID and invoke PlominoDocument factory
        """
	newid = make_uuid()
	self.invokeFactory( type_name='PlominoDocument', id=newid)
	doc = self._getOb( newid )
	doc.setParentDatabase(self)
	return doc

    security.declareProtected(EDIT_PERMISSION, 'deleteDocument')
    def deleteDocument(self,doc):
        """delete the document from database
        """
	if not self.isCurrentUserAuthor(doc):
		raise Unauthorized, "You cannot edit this document."
	else:
		self.manage_delObjects(doc.id)

    security.declarePublic('getIndex')
    def getIndex(self):
        """return the database index
        """
	return self._getOb('plomino_index')

    security.declarePublic('__init__')
    def __init__(self,oid,**kw):
        """
        """
	#changed
	ATFolder.__init__(self, oid, **kw)
	PlominoAccessControl.__init__(self)
	index = PlominoIndex()
	self._setObject(index.getId(), index)


registerType(PlominoDatabase, PROJECTNAME)
# end of class PlominoDatabase

##code-section module-footer #fill in your manual code here
##/code-section module-footer




# -*- coding: utf-8 -*-
#
# File: PlominoDatabase.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:37 2006
# Generator: ArchGenXML Version 1.5.1-svn
#			http://plone.org/products/archgenxml
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
from Products.CMFPlomino.PlominoDesignManager import PlominoDesignManager
from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.utils import make_uuid
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Acquisition import *
from OFS.Folder import *
from Products.CMFPlomino.PlominoUtils import *
import string
import Globals

from zLOG import LOG, ERROR

from PlominoIndex import PlominoIndex
##/code-section module-header

schema = Schema((
	TextField(
		name='AboutDescription',
		allowable_content_types=('text/html',),
		widget=RichWidget(
			label="About this database",
			description="Describe the database, its objectives, its targetted audience, etc...",
			label_msgid='CMFPlomino_label_About',
			description_msgid='CMFPlomino_help_About',
			i18n_domain='CMFPlomino',
		),
		default_output_type='text/html'
	),
	TextField(
		name='UsingDescription',
		allowable_content_types=('text/html',),
		widget=RichWidget(
			label="Using this database",
			description="Describe how to use the database",
			label_msgid='CMFPlomino_label_Using',
			description_msgid='CMFPlomino_help_Using',
			i18n_domain='CMFPlomino',
		),
		default_output_type='text/html'
	),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoDatabase_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
	getattr(PlominoAccessControl, 'schema', Schema(())).copy() + \
	schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoDatabase(ATFolder, PlominoAccessControl, PlominoDesignManager):
	"""
	"""
	security = ClassSecurityInfo()
	__implements__ = (getattr(ATFolder,'__implements__',()),) + (getattr(PlominoAccessControl,'__implements__',()),)

	# This name appears in the 'add' box
	archetype_name = 'PlominoDatabase'

	meta_type = 'PlominoDatabase'
	portal_type = 'PlominoDatabase'
	allowed_content_types = ['PlominoForm', 'PlominoView', 'PlominoAgent', 'PlominoDocument'] + list(getattr(ATFolder, 'allowed_content_types', [])) + list(getattr(PlominoAccessControl, 'allowed_content_types', []))
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

	   {'action': "string:${object_url}/DatabaseDesign",
		'category': "object",
		'id': 'design',
		'name': 'Design',
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

	   {'action': "string:${object_url}/AboutDatabase",
		'category': "object",
		'id': 'about',
		'name': 'About',
		'permissions': ("View",),
		'condition': 'python:1'
	   },
	   
	   {'action': "string:${object_url}/UsingDatabase",
		'category': "object",
		'id': 'using',
		'name': 'Using',
		'permissions': ("View",),
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
		"""DB initialization
		"""
		self.initializeACL()
		resources = Folder('resources')
		resources.title='resources'
		self._setObject('resources', resources)
		p=self.getParentPortal()

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

	security.declarePublic('getAllDocuments')
	def getAllDocuments(self):
		"""return all the database documents
		"""
		return [d.getObject() for d in self.getFolderContents(contentFilter = {'portal_type' : ['PlominoDocument']})]
		
	security.declarePublic('getForm')
	def getForm(self,formname):
		"""return a PlominoForm
		"""
		return self._getOb( formname )

	security.declarePublic('getView')
	def getView(self,viewname):
		"""return a PlominoView
		"""
		return self._getOb( viewname )
	
	security.declarePublic('getDocument')
	def getDocument(self, docid):
		"""return a PlominoDocument
		"""
		return self._getOb( docid )
		
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
			raise Unauthorized, "You cannot delete this document."
		else:
			self.getIndex().unindexDocument(doc)
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
		
	security.declarePublic('getParentPortal')
	def getParentPortal(self):
		try:
			p = self._parentapp._getOb(self._parentportalid)
		except Exception:
			for o in self.aq_chain:
				if type(aq_self(o)).__name__=='Application':
					self._parentapp=o
				if type(aq_self(o)).__name__=='PloneSite':
					self._parentportalid=o.id
			p = self._parentapp._getOb(self._parentportalid)
		return p
	
	security.declarePublic('callScriptMethod')
	def callScriptMethod(self, scriptname, methodname, *args):
		code = importPlominoScript(self, scriptname)
		code=code.replace('\r','')
		lines=code.split('\n')
		indented_code="def plominoScript(*args):\n"
		for l in lines:
			indented_code=indented_code+'\t'+l+'\n'
		indented_code = indented_code +'\n\treturn '+methodname+'(*args)'
		exec indented_code
		return plominoScript(*args)
			
registerType(PlominoDatabase, PROJECTNAME)
# end of class PlominoDatabase

##code-section module-footer #fill in your manual code here
##/code-section module-footer




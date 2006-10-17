# -*- coding: utf-8 -*-
#
# File: PlominoIndex.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:40 2006
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
from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Globals import InitializeClass

from Products.ZCatalog.ZCatalog import LOG
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCatalog.Catalog import CatalogError

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject

from Products.CMFPlomino.config import PROJECTNAME
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoIndex_schema = BaseSchema.copy() + \
	schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoIndex(UniqueObject, ZCatalog, ActionProviderBase):
	"""Plomino index
	"""
	security = ClassSecurityInfo()
	__implements__ = (getattr(UniqueObject,'__implements__',()),) + (getattr(ZCatalog,'__implements__',()),) + (getattr(ActionProviderBase,'__implements__',()),)

	# This name appears in the 'add' box
	archetype_name = 'PlominoIndex'

	meta_type = 'PlominoIndex'
	portal_type = 'PlominoIndex'
	allowed_content_types = []
	filter_content_types = 0
	global_allow = 0
	#content_icon = 'PlominoIndex.gif'
	immediate_view = 'base_view'
	default_view = 'base_view'
	suppl_views = ()
	typeDescription = "PlominoIndex"
	typeDescMsgId = 'description_edit_plominoindex'

	_at_rename_after_creation = True

	schema = PlominoIndex_schema

	##code-section class-header #fill in your manual code here
	# don't know but archgenxml doesn't generate this - tagged value exists
	id = 'plomino_index'

	manage_options = ( ZCatalog.manage_options +
		ActionProviderBase.manage_options +
		({ 'label' : 'Overview', 'action' : 'manage_overview' }
		,
		))
	##/code-section class-header

	# Methods

	security.declarePublic('__init__')
	def __init__(self):
		"""
		"""
		ZCatalog.__init__(self, self.getId())
		self.createIndex('Form')
		self.createIndex('Plomino_Authors')

	security.declareProtected(CMFCorePermissions.View, 'getParentDatabase')
	def getParentDatabase(self):
		"""
		"""
		return self.getParentNode()

	security.declareProtected(CMFCorePermissions.View, 'createIndex')
	def createIndex(self,fieldname):
		"""
		"""
		try:
			self.addIndex(fieldname, 'FieldIndex')
			self.addColumn(fieldname)
		except CatalogError:
			# index already exists
			pass
		self.refreshCatalog()
		
	security.declareProtected(CMFCorePermissions.View, 'createSelectionIndex')
	def createSelectionIndex(self,fieldname):
		"""
		"""
		try:
			self.addIndex(fieldname, 'FieldIndex')
		except CatalogError:
			# index already exists
			pass
		self.refreshCatalog()

	security.declareProtected(CMFCorePermissions.View, 'deleteIndex')
	def deleteIndex(self,fieldname):
		"""
		"""
		self.delIndex(fieldname)
		self.delColumn(fieldname)
		self.refreshCatalog()

	security.declareProtected(CMFCorePermissions.View, 'indexDocument')
	def indexDocument(self,doc):
		"""
		"""
		self.catalog_object(doc, doc.id)

	security.declarePublic('unindexDocument')
	def unindexDocument(self,doc):
		"""
		"""
		self.uncatalog_object(doc.id)

	security.declarePublic('refresh')
	def refresh(self):
		"""
		"""
		self.refreshCatalog()

	security.declarePublic('dbsearch')
	def dbsearch(self,request,sortindex,reverse=0):
		"""
		"""
		return self.search(request, sortindex, reverse)

	security.declarePublic('getKeyUniqueValues')
	def getKeyUniqueValues(self,key):
		"""
		"""
		return self.uniqueValuesFor(key)


# end of class PlominoIndex

##code-section module-footer #fill in your manual code here
##/code-section module-footer




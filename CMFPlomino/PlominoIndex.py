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
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass

from Products.ZCatalog.ZCatalog import LOG
from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCatalog.Catalog import CatalogError

from Products.ZCTextIndex.Lexicon import CaseNormalizer
from Products.ZCTextIndex.Lexicon import Splitter
from Products.ZCTextIndex.Lexicon import StopWordRemover
from Products.ZCTextIndex.ZCTextIndex import PLexicon

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject, SimpleRecord
from Products.CMFCore.utils import getToolByName

from Products.CMFPlomino.config import PROJECTNAME
from Products.CMFPlomino.PlominoCatalog import PlominoCatalog
from Products.CMFPlomino.PlominoViewIndex import PlominoViewIndex
from Products.CMFPlomino.PlominoColumnIndex import PlominoColumnIndex
from Products.CMFPlomino.PlominoFileIndex import PlominoFileIndex
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
		self._catalog = PlominoCatalog()
		lexicon = PLexicon('plaintext_lexicon', '', Splitter(), CaseNormalizer(), StopWordRemover())
		self._setObject('plaintext_lexicon', lexicon)

	security.declareProtected(READ_PERMISSION, 'getParentDatabase')
	def getParentDatabase(self):
		"""
		"""
		return self.getParentNode()

	security.declareProtected(DESIGN_PERMISSION, 'createIndex')
	def createIndex(self,fieldname):
		"""
		"""
		try:
			self._catalog.addIndex(fieldname,PlominoColumnIndex(fieldname))
			self.addColumn(fieldname)
		except CatalogError:
			# index already exists
			pass
		self.refreshCatalog()
		
	security.declareProtected(DESIGN_PERMISSION, 'createFieldIndex')
	def createFieldIndex(self,fieldname, fieldtype):
		"""
		"""
		try:
			#self.addIndex(fieldname, 'KeywordIndex')
			indextype=FIELD_TYPES[fieldtype][1]
			if indextype=='ZCTextIndex':
				plaintext_extra = SimpleRecord( lexicon_id='plaintext_lexicon', index_type='Okapi BM25 Rank')
				self.addIndex(fieldname, 'ZCTextIndex', plaintext_extra)
				if fieldtype=='ATTACHMENT' and self.getParentDatabase().getIndexAttachments():
					self._catalog.addIndex('PlominoFiles_'+fieldname,PlominoFileIndex('PlominoFiles_'+fieldname, caller=self, extra=plaintext_extra))
					#self.addIndex('PlominoFiles_'+fieldname, 'ZCTextIndex', plaintext_extra)
			else:
				self.addIndex(fieldname, indextype)
			self.addColumn(fieldname)
		except CatalogError:
			# index already exists
			pass
		self.refreshCatalog()
		
	security.declareProtected(DESIGN_PERMISSION, 'createSelectionIndex')
	def createSelectionIndex(self,fieldname):
		"""
		"""
		try:
			self._catalog.addIndex(fieldname,PlominoViewIndex(fieldname))
		except CatalogError:
			# index already exists
			pass
		self.refreshCatalog()

	security.declareProtected(DESIGN_PERMISSION, 'deleteIndex')
	def deleteIndex(self,fieldname):
		"""
		"""
		self.delIndex(fieldname)
		self.delColumn(fieldname)
		self.refreshCatalog()

	security.declareProtected(READ_PERMISSION, 'indexDocument')
	def indexDocument(self,doc):
		"""
		"""
		self.catalog_object(doc, doc.absolute_url_path())

	security.declareProtected(READ_PERMISSION, 'unindexDocument')
	def unindexDocument(self,doc):
		"""
		"""
		self.uncatalog_object(doc.absolute_url_path())

	security.declarePublic('refresh')
	def refresh(self):
		"""
		"""
		self.refreshCatalog()

	security.declareProtected(READ_PERMISSION, 'dbsearch')
	def dbsearch(self,request,sortindex,reverse=0):
		"""
		"""
		return self.search(request, sortindex, reverse)

	security.declareProtected(READ_PERMISSION, 'getKeyUniqueValues')
	def getKeyUniqueValues(self,key):
		"""
		"""
		return self.uniqueValuesFor(key)

	security.declarePublic('convertFileToText')
	def convertFileToText(self, doc, field):
		""" (adapted from Plone3 ATContentTypes file class)
		"""
		source   = ''
		mimetype = 'text/plain'
		encoding = 'utf-8'
		
		if hasattr(doc.getItem(field), 'keys'):
			files=doc.getItem(field)
			# stage 1: get the searchable text and convert it to utf8
			sp    = getToolByName(self, 'portal_properties').site_properties
			stEnc = getattr(sp, 'default_charset', 'utf-8')
		
			# get the file and try to convert it to utf8 text
			ptTool = getToolByName(self, 'portal_transforms')
			for filename in files.keys():
				f = getattr(doc, filename)
				if f:
					mt = files[filename]
					try:
						result = ptTool.convertTo('text/plain', str(f), mimetype=mt)
						if result:
							data = result.getData()
						else:
							data = ''
					except TransformException:
						data = ''
					source+=data

		return source

# end of class PlominoIndex

##code-section module-footer #fill in your manual code here
##/code-section module-footer




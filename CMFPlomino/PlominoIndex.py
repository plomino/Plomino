#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

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


class PlominoIndex(UniqueObject, ZCatalog, ActionProviderBase):
	""" Plomino index """
	
	__implements__ = (ZCatalog.__implements__, ActionProviderBase.__implements__)
    
	id = 'plomino_index'
	meta_type = 'PlominoIndex'
	_actions = ()
	
	security = ClassSecurityInfo()
	
	manage_options = ( ZCatalog.manage_options +
			ActionProviderBase.manage_options +
			({ 'label' : 'Overview', 'action' : 'manage_overview' }
			,
			))
	
	def __init__(self):
		ZCatalog.__init__(self, self.getId())
		self.createIndex('Form')
		self.createIndex('Plomino_Authors')
        
	security = ClassSecurityInfo()
			
	security.declareProtected(CMFCorePermissions.View, 'getParentDatabase')	
	def getParentDatabase(self):
		return self.getParentNode()
	
	security.declareProtected(CMFCorePermissions.View, 'createIndex')	
	def createIndex(self, fieldname):
		try:
			self.addIndex(fieldname, 'FieldIndex')
			self.addColumn(fieldname)
			self.refreshCatalog()
		except CatalogError:
			# index already exists
			pass
	
	security.declareProtected(CMFCorePermissions.View, 'createSelectionIndex')	
	def createSelectionIndex(self, fieldname):
		try:
			self.addIndex(fieldname, 'FieldIndex')
			self.refreshCatalog()
		except CatalogError:
			# index already exists
			pass
			
	security.declareProtected(CMFCorePermissions.View, 'deleteIndex')	
	def deleteIndex(self, fieldname):
		self.delIndex(fieldname)
		self.delColumn(fieldname)
		
	security.declareProtected(CMFCorePermissions.View, 'indexDocument')	
	def indexDocument(self, doc):
		self.catalog_object(doc, doc.id)
		
	def unindexDocument(self, doc):
		self.uncatalog_object(doc.id)
		
	def refresh(self):
		self.refreshCatalog()
		
	def dbsearch(self, request, sortindex, reverse=0):
		return self.search(request, sortindex, reverse)
	
InitializeClass(PlominoIndex)
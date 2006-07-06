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
from Products.PluginIndexes.FieldIndex import FieldIndex

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
        
	security = ClassSecurityInfo()
		
	security.declareProtected(CMFCorePermissions.View, 'getParentDatabase')	
	def getParentDatabase(self):
		return self.getParentNode()
	
	security.declareProtected(CMFCorePermissions.View, 'createIndex')	
	def createIndex(self, fieldname):
		ZCatalog.addIndex(fieldname, 'FieldIndex')
	
InitializeClass(PlominoIndex)
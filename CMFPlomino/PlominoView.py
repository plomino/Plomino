#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName

from Products.CMFPlomino.config import PROJECTNAME

import PlominoDocument

class PlominoView(BaseFolder):
	""" Plomino view """
	schema = BaseFolderSchema + Schema(
				(StringField('Description',widget=TextAreaWidget(label='Description')),
				StringField('SelectionFormula',widget=TextAreaWidget(label='Selection formula')),
				StringField('SortField',widget=TextAreaWidget(label='Field used to sort the view')),
				StringField('FormFormula',widget=TextAreaWidget(label='Form formula'))
				))
	
	content_icon = "PlominoView.gif"
	
	actions = (
		{
		'id': 'view',
		'name': 'View',
		'action': 'string:${object_url}/OpenView',
		'permissions': (CMFCorePermissions.View,)
		},
		)
		
	security = ClassSecurityInfo()
	
	security.declareProtected(CMFCorePermissions.View, 'getViewName')
	def getViewName(self):
		return self.Title()
		
	def getParentDatabase(self):
		return self.getParentNode()
	
	def getAllDocuments(self):
		cat = getToolByName(self, 'portal_catalog', None)
		return cat.ZopeFindAndApply(
			obj = self.getParentDatabase(),
			obj_metatypes=['PlominoDocument'],
			obj_expr=self.getSelectionFormula()
			)
		
	def getColumns(self):
		return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoColumn']})
		
		
registerType(PlominoView, PROJECTNAME)
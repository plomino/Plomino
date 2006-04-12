#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.Archetypes.utils import make_uuid

from Products.CMFPlomino.config import PROJECTNAME

class PlominoDatabase(BaseFolder):
	""" Plomino DB """
	schema = BaseFolderSchema + Schema(
		StringField('Description',
		widget=TextAreaWidget(label='Description')
		))
	
	content_icon = "PlominoDatabase.gif"
	
	actions = (
		{
		'id': 'test',
		'name': 'Test',
		'action': 'string:${object_url}/db_view',
		'permissions': (CMFCorePermissions.View,)
		},
		{
		'id': 'forms',
		'name': 'Forms',
		'action': 'string:${object_url}/database_forms',
		'permissions': (CMFCorePermissions.View,)
		},
		{
		'id': 'views',
		'name': 'Views',
		'action': 'string:${object_url}/database_views',
		'permissions': (CMFCorePermissions.View,)
		},)
	
	def getForms(self):
		return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoForm']})
	
	def getForm(self, formname):
		f = self.getFolderContents(contentFilter = {'portal_type' : ['PlominoForm'], 'title' : formname})
		return self._getOb(f[0].id)
	
	def createDocument(self):
		newid = make_uuid()
		self.invokeFactory( type_name='PlominoDocument', id=newid)
		return self._getOb( newid )
		
registerType(PlominoDatabase, PROJECTNAME)
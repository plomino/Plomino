#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo

from Products.CMFPlomino.config import *

class PlominoField(BaseContent):
	""" Plomino Form """
	FIELD_TYPES = [["TEXT", "Text"], ["INTEGER", "Integer"], ["RICHTEXT","Rich text"]]
	
	schema = BaseSchema + Schema((
		StringField('Description', widget=TextAreaWidget(label='Description')),
		StringField('FieldType',widget=SelectionWidget(label='Type'), vocabulary=FIELD_TYPES)
		))
		
	security = ClassSecurityInfo()

	security.declareProtected(DESIGN_PERMISSION, 'update')
	def update(self, **kwargs):
		db = self.getParentDatabase()
		db.Description='yiya'
		db.getIndex().createIndex(self.Title)
		BaseContent.update(self, **kwargs)
			
registerType(PlominoField, PROJECTNAME)
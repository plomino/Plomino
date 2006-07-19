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
	""" Plomino Field """
	FIELD_TYPES = [["TEXT", "Text"], ["INTEGER", "Integer"], ["RICHTEXT","Rich text"]]
	
	schema = BaseSchema + Schema((
		StringField('Description', widget=TextAreaWidget(label='Description')),
		StringField('FieldType',widget=SelectionWidget(label='Type'), vocabulary=FIELD_TYPES)
		))
		
	security = ClassSecurityInfo()

	def at_post_edit_script(self):
		db = self.getParentDatabase()
		#db.Description= 'yi'+self.Title()+'yo'
		db.getIndex().createIndex(self.Title())
	
	def at_post_create_script(self):
		db = self.getParentDatabase()
		db.getIndex().createIndex(self.Title())
        
		
registerType(PlominoField, PROJECTNAME)
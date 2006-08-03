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
	FIELD_TYPES = [["TEXT", "Text"], ["INTEGER", "Integer"], ["RICHTEXT", "Rich text"]]
	FIELD_MODES = [["EDITABLE", "Editable"], ["COMPUTED", "Computed"], ["DISPLAY", "Computed for display"]]
	
	schema = BaseSchema + Schema((
		StringField('Description', widget=TextAreaWidget(label='Description')),
		StringField('FieldType',widget=SelectionWidget(label='Type'), vocabulary=FIELD_TYPES, default="TEXT"),
		StringField('FieldMode',widget=SelectionWidget(label='Mode'), vocabulary=FIELD_MODES, default="EDITABLE"),
		StringField('Formula',widget=TextAreaWidget(label='Formula'))
		))
	
	content_icon = "PlominoField.gif"
	
	security = ClassSecurityInfo()

	def at_post_edit_script(self):
		if not self.getFieldMode()=="DISPLAY":
			db = self.getParentDatabase()
			db.getIndex().createIndex(self.Title())
	
	def at_post_create_script(self):
		if not self.getFieldMode()=="DISPLAY":
			db = self.getParentDatabase()
			db.getIndex().createIndex(self.Title())
        
		
registerType(PlominoField, PROJECTNAME)
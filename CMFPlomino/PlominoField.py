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
	FIELD_TYPES = [
		["TEXT", "Text"],
		["NUMBER", "Number"],
		["RICHTEXT", "Rich text"],
		["DATETIME", "Date/Time"],
		["SELECTION", "Selection list"],
		["MULTISELECTION", "Multi-Selection list"],
		["CHECKBOX", "Check boxes"],
		["RADIO", "Radio buttons"]
		]
	FIELD_MODES = [["EDITABLE", "Editable"], ["COMPUTED", "Computed"], ["DISPLAY", "Computed for display"]]
	
	schema = BaseSchema + Schema((
		StringField('Description', widget=TextAreaWidget(label='Description')),
		StringField('FieldType',widget=SelectionWidget(label='Type'), vocabulary=FIELD_TYPES, default="TEXT"),
		StringField('FieldMode',widget=SelectionWidget(label='Mode'), vocabulary=FIELD_MODES, default="EDITABLE"),
		StringField('Formula',widget=TextAreaWidget(label='Formula')),
		LinesField('SelectionList',widget=LinesWidget(label='Selection list values'))
		))
	
	content_icon = "PlominoField.gif"
	
	security = ClassSecurityInfo()

	def getProperSelectionList(self):
		""" if value not specified (format: label|value), use label as value (return label|label)"""
		s = self.getSelectionList()
		proper = []
		for v in s:
			l = v.split('|')
			if len(l)==2:
				proper.append(v)
			else:
				proper.append(v+'|'+v)
		return proper
	
	def at_post_edit_script(self):
		if not self.getFieldMode()=="DISPLAY":
			db = self.getParentDatabase()
			db.getIndex().createIndex(self.Title())
	
	def at_post_create_script(self):
		if not self.getFieldMode()=="DISPLAY":
			db = self.getParentDatabase()
			db.getIndex().createIndex(self.Title())
        
		
registerType(PlominoField, PROJECTNAME)
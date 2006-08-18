#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

from Products.CMFPlomino.config import PROJECTNAME

class PlominoColumn(BaseContent):
	""" Plomino view column """
	schema = BaseSchema + Schema(
		(StringField('Formula', widget=TextAreaWidget(label='Formula')),
		IntegerField('Position',widget=IntegerWidget(label='Position in view')),
		))
	
	content_icon = "PlominoColumn.gif"
	
	def getColumnName(self):
		return self.Title()
		
	def getParentView(self):
		return self.getParentNode()
		
	def at_post_edit_script(self):
		v = self.getParentView()
		v.declareColumn(self.getColumnName(), self)
	
	def at_post_create_script(self):
		v = self.getParentView()
		v.declareColumn(self.getColumnName(), self)
		
	def manage_beforeDelete(self, item, container):
		v = self.getParentView()
		v.undeclareColumn(self.getColumnName())
		BaseFolder.manage_beforeDelete(self, item, container)
		
registerType(PlominoColumn, PROJECTNAME)
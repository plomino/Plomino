#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

from Products.CMFPlomino.config import PROJECTNAME

class PlominoHidewhen(BaseContent):
	""" Plomino hide-when formula """
	schema = BaseSchema + Schema(
		StringField('Formula',
		widget=TextAreaWidget(label='Formula')
		))
		
	content_icon = "PlominoHidewhen.gif"
		
registerType(PlominoHidewhen, PROJECTNAME)
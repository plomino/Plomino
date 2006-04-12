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
		StringField('Formula',
		widget=TextAreaWidget(label='Formula')
		))
		
registerType(PlominoColumn, PROJECTNAME)
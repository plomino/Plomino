#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions

from Products.CMFPlomino.config import PROJECTNAME

class PlominoField(BaseContent):
	""" Plomino Form """
	schema = BaseSchema + Schema(
		StringField('Description',
		widget=TextAreaWidget(label='Description')
		))
		
registerType(PlominoField, PROJECTNAME)
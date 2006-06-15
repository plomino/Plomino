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
	FIELD_TYPES = [["TEXT", "Text"], ["INTEGER", "Integer"], ["RICHTEXT","Rich text"]]
	
	schema = BaseSchema + Schema((
		StringField('Description', widget=TextAreaWidget(label='Description')),
		StringField('FieldType',widget=SelectionWidget(label='Type'), vocabulary=FIELD_TYPES)
		))
		
		
registerType(PlominoField, PROJECTNAME)
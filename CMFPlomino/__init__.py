#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from Products.CMFPlomino.config import PROJECTNAME, ADD_CONTENT_PERMISSION, SKINS_DIR

def initialize(context):
	##Import Types here to register them
	import PlominoDatabase, PlominoForm, PlominoField, PlominoDocument, PlominoView, PlominoColumn
	
	content_types, constructors, ftis = process_types(listTypes(PROJECTNAME), PROJECTNAME)
	
	registerDirectory(SKINS_DIR, globals())
	
	utils.ContentInit(
		PROJECTNAME + ' Content',
		content_types      = content_types,
		permission         = ADD_CONTENT_PERMISSION,
		extra_constructors = constructors,
		fti                = ftis,
		).initialize(context)
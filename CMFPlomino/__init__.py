#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory

from Products.CMFPlomino.config import PROJECTNAME, ADD_CONTENT_PERMISSION, ADD_DESIGN_PERMISSION, SKINS_DIR

def initialize(context):
	##Import Types here to register them
	import PlominoDatabase, PlominoForm, PlominoField, PlominoDocument, PlominoView, PlominoColumn, PlominoAction
	
	registerDirectory(SKINS_DIR, globals())
	
	content_types, constructors, ftis = process_types(listTypes(PROJECTNAME), PROJECTNAME)
	
	allTypes = zip(content_types, constructors)
	for atype, constructor in allTypes:
		kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
		if atype.archetype_name.find("PlominoDocument")>=0:    
			utils.ContentInit(
				kind,
				content_types      = (atype,),
				permission         = ADD_CONTENT_PERMISSION,
				extra_constructors = (constructor,),
				fti                = ftis,
				).initialize(context)
		else:
			utils.ContentInit(
				kind,
				content_types      = (atype,),
				permission         = ADD_DESIGN_PERMISSION,
				extra_constructors = (constructor,),
				fti                = ftis,
				).initialize(context)

		

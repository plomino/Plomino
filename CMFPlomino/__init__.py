#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from AccessControl.Permission import registerPermissions

from Products.CMFPlomino.config import *

def initialize(context):
	##Import Types here to register them
	import PlominoDatabase, PlominoForm, PlominoField, PlominoDocument, PlominoView, PlominoColumn, PlominoAction, PlominoHidewhen
	
	registerDirectory(SKINS_DIR, globals())
	
	registerPermissions([(ADD_DESIGN_PERMISSION, []), (ADD_CONTENT_PERMISSION, []), (READ_PERMISSION, []), (EDIT_PERMISSION, []), (CREATE_PERMISSION, []), (REMOVE_PERMISSION, []), (DESIGN_PERMISSION, []), (ACL_PERMISSION, [])])
	
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

		

#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName

from Products.CMFPlomino.config import PROJECTNAME, GLOBALS
from StringIO import StringIO

def install(self):
	out = StringIO()
	installTypes(self, out, listTypes(PROJECTNAME), PROJECTNAME)
	install_subskin(self, out, GLOBALS)
	
	propsTool = getToolByName(self, 'portal_properties')
	navtreeProperties = getattr(propsTool, 'navtree_properties')
	typesNotListed = list(navtreeProperties.getProperty('metaTypesNotToList'))
	fieldTypes = ['PlominoForm', 'PlominoField', 'PlominoDocument', 'PlominoColumn', 'PlominoAction', 'PlominoHidewhen']
	for f in fieldTypes:
		if f not in typesNotListed:
			typesNotListed.append(f)
	navtreeProperties.manage_changeProperties(metaTypesNotToList = typesNotListed)

	out.write("Successfully installed %s." % PROJECTNAME)
	return out.getvalue()
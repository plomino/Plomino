#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.CMFCore.utils import getToolByName

from StringIO import StringIO

def install(self):
	out = StringIO()

	propsTool = getToolByName(self, 'portal_properties')
	navtreeProperties = getattr(propsTool, 'navtree_properties')
	typesNotListed = list(navtreeProperties.getProperty('metaTypesNotToList'))
	fieldTypes = ['PlominoForm', 'PlominoField', 'PlominoDocument', 'PlominoColumn', 'PlominoAction', 'PlominoHidewhen', 'PlominoAgent', 'PlominoFile']
	for f in fieldTypes:
		if f not in typesNotListed:
			typesNotListed.append(f)
	out.write(navtreeProperties.getProperty('metaTypesNotToList'))
	navtreeProperties.manage_changeProperties(metaTypesNotToList = typesNotListed)
	out.write("NavTree configuration: OK")
	
	allfieldTypes = ['PlominoDatabase', 'PlominoView', 'PlominoForm', 'PlominoField', 'PlominoDocument', 'PlominoColumn', 'PlominoAction', 'PlominoAgent', 'PlominoHidewhen', 'PlominoAccessControl', 'PlominoFile']
	wfTool = getToolByName(self, 'portal_workflow')
	wfTool.setChainForPortalTypes(pt_names=allfieldTypes, chain='')
	out.write("Workflow configuration cleanup: OK")
		
	return out.getvalue()

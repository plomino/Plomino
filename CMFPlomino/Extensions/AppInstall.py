#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.CMFCore.utils import getToolByName
import transaction

from StringIO import StringIO

def install(self):
	out = StringIO()

	# limit navigation tree entries
	propsTool = getToolByName(self, 'portal_properties')
	navtreeProperties = getattr(propsTool, 'navtree_properties')
	typesNotListed = list(navtreeProperties.getProperty('metaTypesNotToList'))
	fieldTypes = ['PlominoForm', 'PlominoField', 'PlominoDocument', 'PlominoColumn', 'PlominoAction', 'PlominoHidewhen', 'PlominoAgent']
	for f in fieldTypes:
		if f not in typesNotListed:
			typesNotListed.append(f)
	out.write(navtreeProperties.getProperty('metaTypesNotToList'))
	navtreeProperties.manage_changeProperties(metaTypesNotToList = typesNotListed)
	out.write("NavTree configuration: OK")
	
	# remove plone workflow
	allfieldTypes = ['PlominoDatabase', 'PlominoView', 'PlominoForm', 'PlominoField', 'PlominoDocument', 'PlominoColumn', 'PlominoAction', 'PlominoAgent', 'PlominoHidewhen', 'PlominoAccessControl']
	wfTool = getToolByName(self, 'portal_workflow')
	wfTool.setChainForPortalTypes(pt_names=allfieldTypes, chain='')
	out.write("Workflow configuration cleanup: OK")
	
	# re-install kupu to load the customisation policy
	portal = getToolByName(self,'portal_url').getPortalObject()
	quickinstaller = portal.portal_quickinstaller
	print >> out, "(re-)Installing dependency kupu"
	quickinstaller.reinstallProducts(['kupu'])
	transaction.commit()
	
	return out.getvalue()

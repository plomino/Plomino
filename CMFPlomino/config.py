#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################
from AccessControl import ClassSecurityInfo

security = ClassSecurityInfo()

PROJECTNAME = 'CMFPlomino'

security.declarePublic('ADD_DESIGN_PERMISSION')
ADD_DESIGN_PERMISSION = 'CMFPlomino: Add Plomino design elements'
security.declarePublic('ADD_CONTENT_PERMISSION')
ADD_CONTENT_PERMISSION = 'CMFPlomino: Add Plomino content'
security.declarePublic('READ_PERMISSION')
READ_PERMISSION = 'CMFPlomino: Read documents'
security.declarePublic('EDIT_PERMISSION')
EDIT_PERMISSION = 'CMFPlomino: Edit documents'
security.declarePublic('CREATE_PERMISSION')
CREATE_PERMISSION = 'CMFPlomino: Create documents'
security.declarePublic('REMOVE_PERMISSION')
REMOVE_PERMISSION = 'CMFPlomino: Remove documents'
security.declarePublic('DESIGN_PERMISSION')
DESIGN_PERMISSION = 'CMFPlomino: Modify Database design'
security.declarePublic('ACL_PERMISSION')
ACL_PERMISSION = 'CMFPlomino: Control Database ACL'

SKINS_DIR = 'skins'

GLOBALS = globals()
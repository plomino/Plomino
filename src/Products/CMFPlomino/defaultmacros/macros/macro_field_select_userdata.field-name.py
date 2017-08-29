## START selectionlistformula {
from Products.CMFCore.utils import getToolByName
tool = getToolByName(plominoContext, 'portal_memberdata')
ids = tool.propertyIds()
return [''] + ids


## END selectionlistformula }

## START formula {
return 'plone'
## END formula }
## START selectionlistformula {
from Products.CMFCore.utils import getToolByName 
mt = getToolByName(plominoContext, 'portal_membership')
members = mt.listMembers()
users = []
# XXX: Filter by group: {group_filter}
users.extend(['%s|%s' % (member.getProperty('fullname'), member.getId()) for member in members])
return users
## END selectionlistformula }

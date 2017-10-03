## START formula {
DEFAULT_DATA_SOURCE = 'plone'

PLONE = """
script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)

from Products.CMFCore.utils import getToolByName 
mt = getToolByName(plominoContext, 'portal_membership')
members = mt.listMembers()
users = []
# XXX: Filter by group: {group_filter}
users.extend(['%s|%s' % (member.getProperty('fullname'), member.getId()) for member in members])
return users
"""

doc = plominoContext
data_source = doc.getItem('data-source', DEFAULT_DATA_SOURCE)
group_filter = doc.getItem('group-filter')

# We only handle Plone as a data-source for now
if data_source == 'plone':
    code = PLONE.format(group_filter=group_filter)
else:
    # We shouldn't get here
    code = ''
return code



## END formula }
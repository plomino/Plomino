## START formula {
## START formula {

PLONE = """

member_id = \"\"\"{member_id}\"\"\"
field_name = \"\"\"{field_name}\"\"\"
value_if_empty = \"\"\"{value_if_empty}\"\"\"

from Products.CMFCore.utils import getToolByName 
mt = getToolByName(plominoContext, 'portal_membership') 
member = mt.getMemberById(member_id)

value = member.getProperty(field_name)
return value or value_if_empty
"""

doc = plominoContext
member_id = doc.getItem('userlist', '')
field_name = doc.getItem('field-name')
value_if_empty = doc.getItem('value-if-empty', '')

# We only handle Plone as a data-source for now
code = PLONE.format(field_name=field_name, member_id=member_id, value_if_empty=value_if_empty)

return code
## END formula }
## END formula }

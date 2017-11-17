## START formula {
PLONE = """

member_id = \"\"\"{member_id}\"\"\"
field_name = \"\"\"{field_name}\"\"\"
value_to_compare = \"\"\"{value_to_compare}\"\"\"

from Products.CMFCore.utils import getToolByName 
mt = getToolByName(plominoContext, 'portal_membership') 
member = mt.getMemberById(member_id)

value = member.getProperty(field_name)
return value is not None and value_to_compare is not None and value == value_to_compare
"""

doc = plominoContext
member_id = doc.getItem('userlist', '')
field_name = doc.getItem('field-name')
value_to_compare = doc.getItem('value-to-compare', '')

# We only handle Plone as a data-source for now
code = PLONE.format(field_name=field_name, member_id=member_id, value_to_compare=value_to_compare)

return code


## END formula }
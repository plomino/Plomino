## START formula {
DEFAULT_DATA_SOURCE = 'plone'

PLONE = """
script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
value_if_anonymous = \"\"\"{value_if_anonymous}\"\"\"
field_name = \"\"\"{field_name}\"\"\"
value_if_empty = \"\"\"{value_if_empty}\"\"\"

from Products.CMFCore.utils import getToolByName 
mt = getToolByName(plominoContext, 'portal_membership') 
if  mt.isAnonymousUser(): 
    return value_if_anonymous

member = mt.getAuthenticatedMember()

value = member.getProperty(field_name)
return value or value_if_empty
"""

doc = plominoContext
data_source = doc.getItem('data-source', DEFAULT_DATA_SOURCE)
field_name = doc.getItem('field-name')
value_if_empty = doc.getItem('value-if-empty', '')
value_if_anonymous = doc.getItem('value-if-anonymous', '')

# We only handle Plone as a data-source for now
if data_source == 'plone':
    code = PLONE.format(field_name=field_name, value_if_anonymous=value_if_anonymous, value_if_empty=value_if_empty)
else:
    # We shouldn't get here
    code = ''
return code



## END formula }

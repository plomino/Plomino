## START formula {
doc = plominoContext
field_name_ = doc.getItem('field_name')
code = """
db = plominoContext.getParentDatabase()
mt = db.portal_membership
field_name = \"\"\"{field_name}\"\"\"
if not mt.isAnonymousUser():
    current_id = plominoContext.getCurrentUserId()
    if current_id:
        plominoContext.setItem(field_name, current_id)
""".format(field_name=field_name_)
return code

## END formula }

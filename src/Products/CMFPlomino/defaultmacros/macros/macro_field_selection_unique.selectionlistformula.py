## START formula {
field_id = plominoDocument.getItem('field_id')
code = """
field_id = '{field_id}'
if field_id =='@@CURRENT_FIELD':
    script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
    field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
db = plominoContext.getParentDatabase()
index = db.getIndex()
try:
    return index.getKeyUniqueValues(field_id)
except:
    Log('Field index %s not exist' % field_id)
    raise
""" .format(field_id = field_id)
return code
## END formula }
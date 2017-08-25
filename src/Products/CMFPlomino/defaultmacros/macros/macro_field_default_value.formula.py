## START formula {
defaultvalue = plominoContext.getItem('defaultvalue','')
code = """
script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
if not plominoContext.getItem(field_id):
    return '{defaultvalue}'
return plominoContext.getItem(field_id)
""" .format(defaultvalue=defaultvalue)

return code


## END formula }

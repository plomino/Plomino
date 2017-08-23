## START formula {
code = """
script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
value = plominoContext.getItem(field_id)
return value is None or value is False or (isinstance(value, basestring) and len(value.strip())==0)
"""
return code

## END formula }

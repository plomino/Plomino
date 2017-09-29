## START formula {
field_id = plominoContext.getItem('field_id')
code = """
field_id = '{field_id}'
if field_id =='@@CURRENT_FIELD':
    script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
    field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
value = plominoContext.getItem(field_id)
return is_email(value)
""" .format(field_id=field_id)
return code



## END formula }

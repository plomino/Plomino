## START formula {
doc = plominoContext
field_name_ = doc.getItem('field_name')
field_value_ = doc.getItem('field_value')
form_error_message_ = doc.getItem('form_error_message')
code = """
script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
value = plominoContext.getItem(field_id, '')
field_name = \"\"\"{field_name}\"\"\"
field_value = \"\"\"{field_value}\"\"\"
field_result = plominoContext.getItem(field_name)
if field_result == field_value and value == '':
    return \"\"\"{form_error_message}\"\"\"
""".format(
    field_name=field_name_,
    field_value=field_value_,
    form_error_message=form_error_message_
)
return code




## END formula }
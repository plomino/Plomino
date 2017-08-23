## START formula {
doc = plominoContext
min_ = doc.getItem('min', False)
max_ = doc.getItem('max', False)
form_error_message_ = doc.getItem('form_error_message')
code = """
script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
value = plominoContext.getItem(field_id)
min_value = {min}
max_value = {max}
form_error_message = \"\"\"{form_error_message}\"\"\"
if min_value != False and max_value == False:
    if value < min_value:
        return form_error_message
elif max_value != False and min_value == False:
    if value > max_value:
        return form_error_message
elif min_value != False and max_value != False:
    if value < min_value or value > max_value:
        return form_error_message
""".format(
    min=min_,
    max=max_,
    form_error_message=form_error_message_
)
return code


## END formula }

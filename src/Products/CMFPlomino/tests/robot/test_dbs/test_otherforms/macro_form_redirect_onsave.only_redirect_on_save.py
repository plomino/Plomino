## START formula {

### START macro_field_default_value_2 ###

script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
if not plominoContext.getItem(field_id):
    return 'True'
return plominoContext.getItem(field_id)

### END macro_field_default_value_2 ###
## END formula }
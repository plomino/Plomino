## START formula {

### START macro_condition_field_empty_2 ###
def macro_condition_field_empty_2():
    field_id = '@@CURRENT_FIELD'
    if field_id =='@@CURRENT_FIELD':
        script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
        field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
    value = plominoContext.getItem(field_id)
    return value is None or value is False or (isinstance(value, basestring) and len(value.strip())==0)

### END macro_condition_field_empty_2 ###
### START macro_field_default_value_3 ###
if macro_condition_field_empty_2():

    script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
    field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
    if not plominoContext.getItem(field_id):
        return 'save'
    return plominoContext.getItem(field_id)

### END macro_field_default_value_3 ###
## END formula }
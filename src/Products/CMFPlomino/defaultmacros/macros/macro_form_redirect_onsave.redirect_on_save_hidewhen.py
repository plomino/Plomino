## START formula {


### START macro_condition_field_got_substring_3 ###
def macro_condition_field_got_substring_3():
    field_name = """redirect_event"""
    if field_name =='@@CURRENT_FIELD':
        script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
        field_name, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
    field_value = """save"""
    field_result = plominoContext.getItem(field_name)
    form = plominoContext.getForm()
    field = getattr(form, field_name)
    if field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
        field_result = form.computeFieldValue(field_name, plominoContext)
    result = field_value in str(field_result)
    return result

### END macro_condition_field_got_substring_3 ###
### START macro_hidewhen_show_2 ###
if macro_condition_field_got_substring_3():

    return False

### END macro_hidewhen_show_2 ###
### START macro_hidewhen_hide_2 ###

return True

### END macro_hidewhen_hide_2 ###
## END formula }
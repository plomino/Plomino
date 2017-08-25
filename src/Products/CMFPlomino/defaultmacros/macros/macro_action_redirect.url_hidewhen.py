## START formula {
### START macro_condition_field_got_substring_1 ###
def macro_condition_field_got_substring_1():
    
    field_name = """redirect_type"""
    field_value = """url"""
    if not plominoContext.hasItem(field_name):
        return False
    field_result = plominoContext.getItem(field_name)
    if field_name != 'Form':
        form = plominoContext.getForm()
        field = getattr(form, field_name)
        if field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
            field_result = form.computeFieldValue(field_name, plominoContext)
    result = field_value in str(field_result)
    return result
        

### END macro_condition_field_got_substring_1 ###
### START macro_hidewhen_show_1 ###
if macro_condition_field_got_substring_1():
    
    return False
    

### END macro_hidewhen_show_1 ###
### START macro_hidewhen_hide_1 ###

return True

### END macro_hidewhen_hide_1 ###


## END formula }

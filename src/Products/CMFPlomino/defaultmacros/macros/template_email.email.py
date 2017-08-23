## START validation_formula {
### START macro_condition_field_text_validate_email_1 ###
def macro_condition_field_text_validate_email_1():
    
    script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
    field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
    value = plominoContext.getItem(field_id)
    return is_email(value)
    

### END macro_condition_field_text_validate_email_1 ###
### START macro_field_validate_valid_1 ###
if macro_condition_field_text_validate_email_1():
    
    return
    

### END macro_field_validate_valid_1 ###
### START macro_field_validate_invalid_1 ###

return '''This email address is not valid.'''

### END macro_field_validate_invalid_1 ###


## END validation_formula }

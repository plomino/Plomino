## START formula {
doc = plominoContext
field_id_ = doc.getItem('field_id')
less_field_value_ = doc.getItem('less_field_value', '')
and_or_ = doc.getItem('and_or')
more_field_value_ = doc.getItem('more_field_value', '')
if less_field_value_ != '' and more_field_value_ == '':
    code = """
field_id = '{field_id}'
if field_id =='@@CURRENT_FIELD':
    script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
    field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
less_field_result = plominoContext.getItem(field_id)
form = plominoContext.getForm()
lf_field = getattr(form, field_id, None)
if lf_field is None:
    return False
if lf_field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
    try:
        less_field_result = float(form.computeFieldValue(field_id, plominoContext))
    except ValueError:
        less_field_result = 0
result = less_field_result < {less_field_value}
return result
    """.format(
        field_id=field_id_,
        less_field_value=less_field_value_
    )
elif more_field_value_ != '' and less_field_value_ == '':
    code = """
field_id = '{field_id}'
if field_id =='@@CURRENT_FIELD':
    script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
    field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
more_field_result = plominoContext.getItem(field_id)
form = plominoContext.getForm()
mf_field = getattr(form, field_id, None)
if mf_field is None:
    return False
if mf_field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
    try:
        more_field_result = float(form.computeFieldValue(field_id, plominoContext))
    except ValueError:
        more_field_result = 0
result = more_field_result > {more_field_value}
return result
    """.format(
        field_id=field_id_,
        more_field_value=more_field_value_
    )
else:
    code = """
field_id = '{field_id}'
if field_id =='@@CURRENT_FIELD':
    script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
    field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
less_field_result = plominoContext.getItem(field_id)
more_field_result = plominoContext.getItem(field_id)
form = plominoContext.getForm()
lf_field = getattr(form, field_id, None)
if lf_field is None:
    return False
if lf_field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
    try:
        less_field_result = float(form.computeFieldValue(field_id, plominoContext))
    except ValueError:
        less_field_result = 0
mf_field = getattr(form, field_id, None)
if mf_field is None:
    return False
if mf_field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
    try:
        more_field_result = float(form.computeFieldValue(field_id, plominoContext))
    except ValueError:
        more_field_result = 0
result = less_field_result < {less_field_value} {and_or} more_field_result > {more_field_value}
return result
    """.format(
        field_id=field_id_,
        less_field_value=less_field_value_,
        and_or=and_or_,
        more_field_value=more_field_value_
    )
return code



## END formula }
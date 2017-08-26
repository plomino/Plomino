## START formula {
doc = plominoContext
less_field_name_ = doc.getItem('less_field_name')
less_field_value_ = doc.getItem('less_field_value', '')
and_or_ = doc.getItem('and_or')
more_field_name_ = doc.getItem('more_field_name')
more_field_value_ = doc.getItem('more_field_value', '')
if less_field_value_ != '' and more_field_value_ == '':
    code = """
less_field_name = \"\"\"{less_field_name}\"\"\"
if not plominoContext.hasItem(less_field_name):
    return False
less_field_result = plominoContext.getItem(less_field_name)
form = plominoContext.getForm()
lf_field = getattr(form, less_field_name)
if lf_field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
    try:
        less_field_result = float(form.computeFieldValue(less_field_name, plominoContext))
    except ValueError:
        less_field_result = 0
result = less_field_result < {less_field_value}
return result
    """.format(
        less_field_name=less_field_name_,
        less_field_value=less_field_value_
    )
elif more_field_value_ != '' and less_field_value_ == '':
    code = """
more_field_name = \"\"\"{more_field_name}\"\"\"
if not plominoContext.hasItem(more_field_name):
    return False
more_field_result = plominoContext.getItem(more_field_name)
form = plominoContext.getForm()
mf_field = getattr(form, more_field_name)
if mf_field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
    try:
        more_field_result = float(form.computeFieldValue(more_field_name, plominoContext))
    except ValueError:
        more_field_result = 0
result = more_field_result > {more_field_value}
return result
    """.format(
        more_field_name=more_field_name_,
        more_field_value=more_field_value_
    )
else:
    code = """
less_field_name = \"\"\"{less_field_name}\"\"\"
if not plominoContext.hasItem(less_field_name):
    return False
less_field_result = plominoContext.getItem(less_field_name)
more_field_name = \"\"\"{more_field_name}\"\"\"
if not plominoContext.hasItem(more_field_name):
    return False
more_field_result = plominoContext.getItem(more_field_name)
form = plominoContext.getForm()
lf_field = getattr(form, less_field_name)
if lf_field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
    try:
        less_field_result = float(form.computeFieldValue(less_field_name, plominoContext))
    except ValueError:
        less_field_result = 0
mf_field = getattr(form, more_field_name)
if mf_field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
    try:
        more_field_result = float(form.computeFieldValue(more_field_name, plominoContext))
    except ValueError:
        more_field_result = 0
result = less_field_result < {less_field_value} {and_or} more_field_result > {more_field_value}
return result
    """.format(
        less_field_name=less_field_name_,
        less_field_value=less_field_value_,
        and_or=and_or_,
        more_field_name=more_field_name_,
        more_field_value=more_field_value_
    )
return code



## END formula }

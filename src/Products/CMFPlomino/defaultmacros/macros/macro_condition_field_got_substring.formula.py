## START formula {
doc = plominoContext
field_name_ = doc.getItem('field_name')
field_compare_ = doc.getItem('field_compare')
field_value_ = doc.getItem('field_value')
value_type_ = doc.getItem('value_type')
code = ''
if value_type_ == 'text':
    code = """
field_name = \"\"\"{field_name}\"\"\"
field_value = \"\"\"{field_value}\"\"\"
field_result = plominoContext.getItem(field_name)
form = plominoContext.getForm()
field = getattr(form, field_name)
if field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
    field_result = form.computeFieldValue(field_name, plominoContext)
result = field_value {field_compare} str(field_result)
return result
    """.format(
        field_name=field_name_,
        field_compare=field_compare_,
        field_value=field_value_
    )
elif value_type_ == 'regex' and field_compare_ == 'in':
    code = """
import re
field_name = \"\"\"{field_name}\"\"\"
field_value = \"\"\"{field_value}\"\"\"
field_result = plominoContext.getItem(field_name)
form = plominoContext.getForm()
field = getattr(form, field_name)
if field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
    field_result = form.computeFieldValue(field_name, plominoContext)
result = re.search(field_value, field_result)
return result
    """.format(
        field_name=field_name_,
        field_value=field_value_
    )
elif value_type_ == 'regex' and field_compare_ == 'not in':
    code = """
import re
field_name = \"\"\"{field_name}\"\"\"
field_value = \"\"\"{field_value}\"\"\"
field_result = plominoContext.getItem(field_name)
form = plominoContext.getForm()
field = getattr(form, field_name)
if field.field_mode in ["COMPUTED","COMPUTEDONSAVE"]:
    field_result = form.computeFieldValue(field_name, plominoContext)
result = re.search(field_value, field_result)
return not result
    """.format(
        field_name=field_name_,
        field_value=field_value_
    )
return code

## END formula }

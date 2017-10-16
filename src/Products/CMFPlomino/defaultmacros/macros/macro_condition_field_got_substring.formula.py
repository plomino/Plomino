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
if field_name =='@@CURRENT_FIELD':
    script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
    field_name, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
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
if field_name =='@@CURRENT_FIELD':
    script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
    field_name, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
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
if field_name =='@@CURRENT_FIELD':
    script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
    field_name, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
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
## START document_title {
doc = plominoContext
field_name_ = doc.getItem('field_name', '')
field_compare_ = doc.getItem('field_compare', '')
field_value_ = doc.getItem('field_value', '')
value_type_ = doc.getItem('value_type', '')
code = 'Field contains text'

if not (field_name_ and field_compare_ and field_value_ and value_type_):
    return code

value_type = 'pattern'
if value_type_ == 'text':
    value_type = ''
code = '"{field_name}" {field_compare} {field_value} {value_type}'.format(
    field_name=field_name_,
    field_compare=field_compare_,
    field_value=field_value_,
    value_type=value_type
)
return code
## END document_title }

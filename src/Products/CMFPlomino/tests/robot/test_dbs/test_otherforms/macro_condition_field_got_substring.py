## START document_title {

MAX_LEN = 30
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
if len(code) > MAX_LEN:
    code = code[:MAX_LEN] + "..."
return code
## END document_title }


## START formula {
doc = plominoContext
field_name_ = doc.getItem('field_name')
datetime_format_ = doc.getItem('datetime_format')
code = """
field_name = \"\"\"{field_name}\"\"\"
datetime_format = \"\"\"{datetime_format}\"\"\"
field_result = plominoContext.getItem(field_name)
result = str(field_result)
if datetime_format:
    try:
        result = DateToString(field_result, format=datetime_format)
    except:
        result = str(field_result)
return result
""".format(
    field_name=field_name_,
    datetime_format=datetime_format_
)
return code


## END formula }

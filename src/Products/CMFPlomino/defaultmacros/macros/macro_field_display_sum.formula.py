## START formula {
doc = plominoContext
fields_name_ = doc.getItem('fields_name', [])
code = """
fields = {fields_name}
total = 0
for field in fields:
    field_value = plominoContext.getItem(field, 0)
    try:
        total += float(field_value)
    except ValueError:
        continue
return str(total)
""".format(
    fields_name=fields_name_
)
return code


## END formula }

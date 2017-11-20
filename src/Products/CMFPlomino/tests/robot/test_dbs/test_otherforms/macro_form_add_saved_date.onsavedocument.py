## START formula {
doc = plominoContext
field_name_ = doc.getItem('field_name')
code = """
field_name = \"\"\"{field_name}\"\"\"
plominoContext.setItem(field_name, Now())
""".format(field_name=field_name_)
return code




## END formula }
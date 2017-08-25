## START formula {
field_id = plominoContext.getItem('field_id')
code = """
value = plominoDocument.getItem('{field_id}')
return is_email(value)
""" .format(field_id=field_id)
return code



## END formula }

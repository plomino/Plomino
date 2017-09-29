## START formula {
doc = plominoContext
field_id = doc.getItem('field_id')
count_type_ = doc.getItem('count_type')
total_count_ = doc.getItem('total_count')
length_format_ = doc.getItem('length_format')
default_code = """
field_id = '{field_id}'
if field_id =='@@CURRENT_FIELD':
    script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
    field_id, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
value = plominoContext.getItem(field_id)
""".format(field_id = field_id)
word_code = """
adjust_strs = []
for item in value:
    if item.isalnum() or item.isspace():
        adjust_strs.append(item)
    else:
        adjust_strs.append(' ')
new_strs = "".join(adjust_strs)
"""
if count_type_ == 'chars':
    if length_format_ == 'fixed':
        code = default_code + """
return len(value) == {total_count}
        """.format(
            total_count=total_count_
        )
    elif length_format_ == 'variable':
        code = default_code + """
return len(value) < {total_count}
        """.format(
            total_count=total_count_
        )
elif count_type_ == 'words':
    if length_format_ == 'fixed':
        code = default_code + word_code + """
return len(new_strs.split()) == {total_count}
        """.format(
            total_count=total_count_
        )
    elif length_format_ == 'variable':
        code = default_code + word_code + """
return len(new_strs.split()) < {total_count}
        """.format(
            total_count=total_count_
        )
return code



## END formula }

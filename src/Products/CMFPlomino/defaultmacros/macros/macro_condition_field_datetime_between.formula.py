## START formula {
doc = plominoContext
field_name_ = doc.getItem('field_name', '')
min_option_ = doc.getItem('min_option', '')
max_option_ = doc.getItem('max_option', '')
min_datetime_ = doc.getItem('min_datetime')
max_datetime_ = doc.getItem('max_datetime')
code = """
field_name = '{field_name}'
if field_name =='@@CURRENT_FIELD':
    script_type, form_id, rest = script_id.split(SCRIPT_ID_DELIMITER, 2)
    field_name, formula = rest.rsplit(SCRIPT_ID_DELIMITER, 1)
field_result = plominoContext.getItem(field_name)
min_option = '{min_option}'
max_option = '{max_option}'
min_datetime = ''
if min_option == 'pick':
    min_datetime = '{min_datetime}'
    if min_datetime and isinstance(min_datetime, basestring):
        min_datetime = StringToDate(min_datetime)
elif min_option == 'now':
    min_datetime = Now()
max_datetime = ''
if max_option == 'pick':
    max_datetime = '{max_datetime}'
    if max_datetime and isinstance(max_datetime, basestring):
        max_datetime = StringToDate(max_datetime)
elif max_option == 'now':
    max_datetime = Now()
if min_datetime and not max_datetime:
    return min_datetime < field_result
elif max_datetime and not min_datetime:
    return field_result < max_datetime
elif min_datetime and max_datetime:
    return field_result > min_datetime and field_result < max_datetime
else:
    return True
""".format(
    field_name=field_name_,
    min_option=min_option_,
    max_option=max_option_,
    min_datetime=min_datetime_,
    max_datetime=max_datetime_
)
return code
## END formula }


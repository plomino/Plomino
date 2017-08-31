## START document_title {
doc = plominoContext
field_name_ = doc.getItem('field_name', '')
min_option_ = doc.getItem('min_option', '')
max_option_ = doc.getItem('max_option', '')
min_datetime_ = doc.getItem('min_datetime')
max_datetime_ = doc.getItem('max_datetime')
min_datetime = ''
if min_option_ == 'pick':
    min_datetime = min_datetime_
    if min_datetime and isinstance(min_datetime, basestring):
        min_datetime = StringToDate(min_datetime)
    if min_datetime:
        min_datetime = DateToString(min_datetime, format='%d %b %Y')
elif min_option_ == 'now':
    min_datetime = 'past'
max_datetime = ''
if max_option_ == 'pick':
    max_datetime = max_datetime_
    if max_datetime and isinstance(max_datetime, basestring):
        max_datetime = StringToDate(max_datetime)
    if max_datetime:
        max_datetime = DateToString(max_datetime, format='%d %b %Y')
elif max_option_ == 'now':
    max_datetime = 'future'
if min_datetime and not max_datetime:
    return '{min_datetime} < {field_name}'.format(
        min_datetime=min_datetime,
        field_name=field_name_)
elif max_datetime and not min_datetime:
    return '{field_name} < {max_datetime}'.format(
        max_datetime=max_datetime,
        field_name=field_name_)
elif min_datetime and max_datetime:
    return '{min_datetime} < {field_name} < {max_datetime}'.format(
        min_datetime=min_datetime,
        max_datetime=max_datetime,
        field_name=field_name_)
else:
    return '{field_name} is any date'.format(
        field_name=field_name_)




## END document_title }

## START formula {
doc = plominoContext
datetime_format_ = doc.getItem('datetime_format')
code = """
datetime_format = \"\"\"{datetime_format}\"\"\"
from DateTime import DateTime
now = DateTime()
return DateToString(now, datetime_format)
""".format(
    datetime_format=datetime_format_
)
return code




## END formula }
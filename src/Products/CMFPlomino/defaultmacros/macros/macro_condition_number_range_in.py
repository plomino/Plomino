## START document_title {
doc = plominoContext
less_field_name_ = doc.getItem('less_field_name')
less_field_value_ = doc.getItem('less_field_value', '')
and_or_ = doc.getItem('and_or')
more_field_name_ = doc.getItem('more_field_name')
more_field_value_ = doc.getItem('more_field_value', '')
code = "Number in range"

if less_field_value_ != '' and more_field_value_ == '':
    code = """{less_field_name} < {less_field_value}""".format(
        less_field_name=less_field_name_,
        less_field_value=less_field_value_
    )
    return code

elif more_field_value_ != '' and less_field_value_ == '':
    code = """{more_field_name} > {more_field_value}""".format(
        more_field_name=more_field_name_,
        more_field_value=more_field_value_
    )
    return code
    
else:
    code = """{less_field_name} < {less_field_value} {and_or} {more_field_name} > {more_field_value}""".format(
        less_field_name=less_field_name_,
        less_field_value=less_field_value_,
        and_or=and_or_,
        more_field_name=more_field_name_,
        more_field_value=more_field_value_
    )
    return code

return code




## END document_title }

## START formula {
doc = plominoContext
redirect_type_ = doc.getItem('redirect_type')
form_redirect_ = doc.getItem('form_redirect')
view_redirect_ = doc.getItem('view_redirect')
url_redirect_ = doc.getItem('url_redirect')
request_value_ = doc.getItem('request_value')
code = ''
if redirect_type_ == 'form':
    code = """
db = plominoContext.getParentDatabase()
req = getattr(plominoContext, 'REQUEST')
form_redirect = \"\"\"{form_redirect}\"\"\"
targeturl = '%s/%s' % (db.absolute_url(), form_redirect)
if '{request_value}' in req:
    req.RESPONSE.redirect(targeturl)
    """.format(
    form_redirect=form_redirect_,
    request_value=request_value_
)
elif redirect_type_ == 'view':
    code = """
db = plominoContext.getParentDatabase()
req = getattr(plominoContext, 'REQUEST')
view_redirect = \"\"\"{view_redirect}\"\"\"
targeturl = '%s/%s' % (db.absolute_url(), view_redirect)
if '{request_value}' in req:
    req.RESPONSE.redirect(targeturl)
    """.format(
    view_redirect=view_redirect_,
    request_value=request_value_
)
elif redirect_type_ == 'url':
    code = """
db = plominoContext.getParentDatabase()
req = getattr(plominoContext, 'REQUEST')
url_redirect = \"\"\"{url_redirect}\"\"\"
targeturl = '%s' % url_redirect
if '{request_value}' in req:
    req.RESPONSE.redirect(targeturl)
    """.format(
    url_redirect=url_redirect_,
    request_value=request_value_
)
return code




## END formula }
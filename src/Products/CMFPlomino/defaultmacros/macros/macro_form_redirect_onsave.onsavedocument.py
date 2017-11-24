## START formula {
doc = plominoContext
retain_form_data_ = doc.getItem('retain_form_data')
redirect_type_ = doc.getItem('redirect_type')
form_redirect_ = doc.getItem('form_redirect')
view_redirect_ = doc.getItem('view_redirect')
url_redirect_ = doc.getItem('url_redirect')
only_redirect_on_save_ = doc.getItem('only_redirect_on_save', False)
code = ''
if redirect_type_ == 'form':
    code = """
db = plominoContext.getParentDatabase()
req = getattr(plominoContext, 'REQUEST')
form_redirect = '{form_redirect}'
retain_form_data = '{retain_form_data}'
only_redirect_on_save = '{only_redirect_on_save}'
if only_redirect_on_save=='True':
    if retain_form_data=='True':
        targeturl='%s/%s?%s' % (db.absolute_url(),form_redirect,'ignore_actions=1')
        req.response.setHeader('Plomino-Retain-Form-Data','True')
    else:
        targeturl = '%s/%s' % (db.absolute_url(), form_redirect)
else:
    targeturl = ''
return targeturl
""".format(
    form_redirect=form_redirect_,retain_form_data=retain_form_data_, only_redirect_on_save=only_redirect_on_save_
)
elif redirect_type_ == 'view':
    code = """
db = plominoContext.getParentDatabase()
req = getattr(plominoContext, 'REQUEST')
view_redirect = \"\"\"{view_redirect}\"\"\"
targeturl = '%s/%s' % (db.absolute_url(), view_redirect)
return targeturl
""".format(
    view_redirect=view_redirect_
)
elif redirect_type_ == 'url':
    code = """
db = plominoContext.getParentDatabase()
req = getattr(plominoContext, 'REQUEST')
url_redirect = \"\"\"{url_redirect}\"\"\"
targeturl = '%s' % url_redirect
return targeturl
""".format(
    url_redirect=url_redirect_
)
return code
## END formula }
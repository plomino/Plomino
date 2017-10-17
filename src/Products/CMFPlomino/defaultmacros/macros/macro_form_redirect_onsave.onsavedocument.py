## START formula {
doc = plominoContext
enable_attach_doc_id_ = doc.getItem('enable_attach_doc_id')
redirect_type_ = doc.getItem('redirect_type')
form_redirect_ = doc.getItem('form_redirect')
view_redirect_ = doc.getItem('view_redirect')
url_redirect_ = doc.getItem('url_redirect')
code = ''
if redirect_type_ == 'form':
    code = """
db = plominoContext.getParentDatabase()
req = getattr(plominoContext, 'REQUEST')
form_redirect = '{form_redirect}'
enable_attach_doc_id = '{enable_attach_doc_id}'
targeturl = '%s/%s' % (db.absolute_url(), form_redirect)
if enable_attach_doc_id=='True':
    targeturl='%s/document/%s?openwithform=%s' % (db.absolute_url(), plominoDocument.id, form_redirect)
return targeturl
    """.format(
    form_redirect=form_redirect_,enable_attach_doc_id=enable_attach_doc_id_
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
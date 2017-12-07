## START formula {
doc = plominoContext
retain_form_data_ = doc.getItem('retain_form_data')
redirect_type_ = doc.getItem('redirect_type')
form_redirect_ = doc.getItem('form_redirect')
redirect_event_ = doc.getItem('redirect_event', '')
code = ''
if redirect_type_ == 'form' and redirect_event_=='load':
    code = """
db = plominoContext.getParentDatabase()
req = getattr(plominoContext, 'REQUEST')
form_redirect = '{form_redirect}'
redirect_event = '{redirect_event}'
retain_form_data = '{retain_form_data}'
editpath = plominoContext.REQUEST.get('Plomino_Macro_Context')
editcontext = plominoContext.restrictedTraverse(editpath)
ctype = editcontext.getPortalTypeName()
if ctype=='PlominoForm':
    if retain_form_data=='True':
        targeturl='%s/%s?%s&%s' % (db.absolute_url(),form_redirect,req["QUERY_STRING"],'ignore_actions=1')
    else:
        targeturl = '%s/%s?%s' % (db.absolute_url(), form_redirect,form_redirect,req["QUERY_STRING"])
    req.response.redirect(targeturl, status=307)
    return req.response
else:
    return None
    """.format(
    form_redirect=form_redirect_,retain_form_data=retain_form_data_
)
return code
## END formula }
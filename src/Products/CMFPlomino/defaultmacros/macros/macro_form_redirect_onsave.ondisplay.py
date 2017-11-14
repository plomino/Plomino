## START formula {
doc = plominoContext
retain_form_data_ = doc.getItem('retain_form_data')
redirect_type_ = doc.getItem('redirect_type')
form_redirect_ = doc.getItem('form_redirect')
only_redirect_on_save_ = doc.getItem('only_redirect_on_save', False)
code = ''
if redirect_type_ == 'form':
    code = """
db = plominoContext.getParentDatabase()
req = getattr(plominoContext, 'REQUEST')
form_redirect = '{form_redirect}'
only_redirect_on_save = '{only_redirect_on_save}'
retain_form_data = '{retain_form_data}'
editpath = plominoContext.REQUEST.get('Plomino_Macro_Context')
editcontext = plominoContext.restrictedTraverse(editpath)
ctype = editcontext.getPortalTypeName()
if ctype=='PlominoForm' and only_redirect_on_save=='False':
    if retain_form_data=='True':
        targeturl='%s/%s?%s' % (db.absolute_url(),form_redirect,req["QUERY_STRING"])
    else:
        targeturl = '%s/%s' % (db.absolute_url(), form_redirect)
    req.response.setHeader('Plomino-Redirect',targeturl)
    return req.response
else:
    return None
    """.format(
    form_redirect=form_redirect_,retain_form_data=retain_form_data_, only_redirect_on_save =  only_redirect_on_save_
)
return code
## END formula }
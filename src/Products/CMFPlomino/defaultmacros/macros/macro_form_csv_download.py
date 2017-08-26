## START onSaveDocument {
view_redirect_ = plominoContext.getItem('view_redirect')
code = """
db = plominoContext.getParentDatabase()
req = getattr(plominoContext, 'REQUEST')
link = "{{db_url}}/{{view_id}}/exportCSV?displayColumnsTitle=True&separator=%2C".format(
    db_url=db.absolute_url(),
    view_id=\"\"\"{view_redirect}\"\"\")
req.RESPONSE.redirect(link)
""".format(view_redirect=view_redirect_)
plominoDocument.setItem('onDisplay', code)



## END onSaveDocument }

## START formula {
view_redirect_ = plominoContext.getItem('view_redirect')
code = """
db = plominoContext.getParentDatabase()
link = "{{db_url}}/{{view_id}}/exportCSV?displayColumnsTitle=True&separator=%2C".format(
    db_url=db.absolute_url(),
    view_id=\"\"\"{view_redirect}\"\"\")
return link
""".format(view_redirect=view_redirect_)
return code
## END formula }

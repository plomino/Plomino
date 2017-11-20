## START formula {
form_id = plominoDocument.getItem("formlist", "")
code = """
form_id = "{form_id}"
if not form_id:
    return False
doc_form = plominoDocument.getForm()
if doc_form and doc_form.id == form_id:
    return True
return False
""" .format(form_id=form_id)
return code




## END formula }
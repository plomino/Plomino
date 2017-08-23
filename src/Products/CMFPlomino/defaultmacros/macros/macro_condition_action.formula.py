## START formula {
doc = plominoContext
action_id_ = doc.getItem('action_id')

code = """
action_id = \"\"\"{action_id}\"\"\"
request = plominoContext.REQUEST
if request.get(action_id):
    return True
return False
    """.format(
        action_id=action_id_,
    )
return code
## END formula }

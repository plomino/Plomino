## START formula {
doc = plominoContext
message_type_ = doc.getItem('message_type')
message_ = doc.getItem('message')
code = ''
if message_type_ == 'info':
    code = """
db = plominoContext.getParentDatabase()
req = getattr(plominoContext, 'REQUEST')
message = \"\"\"{message}\"\"\"
db.writeMessageOnPage(message, req)
    """.format(
    message=message_
)
elif message_type_ == 'error':
    code = """
db = plominoContext.getParentDatabase()
req = getattr(plominoContext, 'REQUEST')
message = \"\"\"{message}\"\"\"
db.writeMessageOnPage(message, req, error=True)
    """.format(
    message=message_
)
return code
## END formula }

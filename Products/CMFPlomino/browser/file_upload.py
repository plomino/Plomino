"""
Helper view for file upload.
"""
from zope.browser.interfaces import IBrowserView
from zope.interface import implements
from Products.CMFPlomino.interfaces import IPlominoDocument
from uuid import uuid1
import json


class UploadToSession(object):
    implements(IBrowserView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """Store the files provided in the request in the current PlominoDocument.
           If the context is a PlominoForm it means there is no PlominoDocument yet,
           and we'll store the file in the user session.
        """
        self.request.response.setHeader("Content-type", "application/json")
        for key, val in self.request.form.items():
            if hasattr(val, 'filename'):
                submitted_file = val

        if IPlominoDocument.providedBy(self.context):
            # Easy peasy! Just store it straight away and go home.
            import pdb; pdb.set_trace()
            return "{'result':'success'}"

        file_id = uuid1().get_hex()
        self.request.SESSION[file_id] = {
            'filename': submitted_file.filename,
            'data': submitted_file.read(),
        }
        return json.dumps({'result': 'success', 'file_id': file_id})

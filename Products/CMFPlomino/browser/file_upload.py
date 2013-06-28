"""
Helper view for file upload.
"""
from Products.CMFCore.utils import getToolByName
from Products.CMFPlomino.interfaces import IPlominoDocument
from ZPublisher.HTTPRequest import FileUpload
from uuid import uuid1
from zope.browser.interfaces import IBrowserView
from zope.interface import implements
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
            if isinstance(val, FileUpload):
                submitted_file = val
                fieldname = key
                break

        if IPlominoDocument.providedBy(self.context):
            # Easy peasy! Just store it straight away and go home.
            db = self.context.aq_parent.aq_parent
            form = db[self.request.form['Form']]
            field = form[fieldname]

            adapt = field.getSettings()
            adapt.store_file(self.context, submitted_file.read(), submitted_file.filename)
            return json.dumps({'result': 'success'})

        file_id = uuid1().get_hex()
        sdm = getToolByName(self.context, 'session_data_manager')
        session = sdm.getSessionData(create=True)
        session[file_id] = {
            'filename': submitted_file.filename,
            'data': submitted_file.read(),
        }
        return json.dumps({'result': 'success', 'file_id': file_id})

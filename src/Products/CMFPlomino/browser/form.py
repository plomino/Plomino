from jsonutil import jsonutil as json
import plone.protect.interfaces
from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides

from ..config import SCRIPT_ID_DELIMITER
from ..exceptions import PlominoScriptException


class FormView(BrowserView):

    template = ViewPageTemplateFile("templates/openform.pt")
    bare_template = ViewPageTemplateFile("templates/openbareform.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.form = self.context
        self.target = self.context

    def openform(self):
        if (hasattr(self.context, 'onDisplay') and
                self.context.onDisplay):
            try:
                response = self.context.runFormulaScript(
                    SCRIPT_ID_DELIMITER.join([
                        'form', self.context.id, 'ondisplay']),
                    self.context,
                    self.context.onDisplay)
            except PlominoScriptException, e:
                response = None
                e.reportError('onDisplay formula failed')
            # If the onDisplay event returned something, return it
            # We could do extra handling of the response here if needed
            if response is not None:
                return response
        return self.template()

    def openbareform(self):
        return self.bare_template()

    def addField(self):
        # specific field settings are managed as instance behaviors (using
        # collective.instancebehavior), but it is not supported by
        # plone.restapi, so we implement our own endpoint to create fields.
        self.request.RESPONSE.setHeader(
            'content-type', 'text/plain; charset=utf-8')
        if self.request.method == "POST":
            alsoProvides(
                self.request, plone.protect.interfaces.IDisableCSRFProtection)
            data = json.loads(self.request.BODY)
            newfield = api.content.create(
                container=self.context,
                type="PlominoField",
                title=data['title'],
            )
            return json.dumps({'created': newfield.id})

from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from jsonutil import jsonutil as json
import plone.protect.interfaces
from plone import api
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides

from ..config import SCRIPT_ID_DELIMITER
from ..exceptions import PlominoScriptException
from zope.publisher.http import HTTPResponse

class FormView(BrowserView):

    template = ViewPageTemplateFile("templates/openform.pt")
    bare_template = ViewPageTemplateFile("templates/openbareform.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.form = self.context
        self.target = self.context
        if not getattr(self.request, 'SESSION', None):
            setattr(self.request, 'SESSION', self.context.session_data_manager.getSessionData())

    def _process_form(self, template):
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

        self.page_errors = []

        if self.request['REQUEST_METHOD'] == 'POST':
            # When the form is open via redirect from another foorm, ignore action is set
            if self.request.get('ignore_actions', None):
                # - Update navigation page
                # - Reset the Form ID
                # - Process the attachment in the request
                self.request.set('Form', self.form.id)
                self.request.set('plomino_current_page', 1)
                self.form.processAttachment(self.request, doc=None, creation=False)
            if 'attachment-delete' in self.request.form:
                self.form.deleteAttachment(self.request, doc=None)
            errors = self.form.validateInputs(self.request)
            # We can't continue if there are errors
            if errors:
                # save file attachment
                self.form.processAttachment(self.request, doc=None, creation=False)
                # inject these into the form
                self.page_errors = errors
            else:
                # Not create new document if we ignore the action
                # We need to check for custom SAVE actions
                actions = self.context.getActions()
                actions = [i[0].id for i in actions if
                           i[0].action_type == 'SAVE']
                # Add the default save action
                actions.append('plomino_save')
                request_actions = [i for i in actions if i in self.request.form]

                if self.request.get('ignore_actions', None) is None \
                        and len(request_actions):
                    self.form.createDocument(self.request)

        return template()

    def openform(self):
        return self._process_form(self.template)

    def openbareform(self):
        return self._process_form(self.bare_template)

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


    def getfile(self):
        temp_doc = self.form.getTemporaryDocument()
        return temp_doc.getfile(REQUEST=self.request)


@implementer(IPublishTraverse)
class PageView(BrowserView):

    template = ViewPageTemplateFile("templates/openform.pt")

    def publishTraverse(self, request, name):
        # Stop traversing. Page is far enough.
        request['TraversalRequestNameStack'] = []
        # return self so the publisher calls this view
        return self

    def __init__(self, context, request):
        super(PageView, self).__init__(context, request)

        # Set up the form
        self.context = context
        self.request = request
        self.form = self.context
        self.target = self.context
        if not getattr(self.request, 'SESSION', None):
            setattr(self.request, 'SESSION', self.context.session_data_manager.getSessionData())

        # Remove direct page access
        # Default page is page 1
        # self.page = 1
        # Ignore everything past the first page
        # if request.path:
        #    try:
        #        self.page = int(request.path[0])
        #    except ValueError:
        #        self.page = 1

    def __call__(self):
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
        return self.render()

    def render(self):
        self.page_errors = []
        # Set the current page
        #self.request['plomino_current_page'] = self.page
        form = self.context.getForm()
        # Get multi page information
        current_page = form._get_current_page()
        num_pages = form._get_num_pages()
        if self.request['REQUEST_METHOD'] == 'POST':

            # If back or previous is in the form, page backwards
            if 'plomino_previous' in self.request.form or 'back' in self.request.form or 'previous' in self.request.form:
                self.request['plomino_current_page'] = form._get_next_page(self.request, action='back')
                # return form.OpenForm(request=self.request)
                return self.openform()

            if 'attachment-delete' in self.request.form:
                self.form.deleteAttachment(self.request, doc=None)
            # Need to validate the input first before any navigation
            errors = form.validateInputs(self.request)

            # We can't continue if there are errors
            if errors:
                # save file attachment
                self.form.processAttachment(self.request, doc=None, creation=False)
                # inject these into the form
                self.page_errors = errors
                return self.openform()

            # Handle linking
            for key in self.request.form.keys():
                if key.startswith('plominolinkto-'):
                    linkto = key.replace('plominolinkto-', '')
                    self.request['plomino_current_page'] = form._get_next_page(self.request, action='linkto', target=linkto)
                    return self.openform()

            # If next or continue is the form, page forwards if the form is valid
            if 'plomino_next' in self.request.form or 'next' in self.request.form or 'continue' in self.request.form:
                if current_page < (num_pages):
                    self.request['plomino_current_page'] = form._get_next_page(self.request, action='continue')
                    return self.openform()

            # Create the document if it's not a page
            # We need to check for custom SAVE actions
            actions = self.context.getActions()
            actions = [i[0].id for i in actions if
                       i[0].action_type == 'SAVE']
            # Add the default save action
            actions.append('plomino_save')
            request_actions = [i for i in actions if i in self.request.form]

            if not form.isPage and len(request_actions):
                return form.createDocument(self.request)
            else:
                # Process the temporary attachment
                self.form.processAttachment(self.request, doc=None, creation=False)
        return self.openform()

    def openform(self):
        return self.template()


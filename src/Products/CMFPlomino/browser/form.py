from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class FormView(BrowserView):

    template = ViewPageTemplateFile("templates/openform.pt")
    bare_template = ViewPageTemplateFile("templates/openbareform.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.form = self.context
        self.target = self.context

    def openform(self):
        return self.template()

    def openbareform(self):
        return self.bare_template()


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

        # Default page is page 1
        self.page = 1
        # Ignore everything past the first page
        if request.path:
            try:
                self.page = int(request.path[0])
            except ValueError:
                self.page = 1

    def __call__(self):
        return self.render()

    def render(self):
        self.page_errors = []

        # Set the current page
        self.request['plomino_current_page'] = self.page

        form = self.context.getForm()

        # Get multi page information
        current_page = form._get_current_page()
        num_pages = form._get_num_pages()

        if self.request['REQUEST_METHOD'] == 'POST':
            # If back or previous is in the form, page backwards
            if 'back' in self.request.form or 'previous' in self.request.form:
                self.request['plomino_current_page'] = form._get_next_page(self.request, action='back')
                # return form.OpenForm(request=self.request)
                return self.openform()

            # Handle linking
            for key in self.request.form.keys():
                if key.startswith('plominolinkto-'):
                    linkto = key.replace('plominolinkto-', '')
                    self.request['plomino_current_page'] = form._get_next_page(self.request, action='linkto', target=linkto)
                    return self.openform()

            errors = form.validateInputs(self.request)

            # We can't continue if there are errors
            if errors:
                # inject these into the form
                self.page_errors = errors
                return self.openform()

            # If next or continue is the form, page forwards if the form is valid
            if 'next' in self.request.form or 'continue' in self.request.form:
                if current_page < (num_pages):
                    self.request['plomino_current_page'] = form._get_next_page(self.request, action='continue')
                    return self.openform()

            # Otherwise create the document
            return form.createDocument(self.request)

        return self.openform()

    def openform(self):
        return self.template()

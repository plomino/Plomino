from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView


class DocumentView(BrowserView):
    implements(IPublishTraverse)

    view_template = ViewPageTemplateFile('templates/opendocument.pt')
    edit_template = ViewPageTemplateFile('templates/editdocument.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.doc = None
        self.edit_mode = False

    def publishTraverse(self, request, name):
        if name == "OpenDocument" or name == "view":
            return self
        if name == "EditDocument":
            self.edit_mode = True
            return self
        if name == "saveDocument":
            return self.doc.saveDocument(self.request)
        if name == "delete":
            return self.doc.delete(self.request)

        doc = self.context.getParentDatabase().getDocument(name)
        if not doc:
            raise NotFound(self, name, request)
        self.doc = doc
        self.form = doc.getForm()
        self.target = self.doc
        return self

    def render(self):

        if self.edit_mode:
            return self.edit_template()
        else:
            return self.view_template()

    def __call__(self):
        return self.render()

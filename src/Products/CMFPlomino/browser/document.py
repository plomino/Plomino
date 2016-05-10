from AccessControl import Unauthorized
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

from ..config import DESIGN_PERMISSION


class DocumentView(BrowserView):
    implements(IPublishTraverse)

    view_template = ViewPageTemplateFile('templates/opendocument.pt')
    edit_template = ViewPageTemplateFile('templates/editdocument.pt')
    bare_view_template = ViewPageTemplateFile('templates/openbaredocument.pt')
    bare_edit_template = ViewPageTemplateFile('templates/editbaredocument.pt')
    properties_template = ViewPageTemplateFile(
        'templates/documentproperties.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.doc = None
        self.action = None
        self.form = None

    def publishTraverse(self, request, name):
        if name == "OpenDocument" or name == "view":
            self.action = "view"
            return self
        if name == "OpenBareDocument":
            self.action = "bareview"
            return self
        if name == "EditDocument":
            self.action = "edit"
            return self
        if name == "EditBareDocument":
            self.action = "bareedit"
            return self
        if name == "saveDocument":
            self.action = "save"
            return self
        if name == "delete":
            self.action = "delete"
            return self
        if name == "tojson":
            self.action = "json"
            return self
        if name == "DocumentProperties":
            self.action = "properties"
            return self
        if name == "getfile":
            self.action = "getfile"
            return self
        if name == "deleteAttachment":
            self.action = "deleteAttachment"
            return self

        doc = self.context.getParentDatabase().getDocument(name)
        if not doc:
            raise NotFound(self, name, request)
        self.doc = doc
        if getattr(self.context, 'evaluateViewForm', None):
            formname = self.context.evaluateViewForm(self.doc)
            if formname:
                self.form = self.context.getParentDatabase().getForm(formname)
        if not self.form:
            self.form = doc.getForm()
        self.target = self.doc
        return self

    def render(self):
        if self.action == "edit":
            return self.edit_template()
        if self.action == "bareedit":
            return self.bare_edit_template()
        if self.action == "bareview":
            return self.bare_view_template()
        elif self.action == "save":
            return self.doc.saveDocument(self.request)
        elif self.action == "delete":
            return self.doc.delete(self.request)
        elif self.action == "json":
            return self.doc.tojson(self.request)
        elif self.action == "getfile":
            return self.doc.getfile(REQUEST=self.request)
        elif self.action == "deleteAttachment":
            return self.doc.deleteAttachment(REQUEST=self.request)
        elif self.action == "properties":
            db = self.doc.getParentDatabase()
            if db.checkUserPermission(DESIGN_PERMISSION):
                return self.properties_template()
            else:
                raise Unauthorized("You cannot read this content")
        else:
            return self.view_template()

    def __call__(self):
        return self.render()

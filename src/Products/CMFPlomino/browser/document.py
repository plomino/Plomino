from AccessControl import Unauthorized
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.Five.browser import BrowserView

from ..config import DESIGN_PERMISSION
from ..config import SCRIPT_ID_DELIMITER
from ..exceptions import PlominoScriptException


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
        if name == "page" or name == "pageview":
            # Stop traversing
            request['TraversalRequestNameStack'] = []
            self.action = name
            # Default page is page 1
            self.page = 1
            # Ignore everything past the first page
            if request.path:
                try:
                    self.page = int(request.path[0])
                except ValueError:
                    pass
            self.request['plomino_current_page'] = self.page
            return self
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
        if self.action == "page":
            return self._page_edit()
        if self.action == "pageview":
            return self._page_view()
        if self.action == "edit":
            # If a user tries to edit a multipage form
            if self.target.getIsMulti():
                return self.redirect('page', '1')
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
            # If a user tries to view a multipage form
            if self.target.getIsMulti():
                return self.redirect('pageview', '1')
            return self.view_template()

    def __call__(self):
        return self.render()

    def _page_edit(self):
        # Multipage edit mode
        form = self.target.getForm()

        # Get multi page information
        current_page = form._get_current_page()
        num_pages = form._get_num_pages()

        # If they have gone past the end of the form, send them back
        if current_page > num_pages:
            return self.redirect('page', num_pages)

        # Handle POST requests differently.
        if self.request['REQUEST_METHOD'] == 'POST':
            # Look up the form. This might be the context, or the parent form
            # or a value from the request

            if 'plomino_previous' in self.request.form or 'back' in self.request.form or 'previous' in self.request.form:
                next_page = form._get_next_page(self.request, doc=self.target, action='back')
                return self.redirect('page', next_page)

            # Handle linking
            linkto = False
            for key in self.request.form.keys():
                if key.startswith('plominolinkto-'):
                    linkto = key.replace('plominolinkto-', '')
                    next_page = form._get_next_page(self.request, doc=self.target, action='linkto', target=linkto)
                    return self.redirect('page', next_page)

            # Pass in the current doc as well. This ensures that fields on other
            # pages are included (possibly needed for calculations)
            errors = form.validateInputs(self.request, doc=self.target)

            if errors:
                self.page_errors = errors
                return self.edit_template()

            # Any buttons progress the user through the form
            # XXX: We need to handle other types of buttons here
            if current_page < (num_pages):
                next_page = form._get_next_page(self.request, doc=self.target, action='continue')
            else:
                # Don't go past the end of the form
                next_page = num_pages

            # execute the beforeSave code of the form
            error = None
            try:
                error = self.target.runFormulaScript(
                        SCRIPT_ID_DELIMITER.join(['form', form.id, 'beforesave']),
                        self.target,
                        form.beforeSaveDocument)
            except PlominoScriptException, e:
                e.reportError('Form submitted, but beforeSave formula failed')

            if error:
                errors.append({'field': 'beforeSave', 'error': error})
                self.page_errors = errors
                # Stay on this page
                return self.edit_template()

            # Now save and move forwards
            self.target.setItem('Form', form.id)

            # process editable fields (we read the submitted value in the request)
            form.readInputs(self.target, self.request, process_attachments=True)

            # refresh computed values, run onSave, reindex. Should never be creation.
            self.target.save(form, False)

            # If there is a redirect, redirect to it:
            redirect = self.request.get('plominoredirecturl')
            if not redirect:
                redirect = self.target.getItem("plominoredirecturl")

            if redirect:
                return self.request.RESPONSE.redirect(redirect)

            # Otherwise continue to the next page of the document
            return self.redirect('page', next_page)

        return self.edit_template()

    def _page_view(self):
        # Multipage view mode. No need to check validation in this mode.
        form = self.target.getForm()

        # Get multi page information
        current_page = form._get_current_page()
        num_pages = form._get_num_pages()

        # If there is something in the form (i.e. a paging request)
        if self.request.form:
            # If they have gone past the end of the form, send them back
            if current_page > num_pages:
                return self.redirect('pageview', num_pages)

            if 'plomino_previous' in self.request.form or 'back' in self.request.form or 'previous' in self.request.form:
                next_page = form._get_next_page(
                    self.request,
                    doc=self.target,
                    action='back'
                )
                return self.redirect('pageview', next_page)

            # Handle linking
            linkto = False
            for key in self.request.form.keys():
                if key.startswith('plominolinkto-'):
                    linkto = key.replace('plominolinkto-', '')
                    next_page = form._get_next_page(self.request, doc=self.target, action='linkto', target=linkto)
                    return self.redirect('pageview', next_page)

            # Any buttons progress the user through the form
            # XXX: We need to handle other types of buttons here
            if current_page < (num_pages):
                next_page = form._get_next_page(
                    self.request,
                    doc=self.target,
                    action='continue'
                )
            else:
                # Don't go past the end of the form
                next_page = num_pages

            return self.redirect('pageview', next_page)

        return self.view_template()

    def redirect(self, view, page):
        url = '%s/%s/%s' % (self.target.absolute_url(), view, page)
        return self.request.RESPONSE.redirect(url)

from AccessControl import Unauthorized
from jsonutil import jsonutil as json
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ..config import READ_PERMISSION


class DatabaseView(BrowserView):

    acl_template = ViewPageTemplateFile("templates/acl.pt")
    design_template = ViewPageTemplateFile("templates/design.pt")
    view_template = ViewPageTemplateFile("templates/opendatabase.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.form = self.context
        self.target = self.context

    def view(self):
        if self.context.checkUserPermission(READ_PERMISSION):
            if self.context.start_page:
                target = getattr(self.context, self.context.start_page, None)
                if target:
                    self.request.response.redirect(target.absolute_url())
            else:
                return self.view_template()
        else:
            raise Unauthorized("You cannot read this content")

    def design(self):
        return self.design_template()

    def tree(self):
        forms = []
        for form in self.context.getForms():
            fields = []
            for field in form.getFormFields():
                fields.append({"label": field.id, "url": field.absolute_url()})
            actions = []
            for action in form.getFormActions():
                actions.append({"label": action.id, })
            fields.append({
                "label": "Actions",
                "folder": True,
                "children": actions,
            })
            forms.append({
                "label": form.id,
                "folder": True,
                "children": fields,
            })
        elements = [{
            "label": "forms",
            "folder": True,
            "children": forms,
        }, ]
        self.request.RESPONSE.setHeader(
            'content-type', 'application/json; charset=utf-8')
        return json.dumps(elements)

    def acl(self):
        return self.acl_template()

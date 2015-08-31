from jsonutil import jsonutil as json
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class DatabaseView(BrowserView):

    design_template = ViewPageTemplateFile("templates/design.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.form = self.context
        self.target = self.context

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

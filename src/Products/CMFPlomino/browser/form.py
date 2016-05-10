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

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class FormView(BrowserView):

    template = ViewPageTemplateFile("templates/openform.pt")

    def openform(self):
        return self.template()

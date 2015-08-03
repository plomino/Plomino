from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class Actions(BrowserView):

    template = ViewPageTemplateFile("templates/actions.pt")

    def __call__(self):
        return self.template()

    @property
    def macros(self):
        return self.template.macros

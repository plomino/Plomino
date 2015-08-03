from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ErrorMessages(BrowserView):

    template = ViewPageTemplateFile("templates/errors.pt")

    def __call__(self, errors=None):
        self.errors = errors
        return self.template()

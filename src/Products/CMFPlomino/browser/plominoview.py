from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class ViewView(BrowserView):

    template = ViewPageTemplateFile("templates/openview.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.target = self.context

    def openview(self):
        return self.template()

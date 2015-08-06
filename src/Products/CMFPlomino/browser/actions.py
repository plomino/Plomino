from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class Actions(BrowserView):

    action_bar = ViewPageTemplateFile("templates/actions.pt")
    embedded_action = ViewPageTemplateFile("templates/action.pt")

    @property
    def macros(self):
        return self.action_bar.macros

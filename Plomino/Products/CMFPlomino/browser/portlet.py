from zope.interface import Interface, implements
from zope.formlib import form
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class IPortlet(Interface):
    pass

class Assignment(base.Assignment):
    implements(IPortlet)

    title = u'Plomino design portlet'

class Renderer(base.Renderer):
    render = ViewPageTemplateFile('design_portlet.pt')
    
    def parentdatabase(self):
        """
        """
        parentdb = self.context.unrestrictedTraverse(self.context.getPhysicalPath())
        while len(parentdb.getPhysicalPath())>0 and parentdb.__class__.__name__!="PlominoDatabase":
            parentdb = parentdb.getParentNode()
        return parentdb

    def currenttype(self):
        """
        """
        return self.context.__class__.__name__
    
    def hasDesignPermission(self):
        """
        """
        return self.parentdatabase().hasDesignPermission()
    
    @property
    def available(self):
        return self.hasDesignPermission()
    
class AddForm(base.AddForm):
    form_fields = form.Fields(IPortlet)

    def create(self, data):
        return Assignment()

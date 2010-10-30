from zope.interface import Interface, implements
from zope.formlib import form
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from Products.CMFPlomino.browser import PloneMessageFactory as _

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


class IElementPortlet(Interface):
    """Contains the template used to fill a template form
    """
    header = schema.TextLine(title=_(u"Portlet header"),
                             description=_(u"Title of the rendered portlet"),
                             required=True)
    db_path = schema.TextLine(title=_(u"Database path"),
                             description=_(u"Path of the database where the element is stored"),
                             required=True)
    element_id = schema.TextLine(title=_(u"Element ID"),
                             description=_(u"ID of the form to be displayed"),
                             required=True)
    

class ElementPortletAssignment(base.Assignment):
    """Initialises a Plomino Element portlet
    """
    implements(IElementPortlet)
    
    title = u'Plomino Element Display'
    header = u""
    db_path = ""
    element_id = ""
    
    def __init__(self, header=u"", db_path="", element_id=""):
        self.header = header
        self.db_path = db_path
        self.element_id = element_id

    
class ElementPortletRenderer(base.Renderer):
    """Displays the Plomino Element portlet
    """
    render = ViewPageTemplateFile('element_portlet.pt')
    
    def getElement(self):
        """Get the element to be displayed by the portlet
        """
        db = self.context.restrictedTraverse(self.data.db_path.encode(), None)
        if db:
            element = getattr(db, self.data.element_id.encode(), None)
            if hasattr(element, 'formLayout'):
                return element
        return None
        
    @property
    def available(self):
        return True
    
    @property
    def hasGoogleVisualizationField(self):
        element = self.getElement() 
        if element is not None:
            return element.hasGoogleVisualizationField()
        else:
            return False
        
    @property
    def action_url(self):
        element = self.getElement()
        base_url = element.absolute_url()
        if element.isSearchForm:
            return base_url+"/searchDocuments"
        if element.isPage:
            return "."
        return base_url+"/createDocument"
    
    def elementLayout(self):
        """Get the element layout to be displayed by the portlet
        """
        #import pdb; pdb.set_trace()
        element = self.getElement()
        if element:
            return element.formLayout(self.request)
        else:
            return """<p>The database cannot be found or the element cannot be displayed.</p>"""
    
class ElementPortletAddForm(base.AddForm):
    """Creates a portlet used to display a Plomino element everywhere in a Plone site
    """
    label = _(u"Add a Plomino Element Portlet")
    description = _(u"This portlet displays an element of a Plomino database.")
    form_fields = form.Fields(IElementPortlet)

    def create(self, data):
        return ElementPortletAssignment(**data)
    
class ElementPortletEditForm(base.EditForm):
    """Edit a portlet used to display a Plomino element everywhere in a Plone site
    """
    label = _(u"Edit a Plomino Element Portlet")
    description = _(u"This portlet displays an element of a Plomino database.")
    form_fields = form.Fields(IElementPortlet)

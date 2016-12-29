from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import provider, Interface
from zope import schema
from plone.autoform import directives
from .. import _

@provider(IFormFieldProvider)
class IShortName(model.Schema):
    """ Marker interface for our behaviour
    """
    id = schema.ASCIILine(
        title=_(u'Id'),
#        description=_(u'The id used to store and retried this data in the document'),
        required=False,
    )
    directives.write_permission(id='cmf.AddPortalContent')
    directives.order_before(id = 'IBasic.title')

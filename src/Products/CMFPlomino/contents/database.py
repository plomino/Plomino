from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implements

from .. import _


class IPlominoDatabase(model.Schema):
    """ Plomino database schema
    """

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
    )


class PlominoDatabase(Container):
    implements(IPlominoDatabase)

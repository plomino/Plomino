from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implements

from .. import _


class IPlominoField(model.Schema):
    """ Plomino field schema
    """

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
    )


class PlominoField(Item):
    implements(IPlominoField)

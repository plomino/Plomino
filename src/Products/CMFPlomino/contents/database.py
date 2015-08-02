from AccessControl import ClassSecurityInfo
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implements

from .. import _, config
from ..design import DesignManager

security = ClassSecurityInfo()


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

    debugMode = schema.Bool(
        title=_('CMFPlomino_label_debugMode', default="Debug mode"),
        description=_('CMFPlomino_help_debugMode', default="If enabled, script"
        " and formula errors are logged."),
        default=False,
    )


class PlominoDatabase(Container, DesignManager):
    implements(IPlominoDatabase)

    security.declareProtected(config.READ_PERMISSION, 'getParentDatabase')

    def getParentDatabase(self):
        """ Normally used via acquisition by Plomino formulas operating on
        documents, forms, etc.
        """
        obj = self
        while getattr(obj, 'portal_type', '') != 'PlominoDatabase':
            obj = obj.aq_parent
        return obj

from AccessControl import ClassSecurityInfo
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implements

from .. import _, config
from ..accesscontrol import AccessControl
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

    datetime_format = schema.TextLine(
        title=_('CMFPlomino_label_DateTimeFormat', default="Date/time format"),
        description=_(
            "CMFPlomino_help_DateTimeFormat",
            default='Format example: %Y-%m-%d'),
        default=u"%Y-%m-%d",
        required=False,
    )

    debugMode = schema.Bool(
        title=_('CMFPlomino_label_debugMode', default="Debug mode"),
        description=_('CMFPlomino_help_debugMode', default="If enabled, script"
        " and formula errors are logged."),
        default=False,
    )

    do_not_list_users = schema.Bool(
        title=_("CMFPlomino_label_DoNotListUsers",
            default="Do not list portal users"),
        description=_("CMFPlomino_help_DoNotListUsers",
            default='If True, in ACL screen, users are entered using a free '
            'text field, if False, using a selection list. Use True when the '
            'amount of users is large.'),
        default=False,
    )


class PlominoDatabase(Container, AccessControl, DesignManager):
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

    def getViews(self, sortbyid=True):
        """ Return the list of PlominoView instances in the database.
        """
        view_list = [obj for obj in self.objectValues()
            if obj.__class__.__name__ == 'PlominoView']
        view_obj_list = [a for a in view_list]
        if sortbyid:
            view_obj_list.sort(key=lambda elt: elt.id.lower())
        else:
            view_obj_list.sort(key=lambda elt: elt.getPosition())
        return view_obj_list

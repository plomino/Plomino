from plone.autoform import directives
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from .. import _
from ..config import ACTION_TYPES, ACTION_DISPLAY

action_types = SimpleVocabulary([
    SimpleTerm(value=mode[0], title=_(mode[1])) for mode in ACTION_TYPES
])
action_displays = SimpleVocabulary([
    SimpleTerm(value=mode[0], title=_(mode[1])) for mode in ACTION_DISPLAY
])


class IPlominoAction(model.Schema):
    """ Plomino action schema
    """

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
    )

    action_type = schema.Choice(
        title=_('CMFPlomino_label_ActionType',
            default="Select the type for this action"),
        description=_('CMFPlomino_help_ActionType',
            default='Select the type for this action'),
        required=True,
        vocabulary=action_types,
    )

    action_display = schema.Choice(
        title=_('CMFPlomino_label_ActionDisplay', default="Action display"),
        description=_('CMFPlomino_help_ActionDisplay',
            default="How the action is shown"),
        required=True,
        default='BUTTON',
        vocabulary=action_displays,
    )

    directives.widget('content', klass='plomino-formula')
    content = schema.Text(
        title=_('CMFPlomino_label_ActionContent', default='Parameter or code'),
        description=_('CMFPlomino_help_ActionContent',
            default='Code or parameter depending on the action type'),
        required=False,
    )

    hidewhen = schema.Text(
        title=_('CMFPlomino_label_ActionHidewhen',
            default="Action is hidden if formula returns True"),
        description=_('CMFPlomino_help_ActionHidewhen',
            default='Action is hidden if formula returns True'),
        required=False,
    )

    in_action_bar = schema.Bool(
        title=_('CMFPlomino_label_ActionInActionBar',
            default='Display action in action bar (yes/no)'),
        description=_('CMFPlomino_help_ActionInActionBar',
            default='Display action in action bar (yes/no)'),
        default=True,
        required=True,
    )


class PlominoAction(Item):
    implements(IPlominoAction)

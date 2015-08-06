from AccessControl import ClassSecurityInfo
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implements

from .. import _


class IPlominoView(model.Schema):
    """ Plomino view schema
    """

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
    )

    directives.widget('selection_formula', klass='plomino-formula')
    selection_formula = schema.Text(
        title=_('CMFPlomino_label_SelectionFormula',
            default="Selection formula"),
        description=_('CMFPlomino_help_SelectionFormula',
            default="""The view selection formula is a line of Python code """
            """which should return True or False. The formula will be """
            """evaluated for each document in the database to decide if the """
            """document must be displayed in the view or not. """
            """'plominoDocument' is a reserved name in formulae: it returns """
            """the current Plomino document."""),
        default=u"True",
        required=True,
    )

    directives.widget('form_formula', klass='plomino-formula')
    form_formula = schema.Text(
        title=_('CMFPlomino_label_FormFormula', default="Form formula"),
        description=_('CMFPlomino_help_FormFormula',
            default='Documents open from the view will use the form defined '
            'by the following formula(they use their own form if empty)'),
        required=False
    )

    hide_default_actions = schema.Bool(
        title=_('CMFPlomino_label_HideViewDefaultActions',
            default="Hide default actions"),
        description=_('CMFPlomino_help_HideViewDefaultActions',
            default='Delete, Close actions will not be displayed in the '
            'action bar'),
        default=False,
    )

    directives.widget('onOpenView', klass='plomino-formula')
    onOpenView = schema.Text(
        title=_('CMFPlomino_label_onOpenView', default="On open view"),
        description=_('CMFPlomino_help_onOpenView',
            default="Action to take when the view is opened. If a string is "
            "returned, it is considered an error message, and the opening is "
            "not allowed."),
        required=False
    )

    sort_column = schema.TextLine(
        title=_('CMFPlomino_label_SortColumn', default="Sort column"),
        description=_('CMFPlomino_help_SortColumn',
            default="Column used to sort the view, and by default for key "
            "lookup"),
    )

    categorized = schema.Bool(
        title=_('CMFPlomino_label_Categorized', default="Categorized"),
        description=_('CMFPlomino_help_Categorized',
            default='Categorised on first column'),
        default=False,
    )

    reverse_sorting = schema.Bool(
        title=_('CMFPlomino_label_ReverseSorting', default="Reverse sorting"),
        description=_('CMFPlomino_help_ReverseSorting',
            default="Reverse the sort ordering"),
        default=False,
    )


class PlominoView(Container):
    implements(IPlominoView)

    security = ClassSecurityInfo()

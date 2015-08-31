from AccessControl import ClassSecurityInfo
import Missing
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implements, invariant, Invalid

from .. import _
from ..utils import translate


class IPlominoColumn(model.Schema):
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

    displayed_field = schema.Choice(
        vocabulary='Products.CMFPlomino.columns.vocabularies.get_fields',
        title=_('CMFPlomino_label_DisplayedField', default="Displayed field"),
        description=_('CMFPlomino_help_DisplayedField', default="Field value "
            "to display in the column. It does not apply if Formula is "
            "provided."),
        required=False,
    )

    directives.widget('formula', klass='plomino-formula')
    formula = schema.Text(
        title=_('CMFPlomino_label_ColumnFormula', default="Formula"),
        description=_('CMFPlomino_help_ColumnFormula', default='Python code '
            'returning the column value.'),
        required=False,
    )

    hidden_column = schema.Bool(
        title=_('CMFPlomino_label_HiddenColumn', default="Hidden column"),
        default=False,
    )

    @invariant
    def formulaInvariant(data):
        if not(data.displayed_field or data.formula):
            raise Invalid(_("CMFPlomino_validation_column",
                default=u"If you don't specify a column "
                "formula, you need to select a field."))


class PlominoColumn(Item):
    implements(IPlominoColumn)

    security = ClassSecurityInfo()

    security.declarePublic('getColumnRender')

    def getColumnRender(self, fieldvalue):
        """ If associated with a field, let the field do the rendering.
        Do translation of the rendered field.
        """
        if fieldvalue is Missing.Value:
            return ''

        if self.formula:
            return translate(self, fieldvalue)

        # If there is no formula, there has to be a field
        form_id, fieldname = self.displayed_field.split('/')
        db = self.getParentDatabase()
        form = db.getForm(form_id)
        field = form.getFormField(fieldname)

        try:
            return field.getRenderedValue(fieldvalue, False, form)
        except Exception, e:
            self.traceRenderingErr(e, self)
            return ""

    security.declarePublic('getParentView')

    def getParentView(self):
        """ Get parent view
        """
        return self.getParentNode()

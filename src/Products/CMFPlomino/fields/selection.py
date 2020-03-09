# -*- coding: utf-8 -*-
import copy
from Products.CMFPlomino import _
from jsonutil import jsonutil as json
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider, ORDER_KEY
from plone.supermodel import model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from ..utils import PlominoTranslate
from ..config import SCRIPT_ID_DELIMITER
from ..exceptions import PlominoScriptException
from ..utils import asUnicode
from base import BaseField
from z3c.form.interfaces import NOT_CHANGED

@provider(IFormFieldProvider)
class ISelectionField(model.Schema):
    """ Selection field schema
    """

    # directives.fieldset(
    #     'settings',
    #     label=_(u'Settings'),
    #     fields=(
    #         'widget',
    #         'selectionlist',
    #         'selectionlistformula',
    #         'separator',
    #     ),
    # )

    widget = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Selection list", "SELECT"),
            ("Multi-selection list", "MULTISELECT"),
            ("Checkboxes", "CHECKBOX"),
            ("Radio buttons", "RADIO"),
        ]),
        title=u'Widget',
        description=u'Field rendering',
        default="SELECT",
        required=True)

    selectionlist = schema.List(
        title=u'Selection list',
        description=u"List of values to select, one per line, "
        "formatted as 'label|value'",
        required=False,
        default=[],
        value_type=schema.TextLine(title=u'Entry'))

    form.widget('selectionlistformula', klass='plomino-formula')
    selectionlistformula = schema.Text(
        title=u'Selection list formula',
        description=u'Formula to compute the selection list elements',
        missing_value=NOT_CHANGED,
        default=u'',
        required=False)

    allow_other_value = schema.Bool(
        title=u'Allow other value',
        description=u'Allow users to enter a value other than in your list.'
                    u' Your multi-selection list should not include labels in '
                    u'this case',
        default=False,
        required=False)

    separator = schema.TextLine(
        title=u'Separator',
        description=u'Only apply if multiple values will be displayed',
        required=False)


# bug in plone.autoform means order_after doesn't moves correctly
ISelectionField.setTaggedValue(ORDER_KEY, [
    ('widget', 'after', 'field_type'),
    ('selectionlist', 'after', ".widget"),
    ('selectionlistformula', 'after', ".selectionlist"),
    ('separator', 'after', ".selectionlistformula")]
)


@implementer(ISelectionField)
class SelectionField(BaseField):
    """
    """

    read_template = PageTemplateFile('selection_read.pt')
    edit_template = PageTemplateFile('selection_edit.pt')

    def getSelectionList(self, doc):
        """ Return the values list.
        Format: label|value, use label as value if no label.
        """
        # If not dynamic rendering, then enable caching
        db = self.context.getParentDatabase()
        cache_key = "getSelectionList_%s" % (
            hash(self.context)
        )
        if not self.context.isDynamicField:
            cache = db.getRequestCache(cache_key)
            if cache:
                return cache

        # if formula available, use formula, else use manual entries
        f = getattr(self.context, 'selectionlistformula', None)
        if f:
            # if no doc provided (if OpenForm action), we use the PlominoForm
            if doc:
                obj = doc
            else:
                obj = self.context

            try:
                s = self.context.runFormulaScript(
                    SCRIPT_ID_DELIMITER.join(['field',
                                              self.context.getParentNode().id,
                                              self.context.id,
                                             'SelectionListFormula']),
                    obj,
                    f)

            except PlominoScriptException, e:
                p = self.context.absolute_url_path()
                e.reportError(
                    '%s field selection list formula failed' %
                    self.context.id,
                    path=p + '/getSettings?key=selectionlistformula')
                s = []
        else:
            s = getattr(self.context, 'selectionlist', None)

        if not s:
            s = []

        # if values not specified, use label as value
        label_value = []
        for v in s:
            v = asUnicode(v)
            if len(v.split('|')) == 2:
                label_value.append(v)
            else:
                label_value.append(v + '|' + v)


        allow_other = getattr(self.context, 'allow_other_value', False)
        widget =  getattr(self.context, 'widget', None)
        if allow_other and ( widget =='CHECKBOX' or widget == 'RADIO'):
            label_value.append(PlominoTranslate('Other', self.context) + '|' + '@@OTHER_VALUE')
        # Save to cache if not dynamic rendering
        if not self.context.isDynamicField:
            db.setRequestCache(cache_key, label_value)

        return label_value

    def processInput(self, values):
        """
        """
        widget = getattr(self.context, 'widget', None)
        allow_other = getattr(self.context, 'allow_other_value', False)
        values = BaseField.processInput(self, values)
        if isinstance(values, basestring):
            if widget == 'MULTISELECT' and allow_other:
                values = values.split(',') if values else []
        if type(values) == list:
            values = [asUnicode(v) for v in values]
        return values

    @staticmethod
    def tojson(selection):
        """ Return a JSON table storing documents to be displayed
        """
        return json.dumps([v.split('|')[::-1] for v in selection])

    def validate(self, submitted_value):
        errors = []

        # Macros are problematic as the selection list is not derived from
        # the context of the selection formula. It seems that on submission
        # of a macro form the correct context is not set, preventing us from
        # knowing what the list presented in the macro was.
        # See https://github.com/pretagov/PlominoWorkflow/issues/176
        # For now we skip validation of macros...
        if self.context.REQUEST.get('Plomino_Macro_Context', None):
            return errors

        allow_other = getattr(self.context, 'allow_other_value', False)
        if submitted_value is not None:
            plural = False
            select_opts = \
                [i.split('|')[-1] for i in self.getSelectionList(None)]
            if type(submitted_value) in (str, unicode):
                values_match = submitted_value in select_opts
                pretty_value = submitted_value
            else:
                values_match = all(i in select_opts for i in submitted_value)
                pretty_value = ', '.join(submitted_value)
                if len(submitted_value) > 1:
                    plural = True
            if values_match is False and allow_other is False:
                errors.append(_(u'Submitted value%s (%s) do%s not match '
                                u'available selection options' %
                                (plural is True and 's' or '', 
                                 pretty_value,
                                 plural is False and 'es' or '')))
        return errors

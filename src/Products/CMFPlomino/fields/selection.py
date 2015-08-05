# -*- coding: utf-8 -*-

from jsonutil import jsonutil as json
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import directives, model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from .. import _
from ..config import SCRIPT_ID_DELIMITER
from ..exceptions import PlominoScriptException
from ..utils import asUnicode
from base import BaseField


@provider(IFormFieldProvider)
class ISelectionField(model.Schema):
    """ Selection field schema
    """

    directives.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=(
            'widget',
            'selectionlist',
            'selectionlistformula',
            'separator',
        ),
    )

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
        required=False)

    separator = schema.TextLine(
        title=u'Separator',
        description=u'Only apply if multiple values will be displayed',
        required=False)


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
        # if formula available, use formula, else use manual entries
        f = self.context.selectionlistformula
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
                        self.context.id, 'SelectionListFormula']),
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
            s = self.context.selectionlist
            if not s:
                return []

        # if values not specified, use label as value
        label_value = []
        for v in s:
            v = asUnicode(v)
            l = v.split('|')
            if len(l) == 2:
                label_value.append(v)
            else:
                label_value.append(v + '|' + v)

        return label_value

    def processInput(self, values):
        """
        """
        values = BaseField.processInput(self, values)
        if type(values) == list:
            values = [asUnicode(v) for v in values]
        return values

    def tojson(self, selection):
        """ Return a JSON table storing documents to be displayed
        """
        return json.dumps([v.split('|')[::-1] for v in selection])

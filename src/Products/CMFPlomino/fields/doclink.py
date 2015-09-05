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
class IDoclinkField(model.Schema):
    """ Selection field schema
    """

    directives.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=(
            'widget',
            'sourceview',
            'labelcolumn',
            'documentslistformula',
            'separator',
        ),
    )

    widget = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Selection list", "SELECT"),
            ("Multi-selection list", "MULTISELECT"),
            ("Embedded view", "VIEW"),
        ]),
        title=u'Widget',
        description=u'Field rendering',
        default="SELECT",
        required=True)

    sourceview = schema.Choice(
        vocabulary='Products.CMFPlomino.fields.vocabularies.get_views',
        title=u'Source view',
        description=u'View containing the linkable documents',
        required=False)

    labelcolumn = schema.TextLine(
        title=u'Label column',
        description=u'View column used as label',
        required=False)

    form.widget('documentslistformula', klass='plomino-formula')
    documentslistformula = schema.Text(
        title=u'Documents list formula',
        description=u"Formula to compute the linkable documents list "
        "(must return a list of 'label|docid_or_path')",
        required=False)

    separator = schema.TextLine(
        title=u'Separator',
        description=u'Only apply if multiple values will be displayed',
        required=False)


@implementer(IDoclinkField)
class DoclinkField(BaseField):
    """
    """

    read_template = PageTemplateFile('doclink_read.pt')
    edit_template = PageTemplateFile('doclink_edit.pt')

    def getSelectionList(self, doc):
        """ Return the documents list, format: label|docid_or_path, use
        value is used as label if no label.
        """

        # if formula available, use formula, else use view entries
        f = self.context.documentslistformula
        if not f:
            if not(self.context.sourceview and self.context.labelcolumn):
                return []
            v = self.context.getParentDatabase().getView(self.context.sourceview)
            if not v:
                return []
            label_key = v.getIndexKey(self.context.labelcolumn)
            if not label_key:
                return []
            result = []
            for b in v.getAllDocuments(getObject=False):
                val = getattr(b, label_key, '')
                if not val:
                    val = ''
                result.append(asUnicode(val) + "|" + b.id)
            return result
        else:
            # if no doc provided (if OpenForm action), we use the PlominoForm
            if doc is None:
                obj = self.context.getParentNode()
            else:
                obj = doc
            try:
                s = self.context.runFormulaScript(
                    SCRIPT_ID_DELIMITER.join(['field',
                        self.context.getParentNode().id,
                        self.context.id,
                        'documentslistformula']),
                    obj,
                    f)
            except PlominoScriptException, e:
                p = self.context.absolute_url_path()
                e.reportError(
                    '%s doclink field selection list formula failed' %
                    self.context.id,
                    path=p + '/getSettings?key=documentslistformula')
                s = None
            if s is None:
                s = []

        # if values not specified, use label as value
        proper = []
        for v in s:
            l = v.split('|')
            if len(l) == 2:
                proper.append(v)
            else:
                proper.append(v + '|' + v)
        return proper

    def processInput(self, submittedValue):
        """
        """
        if "|" in submittedValue:
            return submittedValue.split("|")
        else:
            return submittedValue

    def tojson(self, selectionlist):
        """Return a JSON table storing documents to be displayed
        """
        if self.context.sourceview:
            sourceview = self.context.getParentDatabase().getView(
                self.sourceview)
            brains = sourceview.getAllDocuments(getObject=False)
            columns = [col for col in sourceview.getColumns()
                    if not(col.getHiddenColumn())]
            column_ids = [col.id for col in columns]

            datatable = []
            for b in brains:
                row = [b.id]
                for col in column_ids:
                    v = getattr(b, sourceview.getIndexKey(col))
                    if not isinstance(v, str):
                        v = unicode(v).encode('utf-8').replace('\r', '')
                    row.append(v or '&nbsp;')
                datatable.append(row)
        else:
            datatable = [v.split('|')[::-1] for v in selectionlist]

        return json.dumps(datatable)

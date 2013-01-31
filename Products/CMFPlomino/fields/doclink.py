# -*- coding: utf-8 -*-
#
# File: doclink.py
#
# Copyright (c) 2009 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

# Third party
from jsonutil import jsonutil as json

# Zope
from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields
from zope.schema import TextLine, Text, Choice
from zope.schema.vocabulary import SimpleVocabulary

# Plomino
from base import IBaseField, BaseField, BaseForm
from dictionaryproperty import DictionaryProperty
from Products.CMFPlomino.exceptions import PlominoScriptException

class IDoclinkField(IBaseField):
    """ Selection field schema
    """
    widget = Choice(
            vocabulary=SimpleVocabulary.fromItems(
                [("Selection list", "SELECT"),
                    ("Multi-selection list", "MULTISELECT"),
                    ("Embedded view", "VIEW"),
                    ("Dynamic table", "DYNAMICTABLE"),
                    ("Dynamic picklist", "PICKLIST")
                    ]),
                title=u'Widget',
                description=u'Field rendering',
                default="SELECT",
                required=True)

    sourceview = Choice(
            vocabulary='Products.CMFPlomino.fields.vocabularies.get_views',
            title=u'Source view',
            description=u'View containing the linkable documents',
            required=False)

    labelcolumn = TextLine(
            title=u'Label column',
            description=u'View column used as label',
            required=False)

    documentslistformula = Text(
            title=u'Documents list formula',
            description=u"Formula to compute the linkable documents list "
                    "(must return a list of 'label|docid_or_path')",
            required=False)
    separator = TextLine(
            title=u'Separator',
            description=u'Only apply if multiple values will be displayed',
            required=False)
    dynamictableparam = Text(
            title=u"Dynamic Table Parameters",
            description=u"Change these options to customize the dynamic table",
            default=u"""
'bPaginate': true,
'bLengthChange': true,
'bFilter': true,
'bSort': true,
'bInfo': true,
'bAutoWidth': false"""
    )

class DoclinkField(BaseField):
    """
    """
    implements(IDoclinkField)

    def getSelectionList(self, doc):
        """ Return the documents list, format: label|docid_or_path, use
        value is used as label if no label.
        """

        #if formula available, use formula, else use view entries
        f = self.documentslistformula
        if not f:
            if self.sourceview:
                v = self.context.getParentDatabase().getView(self.sourceview)
            else:
                v = None
            if v is None:
                return []
            else:
                result = []
                for b in v.getAllDocuments(getObject=False):
                    val = getattr(b, v.getIndexKey(self.labelcolumn), '')
                    if not val:
                        val = ''
                    result.append(val + "|" + b.id)
                return result
        else:
            #if no doc provided (if OpenForm action), we use the PlominoForm
            if doc is None:
                obj = self.context.getParentNode()
            else:
                obj = doc
            try:
                s = self.context.runFormulaScript(
                        'field_%s_%s_DocumentListFormula' % (
                            self.context.getParentNode().id,
                            self.context.id),
                        obj,
                        lambda: f)
            except PlominoScriptException, e:
                p = self.context.absolute_url_path()
                e.reportError(
                        '%s doclink field selection list formula failed' %
                        self.context.id,
                        path=p+'/getSettings?key=documentslistformula')
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
                proper.append(v+'|'+v)
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
        if self.sourceview:
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

    def getJQueryColumns(self):
        """ Returns a JSON representation of columns headers.
        
        Designed for JQuery DataTables.
        """
        if self.sourceview is not None:
            sourceview = self.context.getParentDatabase().getView(
                    self.sourceview)
            columns = [col for col in sourceview.getColumns() 
                    if not(col.getHiddenColumn())]
            column_labels = [col.Title() for col in columns]
        else:
            column_labels = [""]

        column_dicts = [{"sTitle": col} for col in column_labels]
        column_dicts.insert(
                0,
                {"bVisible": False, "bSearchable": False})

        return json.dumps(column_dicts)

    def getColumnLabelIndex(self):
        """ Return the column index used to display the document label
        """
        if self.sourceview:
            return [col.id for col in
                    self.context.getParentDatabase().getView(
                        self.sourceview).getColumns()].index(
                                self.labelcolumn);
        else:
            return 0

for f in getFields(IDoclinkField).values():
    setattr(DoclinkField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IDoclinkField)


# -*- coding: utf-8 -*-
#
# File: selection.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields
from zope.schema import TextLine, Text, List, Choice
from zope.schema.vocabulary import SimpleVocabulary
from dictionaryproperty import DictionaryProperty

from base import IBaseField, BaseField, BaseForm
from Products.CMFPlomino.exceptions import PlominoScriptException
from Products.CMFPlomino.PlominoUtils import asUnicode

from jsonutil import jsonutil as json


class ISelectionField(IBaseField):
    """ Selection field schema
    """
    widget = Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Selection list", "SELECT"),
            ("Multi-selection list", "MULTISELECT"),
            ("Checkboxes", "CHECKBOX"),
            ("Radio buttons", "RADIO"),
            ("Dynamic picklist", "PICKLIST")
        ]),
        title=u'Widget',
        description=u'Field rendering',
        default="SELECT",
        required=True)
    selectionlist = List(
        title=u'Selection list',
        description=u"List of values to select, one per line, "
                "formatted as 'label|value'",
        required=False,
        default=[],
        value_type=TextLine(title=u'Entry'))
    selectionlistformula = Text(
        title=u'Selection list formula',
        description=u'Formula to compute the selection list elements',
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


class SelectionField(BaseField):
    """
    """
    implements(ISelectionField)

    def getSelectionList(self, doc):
        """ Return the values list.
        Format: label|value, use label as value if no label.
        """
        #if formula available, use formula, else use manual entries
        f = self.selectionlistformula
        if f:
            #if no doc provided (if OpenForm action), we use the PlominoForm
            if doc:
                obj = doc
            else:
                obj = self.context
            try:
                s = self.context.runFormulaScript(
                        'field_%s_%s_SelectionListFormula' % (
                            self.context.getParentNode().id,
                            self.context.id),
                        obj,
                        lambda: f)
            except PlominoScriptException, e:
                p = self.context.absolute_url_path()
                e.reportError(
                        '%s field selection list formula failed' % 
                        self.context.id,
                        path=p+'/getSettings?key=selectionlistformula')
                s = []
        else:
            s = self.selectionlist
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
        """Return a JSON table storing documents to be displayed
        """

        return json.dumps([v.split('|')[::-1] for v in selection])


for f in getFields(ISelectionField).values():
    setattr(SelectionField, f.getName(), DictionaryProperty(f, 'parameters'))


class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(ISelectionField)

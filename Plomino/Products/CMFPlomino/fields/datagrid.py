# -*- coding: utf-8 -*-
#
# File: datagrid.py
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
from zope.schema import Text, TextLine
from zope.schema.vocabulary import SimpleVocabulary

import simplejson as json

from dictionaryproperty import DictionaryProperty

from Products.Five.formlib.formbase import EditForm

from Products.CMFPlomino.PlominoUtils import csv_to_array

from base import IBaseField, BaseField

class IDatagridField(IBaseField):
    """
    Text field schema
    """
    associated_form = TextLine(title=u'Associated form',
                description=u'Form to use to create/edit rows',
                required=False)
    
    field_mapping = TextLine(title=u'Columns/fields mapping',
                description=u'Field ids from the associated form, ordered as the columns, separated by commas',
                required=False)
        
    jssettings = Text(title=u'Javascript settings',
                      description=u'jQuery datatable parameters',
                      default=u"""
"aoColumns": [
    { "sTitle": "Column 1" },
    { "sTitle": "Column 2", "sClass": "center" }
],
"bPaginate": false,
"bLengthChange": false,
"bFilter": false,
"bSort": false,
"bInfo": false,
"bAutoWidth": false
""",
                      required=False)

class DatagridField(BaseField):
    """
    """
    implements(IDatagridField)
    
    def getParameters(self):
        """
        """
        return self.jssettings
    
    def processInput(self, submittedValue):
        """
        """
        try:
            return json.loads(submittedValue)
        except:
            return []
    
    def tojson(self, value):
        """
        """
        if value is None or value == "":
            value = []
        return json.dumps(value)
    
for f in getFields(IDatagridField).values():
    setattr(DatagridField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(EditForm):
    """
    """
    form_fields = form.Fields(IDatagridField)
    
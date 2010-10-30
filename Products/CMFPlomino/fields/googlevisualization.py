# -*- coding: utf-8 -*-
#
# File: googlevisualization.py
#
# Copyright (c) 2009 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields
from zope.schema import Text, TextLine

from dictionaryproperty import DictionaryProperty

from Products.Five.formlib.formbase import EditForm

from base import IBaseField, BaseField

class IGooglevisualizationField(IBaseField):
    """
    Google chart field schema
    """
    jssettings = Text(title=u'Javascript settings',
                      description=u'Google Vizualization code',
                      default=u"""
google.load('visualization', '1', {packages:['orgchart']});
google.setOnLoadCallback(gvisudata_drawChart);
var gvisudata;

function gvisudata_drawChart() {
gvisudata = new google.visualization.DataTable();
gvisudata.addColumn('string', 'Name');
gvisudata.addColumn('string', 'Manager');
gvisudata.addColumn('string', 'ToolTip');
gvisudata_getCells();
var gvisudata_chart = new google.visualization.OrgChart(document.getElementById('gvisudata_div'));
gvisudata_chart.draw(gvisudata, {allowHtml:true});
}
""",
                      required=False)
    chartid = TextLine(title=u'Chart id',
                      description=u'Used to name the javascript variable/functions and the DIV element',
                      required=True,
                      default=u'gvisudata')

class GooglevisualizationField(BaseField):
    """ GooglevisualizationField allows to render a datatable using the Google
    Visulization tools.
    The field value is supposed to be an array of array containing the values
    each columns declared in the Google Vizualization javascript code.
    Example:
    if columns declaration is:
    gvisudata.addColumn('string', 'Name');
    gvisudata.addColumn('string', 'Manager');
    gvisudata.addColumn('string', 'ToolTip');
    (typical case when using orgchart package)
    then the field value must be like:
    [['\'Mike\',\'Mike<div style="color:red; font-style:italic">President</div>\'', "''", "'The pres'"],
    ["'Tim'", "'Mike'", "'vp'"],
    ["'Tom'", "'Mike'", "'chief'"]]
    Notes:
    - strings must be enclosed in quotes (as they will be inserted in JS code)
    - when editing the field value from the form, the rows are separated with a newline,
    and the cells are separated with a pipe:
    'Mike','Mike<div style="color:red; font-style:italic">President</div>'|''|'The pres'
    'Tim'|'Mike'|'vp'
    'Tom'|'Mike'|'chief'
    
    More information about Google Visualization javascript APIs:
    http://code.google.com/intl/en/apis/visualization/documentation/
    """
    implements(IGooglevisualizationField)

    def validate(self, submittedValue):
        """
        """
        errors=[]
        # no validation needed
        return errors
    
    def processInput(self, submittedValue):
        """
        """
        lines = submittedValue.replace('\r', '').split('\n')
        datatable = []
        for l in lines:
            datatable.append(l.split('|'))
        return datatable
    
    def jscode(self, datatable):
        """ return Google visualization js code
        """
        js = self.jssettings + "\n"
        js = js + "function " + self.chartid + "_getCells() {\n"
        js = js + self.chartid+".addRows(" + str(len(datatable)) + ");\n"
        i = 0
        for row in datatable:
            j = 0
            for cell in row:
                js = js + self.chartid+".setCell(" + str(i) + ", " + str(j) + ", " + cell + ");\n"
                j = j + 1
            i = i + 1
        js = js + "}"
        return js

    
for f in getFields(IGooglevisualizationField).values():
    setattr(GooglevisualizationField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(EditForm):
    """
    """
    form_fields = form.Fields(IGooglevisualizationField)
    

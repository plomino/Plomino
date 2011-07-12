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

from Products.CMFPlomino.PlominoUtils import asList

from base import IBaseField, BaseField, BaseForm

class IGooglevisualizationField(IBaseField):
    """
    Google chart field schema
    """
    jssettings = Text(title=u'Javascript settings',
                      description=u'Google Vizualization code',
                      default=u"""
google.load('visualization', '1', {packages:['corechart']});
google.setOnLoadCallback(gvisudata_drawChart);
var gvisudata;

function gvisudata_drawChart() {
gvisudata = new google.visualization.DataTable();
gvisudata.addColumn('string', 'Category');
gvisudata.addColumn('number', 'Volume');
gvisudata_getCells();
var gvisudata_chart = new google.visualization.PieChart(document.getElementById('gvisudata_div'));
gvisudata_chart.draw(gvisudata, {width: 400, height: 400, is3D: true});
}
""",
                      required=False)
    chartid = TextLine(title=u'Chart id',
                      description=u'Used to name the javascript variable/functions and the DIV element',
                      required=True,
                      default=u'gvisudata')

class GooglevisualizationField(BaseField):
    """ GooglevisualizationField allows to render a datatable using the Google
    Visualization tools.

    The field value should be list of lists. Each child list contains the
    values for the columns declared in the Google Vizualization javascript
    code.

    Example:

    If the columns declaration is:

        gvisudata.addColumn('string', 'Name');
        gvisudata.addColumn('string', 'Manager');
        gvisudata.addColumn('string', 'ToolTip');

    (typical case when using orgchart package) then the field value should look
    like:

    [['\'Mike\',\'Mike<div style="color:red; font-style:italic">President</div>\'', "''", "'The pres'"],
    ["'Tim'", "'Mike'", "'vp'"],
    ["'Tom'", "'Mike'", "'chief'"]]

    Notes:
    - strings must be enclosed in quotes (as they will be inserted in JS code)
    - when editing the field value from the form, the rows are separated with a
      newline, and the cells are separated with a pipe:

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
        if type(datatable) is dict:
            # if dict, we convert it to googleviz compliant array
            labels = datatable.keys()
            labels.sort()
            tmp = []
            for label in labels:
                valuelist = ["'%s'" % label]
                for e in asList(datatable[label]):
                    if isinstance(e, basestring):
                        valuelist.append("'%s'" % e)
                    else:
                        valuelist.append(str(e))
                tmp.append(valuelist)
            datatable = tmp
            
        js = self.jssettings + "\n"
        js = js + "function " + self.chartid + "_getCells() {\n"
        js = js + self.chartid+".addRows(" + str(len(datatable)) + ");\n"
        i = 0
        for row in datatable:
            j = 0
            for cell in row:
                js = js + self.chartid+".setValue(" + str(i) + ", " + str(j) + ", " + cell + ");\n"
                j = j + 1
            i = i + 1
        js = js + "}"
        return js


for f in getFields(IGooglevisualizationField).values():
    setattr(GooglevisualizationField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IGooglevisualizationField)


# -*- coding: utf-8 -*-

from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform import directives as form
from plone.supermodel import directives, model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema

from .. import _
from ..utils import asList
from base import BaseField

js_func_template = """\
%(jssettings)s

function %(chartid)s_getCells() {
    %(chartid)s.addRows(%(num_rows)s);
    %(rows)s
}"""

js_row_template = """\
    %(chartid)s.setValue(%(row_nr)s, %(col_nr)s, %(cell)s);
"""


@provider(IFormFieldProvider)
class IGooglevisualizationField(model.Schema):
    """ Google viz field schema
    """

    directives.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=('jssettings', 'chartid', ),
    )

    form.widget('jssettings', klass='plomino-formula')
    jssettings = schema.Text(
        title=u'Javascript settings',
        description=u'Google Vizualization code',
        default=u"""
google.load('visualization', '1', {packages: ['corechart']});
google.setOnLoadCallback(gvisudata_drawChart);
var gvisudata;

function gvisudata_drawChart() {
    gvisudata = new google.visualization.DataTable();
    gvisudata.addColumn('string', 'Category');
    gvisudata.addColumn('number', 'Volume');
    gvisudata_getCells();

    var gvisudata_chart = new google.visualization.PieChart(
        document.getElementById('gvisudata_div'));

    google.visualization.events.addListener(
        gvisudata_chart,
        'ready',
        fixGoogleCharts('gvisudata_div'));

    gvisudata_chart.draw(
        gvisudata, {
            width: 400,
            height: 400,
            is3D: true
            }
        );
}
""",
        required=False)

    chartid = schema.TextLine(
        title=u'Chart id',
        description=u"Used to name the javascript variable/functions "
        "and the DIV element",
        required=True,
        default=u'gvisudata')


@implementer(IGooglevisualizationField)
class GooglevisualizationField(BaseField):
    """ GooglevisualizationField allows to render a datatable using the
    Google Visualization tools.

    The field value should be list of lists. Each child list contains the
    values for the columns declared in the Google Visualization javascript
    code.

    Example:

    If the columns declaration is:

        gvisudata.addColumn('string', 'Name');
        gvisudata.addColumn('string', 'Manager');
        gvisudata.addColumn('string', 'ToolTip');

    (typical case when using orgchart package) then the field value should
    look like:

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

    read_template = PageTemplateFile('googlevisualization_read.pt')
    edit_template = PageTemplateFile('googlevisualization_edit.pt')

    def validate(self, submittedValue):
        """
        """
        errors = []
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
        """ Return Google visualization JS code
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

        rows = []
        i = 0
        for row in datatable:
            j = 0
            for cell in row:
                rows.append(js_row_template % {
                    'chartid': self.chartid,
                    'row_nr': i,
                    'col_nr': j,
                    'cell': cell})
                j = j + 1
            i = i + 1

        js = js_func_template % {
            'jssettings': self.jssettings,
            'chartid': self.chartid,
            'num_rows': str(len(datatable)),
            'rows': ''.join(rows)}

        return js

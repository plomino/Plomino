from AccessControl import ClassSecurityInfo, Unauthorized
import cStringIO
import csv
from plone.autoform import directives
from plone.batching.batch import Batch
from plone.dexterity.content import Container
from plone.supermodel import model
from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
from zipfile import ZipFile, ZIP_DEFLATED
from zope import schema
from zope.interface import implements

# 3rd party Python
from jsonutil import jsonutil as json
from dateutil.parser import parse as parse_date

from .. import _
from ..config import (
    READ_PERMISSION,
    SCRIPT_ID_DELIMITER,
)
from ..exceptions import PlominoScriptException
from ..interfaces import IPlominoContext

batch = Batch.fromPagenumber

XLS_TABLE = """<html><head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
<body><table>
%s
</table></body></html>"""
TR = """<tr>%s</tr>"""
TD = """<td>%s</td>"""


class IPlominoView(model.Schema):
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

    directives.widget('selection_formula', klass='plomino-formula')
    selection_formula = schema.Text(
        title=_('CMFPlomino_label_SelectionFormula',
            default="Selection formula"),
        description=_('CMFPlomino_help_SelectionFormula',
            default="""The view selection formula is a line of Python code """
            """which should return True or False. The formula will be """
            """evaluated for each document in the database to decide if the """
            """document must be displayed in the view or not. """
            """'plominoDocument' is a reserved name in formulae: it returns """
            """the current Plomino document."""),
        default=u"True",
        required=True,
    )

    directives.widget('form_formula', klass='plomino-formula')
    form_formula = schema.Text(
        title=_('CMFPlomino_label_FormFormula', default="Form formula"),
        description=_('CMFPlomino_help_FormFormula',
            default='Documents open from the view will use the form defined '
            'by the following formula(they use their own form if empty)'),
        required=False
    )

    hide_default_actions = schema.Bool(
        title=_('CMFPlomino_label_HideViewDefaultActions',
            default="Hide default actions"),
        description=_('CMFPlomino_help_HideViewDefaultActions',
            default='Delete, Close actions will not be displayed in the '
            'action bar'),
        default=False,
    )

    directives.widget('onOpenView', klass='plomino-formula')
    onOpenView = schema.Text(
        title=_('CMFPlomino_label_onOpenView', default="On open view"),
        description=_('CMFPlomino_help_onOpenView',
            default="Action to take when the view is opened. If a string is "
            "returned, it is considered an error message, and the opening is "
            "not allowed."),
        required=False,
    )

    sort_column = schema.Choice(
        vocabulary="Products.CMFPlomino.columns.vocabularies.get_columns",
        title=_('CMFPlomino_label_SortColumn', default="Sort column"),
        description=_('CMFPlomino_help_SortColumn',
            default="Column used to sort the view, and for key lookup"),
        required=False,
    )

    key_column = schema.Choice(
        vocabulary="Products.CMFPlomino.columns.vocabularies.get_columns",
        title=_('CMFPlomino_label_KeyColumn', default="Key column"),
        description=_('CMFPlomino_help_KeyColumn',
            default="Column used for key lookup, if different from sort column"),
        required=False,
    )

    categorized = schema.Bool(
        title=_('CMFPlomino_label_Categorized', default="Categorized"),
        description=_('CMFPlomino_help_Categorized',
            default='Categorised on first column'),
        default=False,
    )

    reverse_sorting = schema.Bool(
        title=_('CMFPlomino_label_ReverseSorting', default="Reverse sorting"),
        description=_('CMFPlomino_help_ReverseSorting',
            default="Reverse the sort ordering"),
        default=False,
    )

    static_rendering = schema.Bool(
        title=_('CMFPlomino_label_static_rendering',
            default="Static rendering"),
        description=_('CMFPlomino_help_static_rendering',
            default='Use inline HTML, without AJAX.'),
        default=False,
    )


class PlominoView(Container):
    implements(IPlominoView, IPlominoContext)

    security = ClassSecurityInfo()

    security.declarePublic('checkBeforeOpenView')

    def checkBeforeOpenView(self):
        """ Check read permission and open view.

        NOTE: if READ_PERMISSION is set on the 'view' action itself, it
        causes error 'maximum recursion depth exceeded' if user hasn't
        permission.
        """
        if self.checkUserPermission(READ_PERMISSION):
            valid = ''
            try:
                if self.getOnOpenView():
                    valid = self.runFormulaScript(
                        SCRIPT_ID_DELIMITER.join(['view', self.id, 'onopen']),
                        self,
                        self.getOnOpenView)
            except PlominoScriptException, e:
                e.reportError('onOpenView event failed')

            if valid:
                return self.ErrorMessages(errors=[valid])

            if self.getViewTemplate():
                pt = self.resources._getOb(self.getViewTemplate())
                return pt.__of__(self)()
            else:
                return self.OpenView()
        else:
            raise Unauthorized("You cannot read this content")

    security.declarePublic('getAllDocuments')

    def getAllDocuments(
        self,
        pagenumber=1,
        pagesize=None,
        only_allowed=True,
        getObject=True,
        fulltext_query=None,
        sortindex=None,
        reverse=None,
        request_query=None,
    ):
        """ Return a subset of documents that matches the view. """
        index = self.getParentDatabase().getIndex()

        if not sortindex and self.sort_column:
            sortindex = self.getIndexKey(self.sort_column)

        if not reverse:
            reverse = self.reverse_sorting

        query = dict()
        if request_query is not None:
            query.update(request_query)
        # in this way you can search only inside view results
        query.update({'PlominoViewFormula_' + self.id: True})

        if fulltext_query:
            query['SearchableText'] = fulltext_query

        results = index.dbsearch(
            query,
            sortindex=sortindex,
            reverse=reverse,
            only_allowed=only_allowed)

        if pagesize:
            results = batch(
                results,
                pagesize=pagesize,
                pagenumber=pagenumber,
            )
        if getObject:
            return [r.getObject() for r in results]
        else:
            return results

    security.declarePublic('getColumns')

    def getColumns(self):
        """ Get columns
        """
        columnslist = self.portal_catalog.search(
            {'portal_type': ['PlominoColumn'],
                'path': '/'.join(self.getPhysicalPath())},
            sort_index='getObjPositionInParent')
        return [c.getObject() for c in columnslist]

    security.declarePublic('getActions')

    def getActions(self, hide=True):
        """ Get filtered actions for the view.
        """
        actions = [obj for obj in self.objectValues()
            if obj.__class__.__name__ == 'PlominoAction']

        filtered = []
        for action in actions:
            if hide:
                if not action.isHidden(self, self):
                    filtered.append((action, self.id))
            else:
                filtered.append((action, self.id))
        return filtered

    security.declarePublic('getColumn')

    def getColumn(self, column_name):
        """ Get a single column
        """
        return getattr(self, column_name)

    security.declarePublic('evaluateViewForm')

    def evaluateViewForm(self, doc):
        """ Compute the form to be used to open documents
        """
        try:
            result = self.runFormulaScript(
                SCRIPT_ID_DELIMITER.join(['view', self.id, 'formformula']),
                doc,
                self.form_formula)
        except PlominoScriptException, e:
            e.reportError('"%s" form formula failed' % self.Title())
            result = ""
        return result

    security.declarePublic('declareColumn')

    def declareColumn(self, column_name, column_obj, index=None):
        """ Declare column
        """
        db = self.getParentDatabase()
        refresh = not(db.do_not_reindex)

        if index is None:
            index = db.getIndex()

        if column_obj.formula:
            index.createIndex(
                'PlominoViewColumn_%s_%s' % (
                    self.id,
                    column_name),
                refresh=refresh)
        else:
            fieldpath = column_obj.displayed_field.split('/')
            form = self.getParentDatabase().getForm(fieldpath[0])
            if form:
                field = form.getFormField(fieldpath[1])
                if field:
                    field.to_be_indexed = True
                    index.createFieldIndex(
                        field.id,
                        field.field_type,
                        refresh=refresh,
                        indextype=field.index_type,
                        fieldmode=field.field_mode)
                else:
                    column_obj.formula = "'Non-existing field'"
                    index.createIndex(
                        'PlominoViewColumn_%s_%s' % (
                            self.id, column_name),
                        refresh=refresh)
            else:
                index.createIndex(
                    'PlominoViewColumn_%s_%s' % (
                        self.id, column_name),
                    refresh=refresh)

    security.declarePublic('getCategorizedColumnValues')

    def getCategorizedColumnValues(self, column_name):
        """ Return existing values for the given key and add the empty value
        """
        brains = self.getAllDocuments(getObject=False)
        column_values = [
            getattr(b, self.getIndexKey(column_name)) for b in brains]
        categories = {}
        for value in column_values:
            if isinstance(value, list):
                for v in value:
                    if v in categories:
                        categories[v] += 1
                    else:
                        categories[v] = 1
            else:
                if value is not None:
                    if value in categories:
                        categories[value] += 1
                    else:
                        categories[value] = 1
        uniquevalues = categories.keys()
        uniquevalues.sort()
        return [(v, categories[v]) for v in uniquevalues]

    security.declarePublic('getCategoryViewEntries')

    def getCategoryViewEntries(self, category_column_name, category_value):
        """ Get category view entry
        """
        index = self.getParentDatabase().getIndex()
        sortindex = self.sort_column
        if sortindex == '':
            sortindex = None
        else:
            sortindex = self.getIndexKey(sortindex)

        return index.dbsearch(
            {'PlominoViewFormula_' + self.id: True,
                self.getIndexKey(category_column_name): category_value},
            sortindex,
            self.reverse_sorting)

    def makeArray(self, brains, columns):
        """ Turn a list of brains and column names into a list of values.
        Encode values as utf-8.
        """
        rows = []
        for b in brains:
            row = []
            for column in columns:
                column_value = getattr(b, self.getIndexKey(column.id))
                column_value = column.getColumnRender(column_value)
                if column_value is None:
                    column_value = ''
                elif isinstance(column_value, basestring):
                    column_value = column_value.encode('utf-8')
                else:
                    column_value = unicode(column_value).encode('utf-8')
                row.append(column_value)
            rows.append(row)
        return rows

    security.declareProtected(READ_PERMISSION, 'exportCSV')

    def exportCSV(self,
            REQUEST=None,
            displayColumnsTitle='False',
            separator="\t",
            brain_docs=None,
            quotechar='"',
            quoting=csv.QUOTE_NONNUMERIC):
        """ Export columns values as CSV.

        IMPORTANT: brain_docs are supposed to be ZCatalog brains
        """
        if REQUEST:
            if REQUEST.get("separator"):
                separator = REQUEST.get("separator")
            if REQUEST.get("displayColumnsTitle"):
                displayColumnsTitle = REQUEST.get("displayColumnsTitle")

        if isinstance(quoting, basestring):
            # convert to int when passed via querystring
            try:
                quoting = int(quoting)
            except:
                quoting = csv.QUOTE_NONNUMERIC

        if brain_docs is None:
            brain_docs = self.getAllDocuments(getObject=False)

        columns = [c for c in self.getColumns()
            if not getattr(c, 'HiddenColumn', False)]

        stream = cStringIO.StringIO()
        writer = csv.writer(stream,
                delimiter=separator,
                quotechar=quotechar,
                quoting=quoting)

        # add column titles
        if displayColumnsTitle == 'True':
            titles = [c.title.encode('utf-8') for c in columns]
            writer.writerow(titles)

        rows = self.makeArray(brain_docs, columns)
        writer.writerows(rows)

        if REQUEST:
            REQUEST.RESPONSE.setHeader(
                'content-type', 'text/csv; charset=utf-8')
            REQUEST.RESPONSE.setHeader(
                'Content-Disposition',
                'attachment; filename=' + self.id + '.csv'
            )
        return stream.getvalue()

    security.declareProtected(READ_PERMISSION, 'exportZIP')

    def exportZIP(self,
            REQUEST=None,
            displayColumnsTitle='False',
            separator="\t",
            brain_docs=None,
            quotechar='"',
            quoting=csv.QUOTE_NONNUMERIC,
            filename=''):
        """ Export CSV as ZIP
        """
        if REQUEST:
            if REQUEST.get("separator"):
                separator = REQUEST.get("separator")
            if REQUEST.get("displayColumnsTitle"):
                displayColumnsTitle = REQUEST.get("displayColumnsTitle")
        data = self.exportCSV(
            None,
            displayColumnsTitle,
            separator,
            brain_docs,
            quotechar,
            quoting,
        )
        file_string = cStringIO.StringIO()
        zip_file = ZipFile(file_string, 'w', ZIP_DEFLATED)
        if not filename:
            filename = self.id
        zip_file.writestr(filename + '.csv', data)
        zip_file.close()

        if REQUEST:
            REQUEST.RESPONSE.setHeader(
                'content-type', 'application/zip')
            REQUEST.RESPONSE.setHeader(
                'Content-Disposition',
                'attachment; filename=' + filename + '.zip'
            )
        return file_string.getvalue()

    security.declareProtected(READ_PERMISSION, 'exportXLS')

    def exportXLS(self, REQUEST, displayColumnsTitle='False',
            brain_docs=None):
        """ Export column values to an HTML table, and set content-type to
        launch Excel.

        IMPORTANT: brain_docs are supposed to be ZCatalog brains
        """
        if REQUEST:
            if REQUEST.get("displayColumnsTitle"):
                displayColumnsTitle = REQUEST.get("displayColumnsTitle")

        if brain_docs is None:
            brain_docs = self.getAllDocuments(getObject=False)

        columns = [c for c in self.getColumns()
            if not getattr(c, 'HiddenColumn', False)]

        rows = self.makeArray(brain_docs, columns)

        # add column titles
        if displayColumnsTitle == 'True':
            titles = [c.title.encode('utf-8') for c in self.getColumns()
                if not getattr(c, 'HiddenColumn', False)]
            rows = [titles] + rows

        html = XLS_TABLE % (
            ''.join([TR %
                ''.join([TD % v for v in row]) for row in rows]))

        REQUEST.RESPONSE.setHeader(
            'content-type', 'application/vnd.ms-excel; charset=utf-8')
        REQUEST.RESPONSE.setHeader(
            'Content-Disposition', 'inline; filename=' + self.id + '.xls')
        return html

    security.declarePublic('getDocumentsByKey')

    def getDocumentsByKey(self, key, getObject=True):
        """ Get documents where key or sorted column matches the given key
        """
        index = self.getParentDatabase().getIndex()
        keycolumn = self.key_column
        sortcolumn = self.sort_column

        if not (keycolumn or sortcolumn):
            return []

        if sortcolumn:
            sortkey = self.getIndexKey(sortcolumn)
        else:
            sortkey = None

        query = {'PlominoViewFormula_%s' % self.id: True}
        if keycolumn:
            query[self.getIndexKey(keycolumn)] = key
        elif sortcolumn:
            query[sortkey] = key

        results = index.dbsearch(
            query,
            sortkey,
            self.reverse_sorting)

        if getObject:
            # TODO: keep lazy
            return [d.getObject() for d in results]
        else:
            return results

    def __query_loads__(self, request_query):
        """ """
        # Some fields might express a date
        # We try to convert those strings to datetime
        indexes = self.getParentDatabase().getIndex().Indexes
        request_query = json.loads(request_query)
        for key, value in request_query.iteritems():
            if key in indexes:
                index = indexes[key]
                # This is lame: we should check if it quacks, not
                # if it's a duck!
                # XXX Use a more robust method to tell apart
                # date indexes from non-dates

                if isinstance(index, DateIndex):
                    # convert value(s) to date(s)
                    if isinstance(value, basestring):
                        request_query[key] = parse_date(value)
                    elif 'query' not in value:
                        # it means value is a list of date values to be used
                        # with the implicit default operator query OR
                        request_query[key] = map(parse_date, value)
                    else:
                        # it means value is a dictionary
                        if isinstance(value['query'], basestring):
                            # query got a single comparison value
                            request_query[key]['query'] = parse_date(
                                value['query'])
                        else:
                            # query got a list of comparison values
                            request_query[key]['query'] = map(
                                parse_date, value['query']
                            )

        return request_query

    security.declarePublic('getIndexKey')

    def getIndexKey(self, columnName):
        """ Returns an index key if one exists.

        We try to find a computed index ('PlominoViewColumn_*');
        if not found, we look for a field.
        """
        key = 'PlominoViewColumn_%s_%s' % (self.id, columnName)
        if key not in self.getParentDatabase().plomino_index.Indexes:
            fieldPath = self.getColumn(columnName).displayed_field.split('/')
            if len(fieldPath) > 1:
                key = fieldPath[1]
            else:
                key = ''
        return key

# -*- coding: utf-8 -*-
#
# File: PlominoView.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'

# From the standard library
import cStringIO
import csv
from zipfile import ZipFile, ZIP_DEFLATED

# 3rd party Python
from jsonutil import jsonutil as json
from dateutil.parser import parse as parse_date

# Zope
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.folder import ATFolder
from zope.interface import implements
from Products.CMFPlomino.PlominoUtils import translate

# Plone
try:
    from plone.batching.batch import Batch
    batch = Batch.fromPagenumber
    
except:
    # < 4.3 compatibility
    from plone.app.content.batching import Batch
    batch = Batch


from Products.PluginIndexes.DateIndex.DateIndex import DateIndex

# Plomino
from exceptions import PlominoScriptException
from PlominoUtils import asUnicode, asList
from Products.CMFPlomino.config import *
from Products.CMFPlomino.browser import PlominoMessageFactory as _
from validator import isValidPlominoId

from Products.CMFPlomino.PlominoUtils import asUnicode, asList
from dateutil.parser import parse as parse_date
from Products.PluginIndexes.DateIndex.DateIndex import DateIndex
from Products.CMFPlomino.index import PlominoIndex


    

import interfaces

import logging
logger = logging.getLogger('Plomino')

schema = Schema((
    StringField(
        name='id',
        widget=StringField._properties['widget'](
            label="Id",
            description="If changed after creation, database refresh is needed",
            label_msgid=_('CMFPlomino_label_view_id', default="Id"),
            description_msgid=_('CMFPlomino_help_view_id', default="If changed after creation, database refresh is needed"),
            i18n_domain='CMFPlomino',
        ),
        validators = ("isValidId", isValidPlominoId),
    ),
    TextField(
        name='SelectionFormula',
        widget=TextAreaWidget(
            label="Selection formula",
            description="""The view selection formula is a line of Python
code which should return True or False. The formula will be evaluated for
each document in the database to decide if the document must be displayed in
the view or not. 'plominoDocument' is a reserved name in formulae: it
returns the current Plomino document.""",
            label_msgid=_('CMFPlomino_label_SelectionFormula', default="Selection formula"),
            description_msgid=_('CMFPlomino_help_SelectionFormula', default="""The view selection formula is a line of Python code which should return True or False. The formula will be evaluated for
each document in the database to decide if the document must be displayed in
the view or not. 'plominoDocument' is a reserved name in formulae: it
returns the current Plomino document."""),
            i18n_domain='CMFPlomino',
        ),
        default = "True",
    ),
    StringField(
        name='SortColumn',
        widget=SelectionWidget(
            label="Sort column",
            description="Column used to sort the view",
            format='select',
            label_msgid=_('CMFPlomino_label_SortColumn', default="Sort column"),
            description_msgid=_('CMFPlomino_help_SortColumn', default="Column used to sort the view, and by default for key lookup"),
            i18n_domain='CMFPlomino',
        ),
        vocabulary="Column_vocabulary",
        schemata="Sorting",
    ),
    StringField(
        name='KeyColumn',
        widget=SelectionWidget(
            label="Key column",
            description="Column used for key lookup",
            format='select',
            label_msgid=_('CMFPlomino_label_KeyColumn', default="Key column"),
            description_msgid=_('CMFPlomino_help_KeyColumn', default="Column used for key lookup, if different from sort column"),
            i18n_domain='CMFPlomino',
        ),
        vocabulary="Column_vocabulary",
        schemata="Sorting",
    ),
    BooleanField(
        name='Categorized',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Categorized",
            description="Categorised on first column",
            label_msgid=_('CMFPlomino_label_Categorized', default="Categorized"),
            description_msgid=_('CMFPlomino_help_Categorized', default='Categorised on first column'),
            i18n_domain='CMFPlomino',
        ),
        schemata="Sorting",
    ),
    TextField(
        name='FormFormula',
        widget=TextAreaWidget(
            label="Form formula",
            description="Documents open from the view will use the form "
                    "defined by the following formula "
                    "(they use their own form if empty)",
            label_msgid=_('CMFPlomino_label_FormFormula', default="Form formula"),
            description_msgid=_('CMFPlomino_help_FormFormula', default='Documents open from the view will use the form defined by the following formula(they use their own form if empty)'),
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='ReverseSorting',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Reverse sorting",
            description="Reverse sorting",
            label_msgid=_('CMFPlomino_label_ReverseSorting', default="Reverse sorting"),
            description_msgid=_('CMFPlomino_help_ReverseSorting', default="Reverse the sort ordering"),
            i18n_domain='CMFPlomino',
        ),
        schemata="Sorting",
    ),
    StringField(
        name='ActionBarPosition',
        default="TOP",
        widget=SelectionWidget(
            label="Position of the action bar",
            description="Select the position of the action bar",
            label_msgid=_('CMFPlomino_label_ActionBarPosition', default="Position of the action bar"),
            description_msgid=_('CMFPlomino_help_ActionBarPosition', default="Select the position of the action bar"),
            i18n_domain='CMFPlomino',
        ),
#        schemata="Parameters",
        vocabulary=[
            ["TOP", "At the top of the page"],
            ["BOTTOM", "At the bottom of the page"],
            ["BOTH", "At the top and at the bottom of the page "]],
    ),
    BooleanField(
        name='HideDefaultActions',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Hide default actions",
            description="Delete, Close actions will not be displayed in the action bar",
            label_msgid=_('CMFPlomino_label_HideViewDefaultActions', default="Hide default actions"),
            description_msgid=_('CMFPlomino_help_HideViewDefaultActions', default='Delete, Close actions will not be displayed in the action bar'),
            i18n_domain='CMFPlomino',
        ),
#        schemata="Parameters",
    ),
    BooleanField(
        name='HideCheckboxes',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Hide checkboxes",
            description="The first column with checkboxes will not be displayed",
            label_msgid=_('CMFPlomino_label_HideCheckboxes', default="Hide checkboxes"),
            description_msgid=_('CMFPlomino_help_HideCheckboxes', default='The first column with checkboxes will not be displayed'),
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='HideInMenu',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Hide in menu",
            description="It will not appear in the database main menu",
            label_msgid=_('CMFPlomino_label_HideInMenu', default="Hide in menu"),
            description_msgid=_('CMFPlomino_help_HideInMenu', default="It will not appear in the database main menu"),
            i18n_domain='CMFPlomino',
        ),
#        schemata="Parameters",
    ),
    StringField(
        name='Widget',
        default="BASIC",
        widget=SelectionWidget(
            label="Widget",
            description="Rendering mode",
            label_msgid=_('CMFPlomino_label_ViewWidget', default="Widget"),
            description_msgid=_('CMFPlomino_help_ViewWidget', default="Rendering mode"),
            i18n_domain='CMFPlomino',
        ),
        vocabulary= [
            ["BASIC", "Basic html"],
            ["DYNAMICTABLE", "Dynamic table"]],
#        schemata="Parameters",
    ),
    TextField(
        name='DynamicTableParameters',
        widget=TextAreaWidget(
            label="Dynamic Table Parameters",
            description="Change these options to customize the dynamic table.",
            label_msgid=_('CMFPlomino_label_DynamicTableParameters', default="Dynamic Table Parameters"),
            description_msgid=_('CMFPlomino_help_DynamicTableParameters', default='Change these options to customize the dynamic table.'),
            i18n_domain='CMFPlomino',
        ),
        default=u"""
'bPaginate': false,
'bLengthChange': false,
'bFilter': true,
'bSort': true,
'bInfo': true,
'bAutoWidth': false""",
#        schemata="Parameters",
    ),
    StringField(
        name='ViewTemplate',
        widget=StringField._properties['widget'](
            label="View template",
            description="Leave blank to use default",
            label_msgid=_('CMFPlomino_label_ViewTemplate', default="View template"),
            description_msgid=_('CMFPlomino_help_ViewTemplate', default="Leave blank to use default"),
            i18n_domain='CMFPlomino',
        ),
#        schemata="Parameters",
    ),
    TextField(
        name='onOpenView',
        widget=TextAreaWidget(
            label="On open view",
            description="Action to take when the view is opened. "
                "If a string is returned, it is considered an error "
                "message, and the opening is not allowed.",
            label_msgid=_('CMFPlomino_label_onOpenView', default="On open view"),
            description_msgid=_('CMFPlomino_help_onOpenView', default="Action to take when the view is opened. If a string is returned, it is considered an error message, and the opening is not allowed."),
            i18n_domain='CMFPlomino',
        ),
    ),
    IntegerField(
        name='Position',
        widget=IntegerField._properties['widget'](
            label="Position",
            label_msgid=_("CMFPlomino_label_Position", default="Position"),
            description="Position in menu",
            description_msgid=_("CMFPlomino_description_Position"),
            i18n_domain='CMFPlomino',
        ),
#        schemata="Parameters",
    ),
),
)

PlominoView_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    schema.copy()


XLS_TABLE = """<html><head>
<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
<body><table>
%s
</table></body></html>"""

TR = """<tr>%s</tr>"""
TD = """<td>%s</td>"""

class PlominoView(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoView)

    meta_type = 'PlominoView'
    _at_rename_after_creation = False

    schema = PlominoView_schema

    # Methods

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
            raise Unauthorized, "You cannot read this content"

    security.declarePublic('getViewName')
    def getViewName(self):
        """Get view name
        """
        return self.id

    def __bobo_traverse__(self, request, name):
        """ Allow traversing to .../<view>/<docid> 
        """
        if self.documents.has_key(name):
            return aq_inner(getattr(self.documents, name)).__of__(self)
        return BaseObject.__bobo_traverse__(self, request, name)

    security.declarePublic('getAllDocuments')
    def getAllDocuments(self, start=1, limit=None, only_allowed=True, getObject=True,
            fulltext_query=None, sortindex=None, reverse=None, request_query=None):
        """ Return a subset of documents that matches the view. """
        index = self.getParentDatabase().getIndex()

        if not sortindex:
            sortindex = self.getSortColumn()
            if sortindex == '':
                sortindex = None
            else:
                sortindex = self.getIndexKey(sortindex)

        if not reverse:
            reverse = self.getReverseSorting()

        query = dict()
        if not request_query is None:
            query.update(request_query)
        # in this way you can search only inside view results
        query.update({'PlominoViewFormula_'+self.getViewName(): True})

        if fulltext_query:
            query['SearchableText'] = fulltext_query

        results = index.dbsearch(
                query,
                sortindex=sortindex,
                reverse=reverse,
                only_allowed=only_allowed)

        if limit:
            results = batch(
                    results,
                    pagesize=limit,
                    pagenumber=int(start/limit)+1)
        if getObject:
            return [r.getObject() for r in results]
        else:
            return results
        # XXX: Fix the generator.
        # for r in results:
        #     if getObject:
        #         try:
        #             obj = r.getObject()
        #             yield obj
        #         except:
        #             logging.exception('Corrupt view: %s'%self.id, exc_info=True)
        #     else:
        #         yield r

    security.declarePublic('getColumns')
    def getColumns(self):
        """ Get columns
        """
        # TODO: why not just `return self.contentValues(filter='PlominoColumn')`?
        columnslist = self.portal_catalog.search(
                {'portal_type': ['PlominoColumn'],
                    'path': '/'.join(self.getPhysicalPath())},
                sort_index='getObjPositionInParent')
        return [c.getObject() for c in columnslist]

    security.declarePublic('getActions')
    def getActions(self, view, hide=True):
        """ Get filtered actions for the view.
        """
        # Note: We take 'view' as parameter (even though `self` and `view`
        # will always be the same) because `getActions` is called from
        # `ActionBar` template without knowing whether it's used for
        # view/document/page.
        actions = self.objectValues(spec='PlominoAction')

        filtered = []
        for action in actions:
            if hide:
                if not action.isHidden(view, self):
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
    def evaluateViewForm(self,doc):
        """ Compute the form to be used to open documents
        """
        try:
            #result = RunFormula(doc, self.getFormFormula())
            result = self.runFormulaScript(
                    SCRIPT_ID_DELIMITER.join(['view', self.id, 'formformula']),
                    doc,
                    self.FormFormula)
        except PlominoScriptException, e:
            e.reportError('"%s" form formula failed' % self.Title())
            result = ""
        return result

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        db = self.getParentDatabase()
        self.cleanFormulaScripts(SCRIPT_ID_DELIMITER.join(["view", self.id]))
        if not db.DoNotReindex:
            self.getParentDatabase().getIndex().refresh()

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        """ Post create
        """
        db = self.getParentDatabase()
        refresh = not db.DoNotReindex
        db.getIndex().createSelectionIndex(
                'PlominoViewFormula_'+self.getViewName(),
                refresh=refresh)
        if refresh:
            self.getParentDatabase().getIndex().refresh()

    security.declarePublic('declareColumn')
    def declareColumn(self, column_name, column_obj, index=None):
        """ Declare column
        """
        db = self.getParentDatabase()
        refresh = not(db.DoNotReindex)

        if index is None:
            index = db.getIndex()

        if column_obj.Formula:
            index.createIndex(
                    'PlominoViewColumn_%s_%s' % (
                        self.getViewName(),
                        column_name),
                    refresh=refresh)
        else:
            fieldpath = column_obj.SelectedField.split('/')
            form = self.getParentDatabase().getForm(fieldpath[0])
            if form:
                field = form.getFormField(fieldpath[1])
                if field:
                    field.setToBeIndexed(True)
                    #field.at_post_edit_script()
                    index.createFieldIndex(
                            field.id,
                            field.getFieldType(),
                            refresh=refresh,
                            indextype=field.getIndexType(),
                            fieldmode=field.getFieldMode())
                else:
                    column_obj.setFormula("'Non-existing field'")
                    index.createIndex(
                            'PlominoViewColumn_%s_%s' % (
                                self.getViewName(), column_name),
                            refresh=refresh)
            else:
                index.createIndex(
                        'PlominoViewColumn_%s_%s' % (
                            self.getViewName(), column_name),
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
        sortindex = self.getSortColumn()
        if sortindex == '':
            sortindex = None
        else:
            sortindex = self.getIndexKey(sortindex)

        return index.dbsearch(
                {'PlominoViewFormula_'+self.getViewName(): True,
                    self.getIndexKey(category_column_name): category_value},
                sortindex,
                self.getReverseSorting())

    security.declarePublic('getColumnSums')
    def getColumnSums(self):
        """ Return the sum of non-null values for each column marked as
        summable.
        """
        sums = {}
        brains = self.getAllDocuments(getObject=False)
        for column in self.getColumns():
            if column.DisplaySum:
                indexkey = self.getIndexKey(column.getColumnName())
                values = [getattr(b, indexkey) for b in brains]
                try:
                    s = sum([v for v in values if v])
                except:
                    logger.error('PlominoView', exc_info=True)
                    s = 0
                sums[column.id] = column.getColumnRender(s)
        return sums

    def makeArray(self, brains, columns):
        """ Turn a list of brains and column names into a list of values.
        Encode values as utf-8.
        """
        rows = []
        for b in brains:
            row = []
            for column in columns:
                column_value = getattr(b, self.getIndexKey(column.id))
                rendered = column.getColumnRender(column_value)
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
            #convert to int when passed via querystring
            try:
                quoting = int(quoting)
            except:
                logging.exception('Bad quoting: %s'%quoting, exc_info=True)
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
        if displayColumnsTitle=='True' :
            titles = [c.title.encode('utf-8') for c in columns]
            writer.writerow(titles)

        rows = self.makeArray(brain_docs, columns)
        writer.writerows(rows)

        if REQUEST:
            REQUEST.RESPONSE.setHeader(
                    'content-type', 'text/csv; charset=utf-8')
            REQUEST.RESPONSE.setHeader(
                    'Content-Disposition', 'attachment; filename='+self.id+'.csv')
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
        data = self.exportCSV(None, displayColumnsTitle, separator, brain_docs, quotechar, quoting)
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
                    'Content-Disposition', 'attachment; filename='+filename+'.zip')
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
                'Content-Disposition', 'inline; filename='+self.id+'.xls')
        return html


    security.declarePublic('getPosition')
    def getPosition(self):
        """ Return the view position in the database
        """
        try:
            return self.Position
        except Exception:
            logger.error('PlominoView', exc_info=True)
            return None

    security.declarePublic('getDocumentsByKey')
    def getDocumentsByKey(self, key, getObject=True):
        """ Get documents where key or sorted column matches the given key
        """
        index = self.getParentDatabase().getIndex()
        keycolumn = self.getKeyColumn()
        sortcolumn = self.getSortColumn()

        if not (keycolumn or sortcolumn):
            return []

        query = {'PlominoViewFormula_%s' % self.getViewName(): True}
        sortkey = None
        if keycolumn:
            query[self.getIndexKey(keycolumn)] = key
        elif sortcolumn:
            sortkey = self.getIndexKey(sortcolumn)
            query[sortkey] = key

        results = index.dbsearch(
                query,
                sortkey,
                self.getReverseSorting())

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
                    elif not 'query' in value:
                        # it means value is a list of date values to be used
                        # with the implicit default operator query OR
                        request_query[key] = map(parse_date, value)
                    else:
                        # it means value is a dictionary
                        if isinstance(value['query'], basestring):
                            # query got a single comparison value
                            request_query[key]['query'] = parse_date(value['query'])
                        else:
                            # query got a list of comparison values
                            request_query[key]['query'] = map(parse_date, value['query'])

        return request_query

    security.declarePublic('tojson')
    def tojson(self, REQUEST=None):
        """ Returns a JSON representation of view data
        """
        data = []
        categorized = self.getCategorized()
        start = 1
        limit = -1
        search = None
        sort_index = None
        reverse = None
        if REQUEST:
            REQUEST.RESPONSE.setHeader(
                    'content-type', 'application/json; charset=utf-8')
            start = int(REQUEST.get('iDisplayStart', 1))
            iDisplayLength = REQUEST.get('iDisplayLength', None)
            if iDisplayLength:
                limit = int(iDisplayLength)
            search = REQUEST.get('sSearch', '').lower()
            if search:
                search = ' '.join([term+'*' for term in search.split(' ')])
            sort_column = REQUEST.get('iSortCol_0')
            if sort_column:
                sort_index = self.getIndexKey(
                        self.getColumns()[int(sort_column)-1].id)
            reverse = REQUEST.get('sSortDir_0', None)
            if reverse == 'desc':
                reverse = 0
            if reverse == 'asc':
                reverse = 1
        if limit < 1:
            limit = None

        if not REQUEST is None and 'request_query' in REQUEST:
            # query parameter in REQUEST is supposed to be a json object
            request_query = self.__query_loads__(REQUEST['request_query'])
        else:
            request_query = None

        results = self.getAllDocuments(
                start=start,
                limit=limit,
                getObject=False,
                fulltext_query=search,
                sortindex=sort_index,
                reverse=reverse,
                request_query=request_query)
        total = display_total = len(results)
        columns = [column for column in self.getColumns()
                if not getattr(column, 'HiddenColumn', False)]
        for brain in results:
            row = [brain.getPath().split('/')[-1]]
            for column in columns:
                column_value = getattr(brain, self.getIndexKey(column.id), '')
                rendered = column.getColumnRender(column_value)
                if isinstance(rendered, list):
                    rendered = [asUnicode(e).encode('utf-8').replace('\r', '') for e in rendered]
                else:
                    rendered = asUnicode(rendered).encode('utf-8').replace('\r', '')
                row.append(rendered or '&nbsp;')
            if categorized:
                for cat in asList(row[1]):
                    entry = [c for c in row]
                    entry[1] = cat
                    data.append(entry)
            else:
                data.append(row)
        return json.dumps(
                    {'iTotalRecords': total,
                    'iTotalDisplayRecords': display_total,
                    'aaData': data })

    security.declarePublic('getIndexKey')
    def getIndexKey(self, columnName):
        """ Returns an index key if one exists.

        We try to find a computed index ('PlominoViewColumn_*');
        if not found, we look for a field.
        """
        key = 'PlominoViewColumn_%s_%s' % (self.getViewName(), columnName)
        if not key in self.getParentDatabase().plomino_index.Indexes:
            fieldPath = self.getColumn(columnName).SelectedField.split('/')
            if len(fieldPath) > 1:
                key = fieldPath[1]
            else:
                key = ''
        return key

    # Return all the documents matching the view and the custom filter criteria.
    security.declarePublic('queryDocuments')    
    def queryDocuments(self, start=1, limit=None, only_allowed=True,
        getObject=True, fulltext_query=None, sortindex=None, reverse=None,
        query_request={}):
        """
        Return all the documents matching the view and the custom filter criteria.
        """
        index = self.getParentDatabase().getIndex()
        if not sortindex:
            sortindex = self.getSortColumn()
            if sortindex=='':
                sortindex=None
            else:
                sortindex=self.getIndexKey(sortindex)
        if not reverse:
            reverse = self.getReverseSorting()
        query = {'PlominoViewFormula_'+self.getViewName() : True}

        total = len(index.dbsearch(query, only_allowed=only_allowed))

        query.update(query_request)

        if fulltext_query:
            query['SearchableText'] = fulltext_query
        results=index.dbsearch(
            query,
            sortindex=sortindex,
            reverse=reverse,
            only_allowed=only_allowed) # di fatto questo parametro NON viene usato dal metodo dbsearch
        if limit:
            results = batch(
                    results,
                    pagesize=limit,
                    pagenumber=int(start/limit)+1)
        if getObject:
            return [r.getObject() for r in results], total
        else:
            return results, total

    
    security.declarePublic('search_json')
    def search_json(self, REQUEST=None):
        """ Returns a JSON representation of view filtered data
        """
        data = []
        categorized = self.getCategorized()
        start = 1
        search = None
        sort_index = None
        reverse = 1

        if REQUEST:
            start = int(REQUEST.get('iDisplayStart', 1))

            limit = REQUEST.get('iDisplayLength')
            limit = (limit and int(limit))
            # In case limit == -1 we want it to be None
            if limit < 1:
                limit = None

            search = REQUEST.get('sSearch', '').lower()
            if search:
                search = " ".join([term+'*' for term in search.split(' ')])
            sort_column = REQUEST.get('iSortCol_0')
            if sort_column:
                sort_index = self.getIndexKey(self.getColumns()[int(sort_column)-1].id)
            reverse = REQUEST.get('sSortDir_0') or 'asc'
            if reverse=='desc':
                reverse = 0
            if reverse=='asc':
                reverse = 1

        query_request = json.loads(REQUEST['query'])
        # Some fields might express a date
        # We try to convert those strings to datetime
        #indexes = self.aq_parent.aq_base.plomino_index.Indexes
        indexes = self.getParentDatabase().getIndex().Indexes
        for key, value in query_request.iteritems():
            if key in indexes:
                index = indexes[key]
                # This is lame: we should check if it quacks, not
                # if it's a duck!
                # XXX Use a more robust method to tell apart
                # date indexes from non-dates

                # I'd use a solution like this one: http://getpython3.com/diveintopython3/examples/customserializer.py
                if isinstance(index, DateIndex):
                    # convert value(s) to date(s)
                    if isinstance(value, basestring):
                        query_request[key] = parse_date(value)
                    else:
                        if isinstance(value['query'], basestring):
                            value['query'] = parse_date(value['query'])
                        else:
                            query_request[key]['query'] = [parse_date(v) for v in value['query']]

        results, total = self.queryDocuments(start=1,
                                       limit=None,
                                       getObject=False,
                                       fulltext_query=search,
                                       sortindex=sort_index,
                                       reverse=reverse,
                                       query_request=query_request)
        
        if limit:
            results = batch(
                    results,
                    pagesize=limit,
                    pagenumber=int(start/limit)+1)
        display_total = len(results)
        
        columnids = [col.id for col in self.getColumns() if not getattr(col, 'HiddenColumn', False)]
        for b in results:
            row = [b.getPath().split('/')[-1]]
            for colid in columnids:
                v = getattr(b, self.getIndexKey(colid), '')
                if isinstance(v, list):
                    v = [asUnicode(e).encode('utf-8').replace('\r', '') for e in v]
                else:
                    v = asUnicode(v).encode('utf-8').replace('\r', '')
                row.append(v or '&nbsp;')
            if categorized:
                for cat in asList(row[1]):
                    entry = [c for c in row]
                    entry[1] = cat
                    data.append(entry)
            else:
                data.append(row)
        return json.dumps({ 'iTotalRecords': total, 'iTotalDisplayRecords': display_total, 'aaData': data })    

    def Column_vocabulary(self):
        return [''] + [c.id for c in self.getColumns()]

registerType(PlominoView, PROJECTNAME)
# end of class PlominoView

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

# Zope
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from Acquisition import aq_inner
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.folder import ATFolder
from zope.interface import implements

# Plone
try:
    from plone.batching.batch import Batch
    batch = Batch.fromPagenumber
except:
    # < 4.3 compatibility
    from plone.app.content.batching import Batch
    batch = Batch

# Plomino
from exceptions import PlominoScriptException
from PlominoUtils import asUnicode, asList
from Products.CMFPlomino.config import *
from Products.CMFPlomino.browser import PlominoMessageFactory as _
from validator import isValidPlominoId
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
            description_msgid=_('CMFPlomino_help_SortColumn', default="Column used to sort the view"),
            i18n_domain='CMFPlomino',
        ),
        vocabulary="_getcolumn_ids",
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
                            'view_%s_onopen' % self.id,
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
        if self.documents.has_key(name):
            return aq_inner(getattr(self.documents, name)).__of__(self)
        return BaseObject.__bobo_traverse__(self, request, name)

    security.declarePublic('getAllDocuments')
    def getAllDocuments(self, start=1, limit=None, only_allowed=True,
            getObject=True, fulltext_query=None, sortindex=None, reverse=None):
        """ Return all the documents matching the view.
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
        query = {'PlominoViewFormula_'+self.getViewName(): True}
        if fulltext_query:
            query['SearchableText'] = fulltext_query
        results=index.dbsearch(
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
        columnslist = self.portal_catalog.search(
                {'portal_type': ['PlominoColumn'],
                    'path': '/'.join(self.getPhysicalPath())},
                sort_index='getObjPositionInParent')
        return [c.getObject() for c in columnslist]

    security.declarePublic('getActions')
    def getActions(self, target, hide=True, parent_id=None):
        """Get actions
        """
        actions = self.objectValues(spec='PlominoAction')

        filtered = []
        for action in actions:
            if hide:
                try:
                    #result = RunFormula(target, action.getHidewhen())
                    result = self.runFormulaScript(
                            'action_%s_%s_hidewhen' % (
                                action.getParentNode().id,
                                action.id),
                            target,
                            action.Hidewhen,
                            True)
                except PlominoScriptException, e:
                    e.reportError(
                            '"%s" action hide-when failed' % action.Title())
                    # if error, we hide anyway
                    result = True
                if not result:
                    filtered.append((action, parent_id))
            else:
                filtered.append((action, parent_id))
        return filtered

    security.declarePublic('getColumn')
    def getColumn(self,column_name):
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
                    'view_%s_formformula' % self.id,
                    doc,
                    self.FormFormula)
        except PlominoScriptException, e:
            e.reportError('"%s" form formula failed' % self.Title())
            result = ""
        return result

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        db = self.getParentDatabase()
        self.cleanFormulaScripts("view_"+self.id)
        if not db.DoNotReindex:
            self.getParentDatabase().getIndex().refresh()

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        """ Post create
        """
        db = self.getParentDatabase()
        db.getIndex().createSelectionIndex(
                'PlominoViewFormula_'+self.getViewName())
        if not db.DoNotReindex:
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
                            indextype=field.getIndexType())
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
        for col in self.getColumns():
            if col.DisplaySum:
                indexkey = self.getIndexKey(col.getColumnName())
                values = [getattr(b, indexkey) for b in brains]
                try:
                    s = sum([v for v in values if v is not None])
                except:
                    logger.error('PlominoView', exc_info=True)
                    s = 0
                sums[col.id] = s
        return sums

    def makeArray(self, brains, columns):
        """ Turn a list of brains and column names into a list of values.
        Encode values as utf-8.
        """
        rows = []
        for b in brains:
            row = []
            for cname in columns:
                v = getattr(b, self.getIndexKey(cname))
                if v is None:
                    v = ''
                elif isinstance(v, basestring):
                    v = v.encode('utf-8')
                else:
                    v = unicode(v).encode('utf-8')
                row.append(v)
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

        columns = [c.id for c in self.getColumns()
            if not getattr(c, 'HiddenColumn', False)]

        stream = cStringIO.StringIO()
        writer = csv.writer(stream,
                delimiter=separator,
                quotechar=quotechar,
                quoting=quoting)

        # add column titles
        if displayColumnsTitle=='True' :
            titles = [c.title.encode('utf-8') for c in self.getColumns()
                      if not getattr(c, 'HiddenColumn', False)]
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
        if brain_docs is None:
            brain_docs = self.getAllDocuments(getObject=False)

        columns = [c.id for c in self.getColumns()
            if not getattr(c, 'HiddenColumn', False)]

        rows = self.makeArray(brain_docs, columns)

        # add column titles
        if displayColumnsTitle == 'True':
            titles = [c.title.encode('utf-8') for c in self.getColumns()
                if not getattr(c, 'HiddenColumn', False)]
            rows[0:0] = titles

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
        """ Get documents where the sorted column value matches the given key.
        """
        index = self.getParentDatabase().getIndex()
        sortindex = self.getSortColumn()
        if not sortindex:
            return []

        sortindex = self.getIndexKey(sortindex)
        results = index.dbsearch(
                    {'PlominoViewFormula_%s' % self.getViewName(): True,
                    sortindex: key},
                sortindex,
                self.getReverseSorting())

        if getObject:
            return [d.getObject() for d in results]
        else:
            return results

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
        results = self.getAllDocuments(
                start=start,
                limit=limit,
                getObject=False,
                fulltext_query=search,
                sortindex=sort_index,
                reverse=reverse)
        total = display_total = len(results)
        columnids = [col.id for col in self.getColumns()
                if not getattr(col, 'HiddenColumn', False)]
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

    def _getcolumn_ids(self):
        return [''] +  [c.id for c in self.getColumns()]

registerType(PlominoView, PROJECTNAME)
# end of class PlominoView

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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.CMFPlomino.config import *
from PlominoUtils import asUnicode, asList
from exceptions import PlominoScriptException
from validator import isValidPlominoId

from AccessControl import Unauthorized
import csv, cStringIO
from Acquisition import aq_inner
import PlominoDocument

import simplejson as json

import logging
logger = logging.getLogger('Plomino')

schema = Schema((

    StringField(
        name='id',
        widget=StringField._properties['widget'](
            label="Id",
            description="If changed after creation, database refresh is needed",
            label_msgid='CMFPlomino_label_view_id',
            description_msgid='CMFPlomino_help_view_id',
            i18n_domain='CMFPlomino',
        ),
        validators = ("isValidId", isValidPlominoId),
    ),
    TextField(
        name='SelectionFormula',
        widget=TextAreaWidget(
            label="Selection formula",
            description="The view selection formula is a line of Python code which should return True or False. The formula will be evaluated for each document in the database to decide if the document must be displayed in the view or not. plominoDocument is a reserved name in formulae, it returns the current Plomino document. Each document field value can be accessed directly as an attribute of the document: plominoDocument.<fieldname>",
            label_msgid='CMFPlomino_label_SelectionFormula',
            description_msgid='CMFPlomino_help_SelectionFormula',
            i18n_domain='CMFPlomino',
        ),
        default = "True",
    ),
    StringField(
        name='SortColumn',
        widget=StringField._properties['widget'](
            label="Sort column",
            description="Column used to sort the view",
            label_msgid='CMFPlomino_label_SortColumn',
            description_msgid='CMFPlomino_help_SortColumn',
            i18n_domain='CMFPlomino',
        ),
        schemata="Sorting",
    ),
    BooleanField(
        name='Categorized',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Categorized",
            description="Categorised on first column",
            label_msgid='CMFPlomino_label_Categorized',
            description_msgid='CMFPlomino_help_Categorized',
            i18n_domain='CMFPlomino',
        ),
        schemata="Sorting",
    ),
    TextField(
        name='FormFormula',
        widget=TextAreaWidget(
            label="Form formula",
            description="Documents open from the view will use the form defined by the following formula (they use their own form if empty)",
            label_msgid='CMFPlomino_label_FormFormula',
            description_msgid='CMFPlomino_help_FormFormula',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='ReverseSorting',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Reverse sorting",
            description="Reverse sorting",
            label_msgid='CMFPlomino_label_ReverseSorting',
            description_msgid='CMFPlomino_help_ReverseSorting',
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
            label_msgid='CMFPlomino_label_ActionBarPosition',
            description_msgid='CMFPlomino_help_ActionBarPosition',
            i18n_domain='CMFPlomino',
        ),
#        schemata="Parameters",
        vocabulary=[["TOP", "At the top of the page"], ["BOTTOM", "At the bottom of the page"], ["BOTH", "At the top and at the bottom of the page "]],
    ),
    BooleanField(
        name='HideDefaultActions',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Hide default actions",
            description="Delete, Close actions will not be displayed in the action bar",
            label_msgid='CMFPlomino_label_HideViewDefaultActions',
            description_msgid='CMFPlomino_help_HideViewDefaultActions',
            i18n_domain='CMFPlomino',
        ),
#        schemata="Parameters",
    ),
    BooleanField(
        name='HideInMenu',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Hide in menu",
            description="It will not appear in the database main menu",
            label_msgid='CMFPlomino_label_HideInMenu',
            description_msgid='CMFPlomino_help_HideInMenu',
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
            label_msgid='CMFPlomino_label_ViewWidget',
            description_msgid='CMFPlomino_help_ViewWidget',
            i18n_domain='CMFPlomino',
        ),
        vocabulary= [["BASIC", "Basic html"], ["DYNAMICTABLE", "Dynamic table"]],
#        schemata="Parameters",
    ),
    TextField(
        name='DynamicTableParameters',
        widget=TextAreaWidget(
            label="Dynamic Table Parameters",
            description="Change these options to customize the dynamic table.",
            label_msgid='CMFPlomino_label_DynamicTableParameters',
            description_msgid='CMFPlomino_help_DynamicTableParameters',
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
            label_msgid='CMFPlomino_label_ViewTemplate',
            description_msgid='CMFPlomino_help_ViewTemplate',
            i18n_domain='CMFPlomino',
        ),
#        schemata="Parameters",
    ),
    TextField(
        name='onOpenView',
        widget=TextAreaWidget(
            label="On open view",
            description="Action to take when the view is opened. If a string is returned, it is considered as an error message, and the openning is not allowed.",
            label_msgid='CMFPlomino_label_onOpenView',
            description_msgid='CMFPlomino_help_onOpenView',
            i18n_domain='CMFPlomino',
        ),
    ),
    IntegerField(
        name='Position',
        widget=IntegerField._properties['widget'](
            label="Position",
            label_msgid="CMFPlomino_label_Position",
            description="Position in menu",
            description_msgid="CMFPlomino_description_Position",
            i18n_domain='CMFPlomino',
        ),
#        schemata="Parameters",
    ),
),
)

PlominoView_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    schema.copy()

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
        """check read permission and open view NOTE: if READ_PERMISSION set
        on the 'view' action itself, it causes error 'maximum recursion
        depth exceeded' if user hasn't permission
        """
        if self.checkUserPermission(READ_PERMISSION):
            valid = ''
            try:
                if self.getOnOpenView():
                    valid = self.runFormulaScript("view_"+self.id+"_onopen", self, self.getOnOpenView)
            except PlominoScriptException, e:
                e.reportError('onOpenView event failed')
            
            if valid:
                return self.ErrorMessages(errors=[valid])

            if not self.getViewTemplate()=="":
                pt=self.resources._getOb(self.getViewTemplate())
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
    def getAllDocuments(self, start=1, limit=None, only_allowed=True, getObject=True):
        """ Return all the documents matching the view.
        """
        # Ignore 'start': batching should be done using PloneBatch.
        index = self.getParentDatabase().getIndex()
        sortindex = self.getSortColumn()
        if sortindex=='':
            sortindex=None
        else:
            sortindex=self.getIndexKey(sortindex)
        results=index.dbsearch(
            {'PlominoViewFormula_'+self.getViewName() : True},
            sortindex,
            self.getReverseSorting(),
            only_allowed=only_allowed,
            limit=limit)
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
        """Get colums
        """
        columnslist = self.portal_catalog.search({'portal_type' : ['PlominoColumn'], 'path': '/'.join(self.getPhysicalPath())}, sort_index='getObjPositionInParent')
        #orderedcolumns = []
        #for c in columnslist:
        #    c_obj = c.getObject()
        #    if not(c_obj is None):
        #        orderedcolumns.append([c_obj.Position, c_obj])
        #orderedcolumns.sort()
        #return [i[1] for i in orderedcolumns]
        return [c.getObject() for c in columnslist]

    security.declarePublic('getActions')
    def getActions(self, target, hide=True, parent_id=None):
        """Get actions
        """
        all = self.objectValues(spec='PlominoAction')
        
        filtered = []
        for obj_a in all:
            if hide:
                try:
                    #result = RunFormula(target, obj_a.getHidewhen())
                    result = self.runFormulaScript("action_"+obj_a.getParentNode().id+"_"+obj_a.id+"_hidewhen", target, obj_a.Hidewhen, True)
                except PlominoScriptException, e:
                    e.reportError('"%s" action hide-when failed' % obj_a.Title())
                    #if error, we hide anyway
                    result = True
                if not result:
                    filtered.append((obj_a, parent_id))
            else:
                filtered.append((obj_a, parent_id))
        return filtered

    security.declarePublic('getColumn')
    def getColumn(self,column_name):
        """Get a single column
        """
        return getattr(self, column_name)

    security.declarePublic('evaluateViewForm')
    def evaluateViewForm(self,doc):
        """compute the form to be used to open documents
        """
        try:
            #result = RunFormula(doc, self.getFormFormula())
            result = self.runFormulaScript("view_"+self.id+"_formformula", doc, self.FormFormula)
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
        """post create
        """
        db = self.getParentDatabase()
        db.getIndex().createSelectionIndex('PlominoViewFormula_'+self.getViewName())
        if not db.DoNotReindex:
            self.getParentDatabase().getIndex().refresh()

    security.declarePublic('declareColumn')
    def declareColumn(self,column_name,column_obj, index=None):
        """declare column
        """
        db = self.getParentDatabase()
        refresh = not(db.DoNotReindex)
        
        if index is None:
            index = db.getIndex()
            
        if column_obj.Formula:
            index.createIndex('PlominoViewColumn_'+self.getViewName()+'_'+column_name, refresh=refresh)
        else:
            fieldpath = column_obj.SelectedField.split('/')
            form = self.getParentDatabase().getForm(fieldpath[0])
            if form:
                field = form.getFormField(fieldpath[1])
                if field:
                    field.setToBeIndexed(True)
                    #field.at_post_edit_script()
                    index.createFieldIndex(field.id, field.getFieldType(), refresh=refresh)
                else:
                    column_obj.setFormula("'Non-existing field'")
                    index.createIndex('PlominoViewColumn_'+self.getViewName()+'_'+column_name, refresh=refresh)
            else:
                column_obj.setFormula("'Non-existing form'")
                index.createIndex('PlominoViewColumn_'+self.getViewName()+'_'+column_name, refresh=refresh)

    security.declarePublic('getCategorizedColumnValues')
    def getCategorizedColumnValues(self,column_name):
        """return existing values for the given key and add the empty value
        """
        brains = self.getAllDocuments(getObject=False)
        allvalues = [getattr(b, self.getIndexKey(column_name)) for b in brains]
        categories = {}
        for itemvalue in allvalues:
            if type(itemvalue) == list:
                for v in itemvalue:
                    if not(v in categories):
                        categories[v] = 1
                    else:
                        categories[v] += 1
            else:
                if itemvalue is not None:
                    if not(itemvalue in categories):
                        categories[itemvalue] = 1
                    else:
                        categories[itemvalue] += 1
        uniquevalues = categories.keys()
        uniquevalues.sort()
        return [(v, categories[v]) for v in uniquevalues]


    security.declarePublic('getCategoryViewEntries')
    def getCategoryViewEntries(self,category_column_name,category_value):
        """get category view entry
        """
        index = self.getParentDatabase().getIndex()
        sortindex = self.getSortColumn()
        if sortindex=='':
            sortindex=None
        else:
            sortindex=self.getIndexKey(sortindex)

        return index.dbsearch(
            {
                'PlominoViewFormula_'+self.getViewName() : True,
                self.getIndexKey(category_column_name) : category_value
            },
            sortindex,
            self.getReverseSorting())

    security.declarePublic('getColumnSums')
    def getColumnSums(self):
        """return the sum of non null values for each column
        marked as summable
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
    def exportCSV(self, REQUEST=None, displayColumnsTitle='False', separator="\t", brain_docs = None, quotechar='"', quoting=csv.QUOTE_NONNUMERIC):
        """export columns values as CSV
        IMPORTANT : brain_docs are supposed to be ZCatalog brains
        """
        if type(quoting) is str:
            #convert to int when passed via querystring
            try:
                quoting = int(quoting)
            except:
                logging.exception('Bad quoting: %s'%quoting, exc_info=True)
                quoting=csv.QUOTE_NONNUMERIC

        if brain_docs is None:
            brain_docs = self.getAllDocuments(getObject=False)

        columns = [c.id for c in self.getColumns()]

        stream = cStringIO.StringIO()
        writer = csv.writer(stream, delimiter=separator, quotechar=quotechar, quoting=quoting)

        # add column titles
        if displayColumnsTitle=='True' :
            titles = [c.title for c in self.getColumns()]
            writer.writerow(titles)

        rows = self.makeArray(brain_docs, columns)
        writer.writerows(rows)

        if REQUEST:
            REQUEST.RESPONSE.setHeader('content-type', 'text/csv; charset=utf-8')
            REQUEST.RESPONSE.setHeader("Content-Disposition", "attachment; filename="+self.id+".csv")
        return stream.getvalue()

    security.declareProtected(READ_PERMISSION, 'exportXLS')
    def exportXLS(self, REQUEST, displayColumnsTitle='False', brain_docs = None):
        """ Export column values to an HTML table, and set content-type to
        launch Excel.
        IMPORTANT: brain_docs are supposed to be ZCatalog brains
        """
        if brain_docs is None:
            brain_docs = self.getAllDocuments(getObject=False)

        columns = [c.id for c in self.getColumns()]

        rows = self.makeArray(brain_docs, columns)

        # add column titles
        if displayColumnsTitle == 'True':
            titles = [c.title.encode('utf-8') for c in self.getColumns()]
            rows[0:0] = titles

        html = """<html><head>
    <meta http-equiv="Content-Type"
          content="text/html;charset=utf-8" />
<body><table>"""
        for row in rows:
            html = html + "<tr>" + ''.join(["<td>%s</td>" % v for v in row]) + "</tr>\n"

        html = html + "</table>\n</body></html>"
        REQUEST.RESPONSE.setHeader('content-type', 'application/vnd.ms-excel; charset=utf-8')
        REQUEST.RESPONSE.setHeader("Content-Disposition", "inline; filename="+self.id+".xls")
        return html


    security.declarePublic('getPosition')
    def getPosition(self):
        """Return the view position in the database
        """
        try :
            return self.Position
        except Exception :
            return None

    security.declarePublic('getDocumentsByKey')
    def getDocumentsByKey(self, key, getObject=True):
        """Get documents which sorted column value match the given key
        """
        index = self.getParentDatabase().getIndex()
        sortindex = self.getSortColumn()
        if sortindex=='':
            return []
        else:
            sortindex=self.getIndexKey(sortindex)
            results=index.dbsearch({'PlominoViewFormula_'+self.getViewName() : True,
                                    sortindex : key
                                    },
                                   sortindex, self.getReverseSorting())
        if getObject:
            return [d.getObject() for d in results]
        else:
            return results

    security.declarePublic('tojson')
    def tojson(self):
        """Returns a JSON representation of view data 
        """
        data = []
        categorized = self.getCategorized()
        
        columnids = [col.id for col in self.getColumns() if not getattr(col, 'HiddenColumn', False)]
        for b in self.getAllDocuments(getObject=False):
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
        return json.dumps({ 'aaData': data })

    security.declarePublic('getIndexKey')
    def getIndexKey(self, columnName):
        """Returns an index key depending of which one exists.
        It can be a computed index (PlominoViewColumn_) or a link to a column. 
        """
        key = 'PlominoViewColumn_%s_%s' % (self.getViewName(), columnName)
        if key not in self.getParentDatabase().plomino_index.Indexes:
            fieldPath = self.getColumn(columnName).SelectedField.split('/')
            if len(fieldPath) > 1:
                key = fieldPath[1]
            else:
                key = ''
        return key


registerType(PlominoView, PROJECTNAME)
# end of class PlominoView




from __future__ import absolute_import #Needed for caseinsensitive file systems. Due to accesscontrol.py
from collections import OrderedDict
from dircache import listdir
from AccessControl import ClassSecurityInfo
from AccessControl.requestmethod import postonly
from AccessControl.SecurityManagement import newSecurityManager
import base64
from os.path import isfile

from ZODB.utils import u64
from plone.behavior.interfaces import IBehaviorAssignable
from z3c.form.interfaces import IDataManager
from zc.twist import Failure
from zope.component import getMultiAdapter

from Products.CMFPlomino.contents.agent import IPlominoAgent
from Products.CMFPlomino.contents.field import IPlominoField
from Products.CMFPlomino.contents.form import IPlominoForm
from Products.CMFPlomino.events import afterFieldModified
from zope.globalrequest import getRequest
import codecs
from cStringIO import StringIO
from DateTime import DateTime
import glob
import json
import re
import logging
from OFS.Folder import Folder
from OFS.Image import manage_addImage
from OFS.ObjectManager import ObjectManager
import os
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
from plone.protect.interfaces import IDisableCSRFProtection
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from Products.PythonScripts.PythonScript import (
    PythonScript,
    manage_addPythonScript,
)
import sys
import traceback
import transaction
from webdav.Lockable import wl_isLocked
from zipfile import ZipFile, ZIP_DEFLATED
from zope import component
from zope.interface import alsoProvides
from zope.lifecycleevent import modified
from zope.schema import getFieldsInOrder
from ZPublisher.HTTPRequest import FileUpload
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse

from Products.CMFPlomino.config import (
    DESIGN_PERMISSION,
    MSG_SEPARATOR,
    TIMEZONE,
)
from Products.CMFPlomino import plomino_profiler, get_utils, get_resource_directory
from Products.CMFPlomino.config import SCRIPT_ID_DELIMITER
from Products.CMFPlomino import contents
from Products.CMFPlomino.exceptions import PlominoDesignException, PlominoScriptException
from Products.CMFPlomino.HttpUtils import authenticateAndLoadURL, authenticateAndPostToURL
from Products.CMFPlomino.index.index import PlominoIndex
from Products.CMFPlomino.interfaces import IPlominoDocument
from Products.CMFPlomino.migration import migrate
from Products.CMFPlomino.utils import (
    _expandIncludes,
    asUnicode,
    DateToString,
)
from collections import defaultdict
try:
    from plone.app.async.interfaces import IAsyncService
except ImportError:
    IAsyncService = None
import persistent

logger = logging.getLogger('Plomino')

STR_FORMULA = """plominoContext = context
plominoDocument = context
script_id = '%(script_id)s'
%(import_list)s

%(formula)s
"""

# example script_id
# field_-_form_test_email_basic_-_fullname_-_formula
# hidewhen_-_form_test_email_basic_-_hidewhen_good_-_formula
# action_-_form_test_email_basic_-_action_redirect_-_script
# form_-_form_test_email_basic_-_ondisplay
# column_-_allfrmtest_-_ffullname_-_formula
# view_-_alltestformonsave_-_selection
# action_-_admin_list_-_download_-_hidewhen'
# action buttons could happen in both form or view
ALL_SCRIPT_TYPES = ['action']
# If it begins with script, the script is in resource folder
# If it begins with agent, it is agent script
IGNORE_SCRIPT_TYPES = ['script', 'agent']
FORM_SCRIPT_TYPES = ['field', 'hidewhen', 'form']
VIEW_SCRIPT_TYPES = ['column', 'view']

HTML_PROPERTY = "form_layout"

class Bundle:

    def __init__(self):
        self.contentList = []

    def __init__(self, zip_file = None, folder = None):
        self.contentList = []
        self.zip_file = zip_file
        self.folder = folder
        if zip_file:
            for file_path in zip_file.namelist():
                dir, fname = os.path.split(file_path)
                elementids = fname.split('.')
                self.contentList.append(( '.'.join(elementids[:-1]), elementids[-1],  None, file_path))
        if folder:
            for file_path in [os.path.join(folder, f) for f in listdir(folder)]:
                if not isfile(file_path):
                    continue
                dir, fname = os.path.split(file_path)
                if not '.' in fname:
                    continue
                elementids = fname.split('.')
                self.contentList.append(( '.'.join(elementids[:-1]), elementids[-1], None, file_path))

    def contents(self, content_type=None):
        for obj_id, obj_type,  content, file_path in self.contentList:
            if content_type and content_type != obj_type:
                continue
            if content:
                yield (obj_id, obj_type, content)
            if self.folder:
                fileobj = codecs.open(file_path, 'r', 'utf-8')
                yield (obj_id, obj_type, fileobj.read())
            if self.zip_file:
                yield (obj_id, obj_type, self.zip_file.open(file_path).read())

    def addContent(self, obj_id, obj_type, content, file_path=None):
        self.contentList.append((obj_id, obj_type, content, file_path))



def makePythonScript(code, context=None):
    ps = PythonScript('ps')  # TODO: should it VerifiedPythonScript?
    #ps.ZBindings_edit(dict(context=context))
    ps.write(code)
    ps._makeFunction()
    if ps.errors:
        raise SyntaxError, ps.errors[0]
    if context is not None:
        return ps.__of__(context)
    return ps


def asyncExecute(executable, *args, **kwargs):
    __async_script__ = kwargs.pop('__async_script__', None)
    __document_id__ = kwargs.pop('__document_id__', None)
    original_request = kwargs.pop('original_request', None)
    if IPlominoAgent.providedBy(executable):
        try:
            return executable.runAgent(*args, **kwargs)
        except PlominoScriptException, e:
            msg = str(e)
            logger.error("Formula error: %s", msg)
            # PlominoScriptException have context object which screws up async as its from another connection.
            raise Exception(msg)
    elif IPlominoForm.providedBy(executable):
        form = executable
        # for forms we run the ondisplay
        db = form.getParentDatabase()
        if __document_id__ is not None:
            context = db.getDocument(__document_id__)
        else:
            context = form
        try:
            response = db.runFormulaScript(
                SCRIPT_ID_DELIMITER.join([
                    'form', form.id, 'ondisplay']),
                context,
                form.onDisplay)
        except PlominoScriptException, e:
            msg = str(e)
            logger.error(msg)
            # PlominoScriptException have context object which screws up async as its from another connection.
            raise Exception(msg)
        # If the onDisplay event returned something, return it
        # We could do extra handling of the response here if needed
        return response
    elif IPlominoField.providedBy(executable):
        field = executable
        form = field.aq_parent
        db = form.getParentDatabase()
        if __document_id__ is not None:
            context = db.getDocument(__document_id__)
        else:
            context = form

        try:
            return form.computeFieldValue(field.id, context, report=False)
        except PlominoScriptException, e:
            msg = str(e)
            logger.error(msg)
            # PlominoScriptException have context object which screws up async as its from another connection.
            raise Exception(msg)

    elif __async_script__ is not None:
        # In this case we will run it as a pythonscript
        ps = makePythonScript(__async_script__, executable)
        return ps(*args, **kwargs)

    else:
        # assume its a callable
        return executable(*args, **kwargs)


class DesignManager:

    security = ClassSecurityInfo()

    security.declareProtected(DESIGN_PERMISSION, 'doRefreshDB')

    @postonly
    def doRefreshDB(self, REQUEST):
        """ Launch refreshDB
        """
        report = self.refreshDB()

        self.writeMessageOnPage(MSG_SEPARATOR.join(report), REQUEST, False)
        REQUEST.RESPONSE.redirect(self.absolute_url() + "/DatabaseDesign")

    security.declareProtected(DESIGN_PERMISSION, 'refreshDB')

    def refreshDB(self):
        """ All actions to take when refreshing a DB (after import for
        instance).
        """
        logger.info('Refreshing database ' + self.id)
        report = []

        self.setStatus("Refreshing design")
        # migrate to current version
        messages = migrate(self)
        for msg in messages:
            report.append(msg)
            logger.info(msg)

        # check folders
        if not hasattr(self, 'resources'):
            resources = Folder('resources')
            resources.title = 'resources'
            self._setObject('resources', resources)
        msg = 'Resources folder OK'
        report.append(msg)
        logger.info(msg)
        if not hasattr(self, 'scripts'):
            scripts = Folder('scripts')
            scripts.title = 'scripts'
            self._setObject('scripts', scripts)
        self.cleanFormulaScripts()
        msg = 'Scripts folder OK and clean'
        report.append(msg)
        logger.info(msg)

        # clean portal_catalog
        portal_catalog = self.portal_catalog
        catalog_entries = portal_catalog.search({
            'portal_type': ['PlominoDocument'],
            'path': '/'.join(self.getPhysicalPath())
        })
        for d in catalog_entries:
            portal_catalog.uncatalog_object(d.getPath())
        msg = 'Portal catalog clean'
        report.append(msg)
        logger.info(msg)

        # create new blank index (without fulltext)
        index = PlominoIndex(FULLTEXT=False).__of__(self)
        index.no_refresh = True
        msg = 'New index created'
        report.append(msg)
        logger.info(msg)

        # declare all indexed fields
        for f_obj in self.getForms():
            for f in f_obj.getFormFields():
                if f.to_be_indexed:
                    index.createFieldIndex(
                        f.id,
                        f.field_type,
                        indextype=f.index_type,
                        fieldmode=f.field_mode)
        logger.info('Field indexing initialized')

        # declare all the view formulas and columns index entries

        for v_obj in self.getViews():
            index.createSelectionIndex(
                'PlominoViewFormula_' + v_obj.id)
            for c in v_obj.getColumns():
                v_obj.declareColumn(c.id, c, index=index, refresh=False)
        # add fulltext if needed
        if self.fulltextIndex:
            index.createFieldIndex('SearchableText', 'RICHTEXT')
        logger.info('Views indexing initialized')

        # re-index documents
        start_time = DateTime().toZone(TIMEZONE)
        msg = self.reindexDocuments(index)
        report.append(msg)

        # Re-indexed documents that have changed since indexing started
        msg = self.reindexDocuments(index, changed_since=start_time)
        report.append(msg)
        index.no_refresh = False

        # destroy the old index and rename the new one
        self.manage_delObjects("plomino_index")
        self._setObject('plomino_index', index.aq_base)
        msg = 'Old index removed and replaced'
        report.append(msg)
        logger.info(msg)

        # refresh portal_catalog
        if self.indexInPortal:
            self.refreshPortalCatalog()

        # update Plone workflow state and role permissions
        self.refreshWorkflowState()
        self.refreshPlominoRolesPermissions()

        self.setStatus("Ready")
        return report

    security.declareProtected(DESIGN_PERMISSION, 'reindexDocuments')

    def reindexDocuments(self, plomino_index, items_only=False,
            views_only=False, update_metadata=1, changed_since=None):
        """ Reindex all documents in a given index.
        """
        documents = self.getAllDocuments()
        if changed_since:
            documents = [doc for doc in documents
                    if doc.plomino_modification_time > changed_since]
            total_docs = len(documents)
            logger.info('Re-indexing %d changed document(s) since %s' % (
                total_docs, DateToString(changed_since, db=self)))
        else:
            total_docs = len(self.plomino_documents)
            logger.info('Existing documents: ' + str(total_docs))
        total = 0
        counter = 0
        errors = 0
        label = "documents"
        if items_only:
            label = "items"
        if views_only:
            label = "views"
        self.setStatus("Re-indexing %s (0%%)" % label)

        indexes = plomino_index.indexes()
        view_indexes = [idx for idx in indexes
                if idx.startswith("PlominoView")]
        if 'SearchableText' in indexes:
            view_indexes.append('SearchableText')
        for d in documents:
            try:
                idxs = []
                if items_only:
                    items = d.getItems() + ['id', 'getPlominoReaders']
                    idxs = [idx for idx in indexes if idx in items]
                if views_only:
                    idx = view_indexes
                txn = transaction.get()
                plomino_index.indexDocument(
                    d,
                    idxs=idxs,
                    update_metadata=update_metadata)
                txn.commit()
                total = total + 1
            except Exception, e:
                errors = errors + 1
                logger.info("Ouch! \n%s\n%s" % (e, repr(d)))
            counter = counter + 1
            if counter == 100:
                self.setStatus("Re-indexing %s (%d%%)" % (
                    label,
                    int(100 * (total + errors) / total_docs)))
                counter = 0
                logger.info("Re-indexing %s: "
                    "%d indexed successfully, %d errors(s)..." % (
                        label, total, errors))
        if changed_since:
            msg = ("Intermediary changes: "
                "%d modified documents re-indexed successfully, "
                "%d errors(s)" % (total, errors))
        else:
            msg = ("Re-indexing %s: "
                "%d documents indexed successfully, "
                "%d errors(s)" % (label, total, errors))
        logger.info(msg)
        return msg

    security.declareProtected(DESIGN_PERMISSION, 'recomputeAllDocuments')

    @postonly
    def recomputeAllDocuments(self, REQUEST=None):
        """
        """
        logger.info('Re-compute documents in ' + self.id)
        documents = self.getAllDocuments()
        total_docs = len(self.plomino_documents)
        logger.info('Existing documents: ' + str(total_docs))
        total_docs = len(documents)
        total = 0
        counter = 0
        errors = 0
        self.setStatus("Re-compute documents")
        for d in documents:
            try:
                txn = transaction.get()
                d.save(asAuthor=False, onSaveEvent=False)
                txn.commit()
                total = total + 1
            except Exception, e:
                errors = errors + 1
                logger.info("Ouch! \n%s\n%s" % (e, repr(d)))
            counter = counter + 1
            if counter == 10:
                self.setStatus(
                    "Re-compute documents (%d%%)" %
                    (int(100 * (total + errors) / total_docs)))
                counter = 0
                logger.info("Re-compute documents: "
                    "%d computed successfully, "
                    "%d errors(s) ..." % (total, errors))
        msg = ("Re-compute documents: "
            "%d documents computed successfully, "
            "%d errors(s)" % (total, errors))
        logger.info(msg)
        self.setStatus("Ready")
        if REQUEST:
            self.writeMessageOnPage(msg, REQUEST, False)
            REQUEST.RESPONSE.redirect(self.absolute_url() + "/DatabaseDesign")

    security.declareProtected(DESIGN_PERMISSION, 'refreshMacros')

    @postonly
    def refreshMacros(self, REQUEST=None):
        macros=0
        forms = self.getForms()
        views = self.getViews()
        for form in forms + views:
            items = form.objectValues()

            #TODO: more things than fields have macros on them
            #TODO: modified events might have other consequences?
            for item in list(items) + [form]:
                helpers = getattr(item, 'helpers', None) or []#TODO should use a DM

                changed = False
                for helper in helpers:
                    for subhelper in helper:
                        #TODO: is subhelper['Form'].modified > item.modified?
                        changed = True

                        #if self.getForm(subhelper['Form']).modified > :
                        macros += 1
                if changed:
                    logger.debug('updated macro template on field: %s' % item.id)
                    modified(item)

        msg = '%i macros updated' % macros
        if REQUEST:
            self.writeMessageOnPage(msg, REQUEST, False)
            REQUEST.RESPONSE.redirect(self.absolute_url() + "/DatabaseDesign")

    security.declareProtected(DESIGN_PERMISSION, 'refreshPortalCatalog')

    @postonly
    def refreshPortalCatalog(self, REQUEST=None):
        """
        """
        msg = ""
        portal_catalog = self.portal_catalog
        if self.indexInPortal:
            logger.info(
                'Refresh documents from %s in portal catalog' % self.id)
            documents = self.getAllDocuments()
            total_docs = len(self.plomino_documents)
            logger.info('Existing documents: ' + str(total_docs))
            for d in documents:
                portal_catalog.catalog_object(
                    d,
                    "/".join(self.getPhysicalPath() + (d.id,)))
            msg = '%d documents re-cataloged' % total_docs
        else:
            logger.info(
                'Database %s does not allow portal catalog indexing.' %
                self.id)
            catalog_entries = portal_catalog.search({
                'portal_type': ['PlominoDocument'],
                'path': '/'.join(self.getPhysicalPath())
            })
            if catalog_entries:
                for d in catalog_entries:
                    portal_catalog.uncatalog_object(d.getPath())
                logger.info(
                    'Related portal catalog entries have been removed.')
            msg = 'Database is not cataloged'

        logger.info(msg)
        if REQUEST:
            self.writeMessageOnPage(msg, REQUEST, False)
            REQUEST.RESPONSE.redirect(self.absolute_url() + "/DatabaseDesign")

    security.declareProtected(DESIGN_PERMISSION, 'refreshWorkflowState')

    def refreshWorkflowState(self):
        """ Prevent Plone security inconsistencies when refreshing design
        """
        workflow_tool = api.portal.get().portal_workflow
        wfs = workflow_tool.getWorkflowsFor(self)
        for wf in wfs:
            if not isinstance(wf, DCWorkflowDefinition):
                continue
            wf.updateRoleMappingsFor(self)
        logger.info('Plone workflow update')

    security.declareProtected(DESIGN_PERMISSION, 'exportDesign')

    def exportDesign(self, targettype='file', targetfolder='', dbsettings=True,
            designelements=None, REQUEST=None, **kw):
        """ Export design elements to JSON.
        The targettype can be file, zipfile, server, or folder.
        """
        if REQUEST:
            entire = REQUEST.get('entire')
            targettype = REQUEST.get('targettype')
            targetfolder = REQUEST.get('targetfolder')
            dbsettings = REQUEST.get('dbsettings')

        if dbsettings == "Yes":
            dbsettings = True
        else:
            dbsettings = False

        if designelements:
            if entire == "Yes":
                designelements = None
            else:
                designelements = REQUEST.get('designelements')
                if designelements:
                    if type(designelements) == str:
                        designelements = [designelements]

        if targettype in ["server", "file"]:
            jsonstring = self.exportDesignAsJSON(
                elementids=designelements,
                dbsettings=dbsettings)

            if targettype == "server":
                if REQUEST:
                    targetURL = REQUEST.get('targetURL')
                    username = REQUEST.get('username')
                    password = REQUEST.get('password')
                authenticateAndPostToURL(
                    targetURL + "/importDesignFromJSON",
                    username,
                    password,
                    'exportDesignAsJSON.json',
                    jsonstring)
                REQUEST.RESPONSE.redirect(
                    self.absolute_url() + "/DatabaseDesign")
            elif targettype == "file":
                if REQUEST:
                    REQUEST.RESPONSE.setHeader(
                        'content-type', 'application/json')
                    REQUEST.RESPONSE.setHeader(
                        "Content-Disposition",
                        "attachment; filename=%s.json" % self.id)
                return jsonstring
        elif targettype == "zipfile":
            zip_string = self.exportDesignAsZip(
                designelements=designelements,
                dbsettings=dbsettings)

            if REQUEST:
                REQUEST.RESPONSE.setHeader('Content-Type', 'application/zip')
                REQUEST.RESPONSE.setHeader(
                    "Content-Disposition",
                    "attachment; filename=%s.zip" % self.id)
                REQUEST.RESPONSE.setHeader(
                    'Content-Length', len(zip_string.getvalue()))
            return zip_string.getvalue()
        elif targettype == "folder":
            if not designelements:
                designelements = (
                    [o.id for o in self.getDesignElements(sortbyid=False)] +
                    ["resources/" + id for id in self.resources.objectIds()]
                )
            exportpath = os.path.join(targetfolder, self.id)
            resources_exportpath = os.path.join(exportpath, 'resources')
            if os.path.isdir(exportpath):
                # remove previous export
                for f in glob.glob(os.path.join(exportpath, "*.json")):
                    os.remove(f)
                if os.path.isdir(resources_exportpath):
                    for f in glob.glob(
                            os.path.join(resources_exportpath, "*.json")):
                        os.remove(f)
            else:
                os.makedirs(exportpath)
            if [id for id in designelements if id.startswith('resources/')]:
                if not os.path.isdir(resources_exportpath):
                    os.makedirs(resources_exportpath)

            for id in designelements:
                if id.startswith('resources/'):
                    path = os.path.join(
                        resources_exportpath,
                        id.split('/')[-1] + '.json')
                    jsonstring = self.exportDesignAsJSON(
                        elementids=[id],
                        dbsettings=False,
                        bundle=True)
                    self.saveFile(path, jsonstring)
                    path = os.path.join(
                        resources_exportpath,
                        id.split('/')[-1] + '.py')
                    filestring = self.exportResourceAsPy(
                        self.resources[id.split('/')[-1]])
                    self.saveFile(path, filestring)

                else:
                    bundle = self.exportDesignAsBundle(
                        elementid=id)
                    for obj_id, obj_type, content in bundle.contents():
                        if content:
                            path = os.path.join(
                                exportpath,
                                obj_id + "." + obj_type)
                            self.saveFile(path, content)
            if dbsettings:
                path = os.path.join(exportpath, ('dbsettings.json'))
                jsonstring = self.exportDesignAsJSON(
                    elementids=[],
                    dbsettings=True)
                self.saveFile(path, jsonstring.decode('utf-8'))

    @staticmethod
    def saveFile(path, content):
        fileobj = codecs.open(path, "w", "utf-8")
        try:
            logger.info('saveFile> write with no decode')
            fileobj.write(content)
        except UnicodeDecodeError:
            fileobj.write(content.decode('utf-8'))
            logger.info('saveFile> write.decode("utf-8"): %s' % path)
        fileobj.close()

    security.declareProtected(DESIGN_PERMISSION, 'importDesign')

    def importDesign(self, REQUEST=None):
        """ Import design elements in current database
        """
        submit_import = REQUEST.get('submit_import')
        entire = REQUEST.get('entire')
        sourcetype = REQUEST.get('sourcetype')
        sourceURL = REQUEST.get('sourceURL')
        username = REQUEST.get('username')
        password = REQUEST.get('password')
        replace_design = REQUEST.get('replace_design')
        replace = replace_design == "Yes"
        if submit_import:
            if sourcetype == "server":
                export_url = sourceURL + "/exportDesignAsJSON"
                if not entire == "Yes":
                    designelements = REQUEST.get('designelements')
                    if designelements:
                        if type(designelements) == str:
                            designelements = [designelements]
                        export_url = "%s?elementids=%s" % (
                            export_url,
                            "@".join(designelements)
                        )
                jsonstring = authenticateAndLoadURL(
                    export_url, username, password).read()
                self.importDesignFromJSON(jsonstring, replace=replace)

            elif sourcetype == "folder":
                path = REQUEST.get('sourcefolder')
                self.importDesignFromJSON(from_folder=path, replace=replace)
            else:
                fileToImport = REQUEST.get('sourceFile', None)
                if not fileToImport:
                    raise PlominoDesignException('file required')
                if not isinstance(fileToImport, FileUpload):
                    raise PlominoDesignException('unrecognized file uploaded')
                if fileToImport.headers['content-type'] in [
                    'application/zip',
                    'application/x-zip-compressed'
                ]:
                    zip_file = ZipFile(fileToImport)
                    self.importDesignFromJSON(from_zip=zip_file, replace=replace)
                else:
                    jsonstring = fileToImport.read()
                    self.importDesignFromJSON(jsonstring, replace=replace)

            no_refresh_documents = REQUEST.get('no_refresh_documents', 'No')
            if no_refresh_documents == 'No':
                self.refreshDB()
            else:
                self.refreshWorkflowState()
            REQUEST.RESPONSE.redirect(self.absolute_url() + "/DatabaseDesign")
        else:
            REQUEST.RESPONSE.redirect(
                "%s/DatabaseDesign"
                "?username=%s"
                "&password=%s"
                "&sourceURL=%s" % (
                    self.absolute_url(),
                    username,
                    password,
                    sourceURL)
            )

    security.declareProtected(DESIGN_PERMISSION, 'getViewsList')

    def getViewsList(self):
        """ Return the database views ids in a string
        """
        views = self.getViews()
        ids = [v.id for v in views]
        ids.sort()
        return '/'.join(ids)

    security.declareProtected(DESIGN_PERMISSION, 'getFormsList')

    def getFormsList(self):
        """ Return the database forms ids in a string
        """
        forms = self.getForms()
        ids = [f.id for f in forms]
        ids.sort()
        return '/'.join(ids)

    security.declareProtected(DESIGN_PERMISSION, 'getAgentsList')

    def getAgentsList(self):
        """ Return the database agents ids in a string
        """
        agents = self.getAgents()
        ids = [a.id for a in agents]
        ids.sort()
        return '/'.join(ids)

    security.declareProtected(DESIGN_PERMISSION, 'getResourcesList')

    def getResourcesList(self):
        """ Return the database resources objects ids in a string
        """
        # Un-lazify, resources is a BTree
        ids = [i for i in self.resources.objectIds()]
        ids.sort()
        return '/'.join(ids)

    security.declareProtected(DESIGN_PERMISSION, 'getRemoteViews')

    def getRemoteViews(self, sourceURL, username, password):
        """ Get views ids list from remote database
        """
        views = authenticateAndLoadURL(
            sourceURL + "/getViewsList",
            username,
            password).read()
        ids = views.split('/')
        return ids

    security.declareProtected(DESIGN_PERMISSION, 'getRemoteForms')

    def getRemoteForms(self, sourceURL, username, password):
        """ Get forms ids list from remote database
        """
        forms = authenticateAndLoadURL(
            sourceURL + "/getFormsList",
            username,
            password).read()
        ids = forms.split('/')
        return ids

    security.declareProtected(DESIGN_PERMISSION, 'getRemoteAgents')

    def getRemoteAgents(self, sourceURL, username, password):
        """ Get agents ids list from remote database
        """
        agents = authenticateAndLoadURL(
            sourceURL + "/getAgentsList",
            username,
            password).read()
        ids = agents.split('/')
        return ids

    security.declareProtected(DESIGN_PERMISSION, 'getRemoteResources')

    def getRemoteResources(self, sourceURL, username, password):
        """ Get resources ids list from remote database
        """
        res = authenticateAndLoadURL(
            sourceURL + "/getResourcesList",
            username,
            password).read()
        ids = res.split('/')
        return ['resources/' + i for i in ids]

    security.declarePublic('getFormulaScript')

    def getFormulaScript(self, script_id, formula=None):

        ps = self.scripts._getOb(script_id, None)
        if ps is not None and formula is not None and getattr(ps, '_formula_hash', None) != hash(formula):
            return None
        return ps


    security.declarePublic('cleanFormulaScripts')

    def cleanFormulaScripts(self, script_id_pattern=None):
        to_delete = []
        if not script_id_pattern:
            to_delete = self.scripts.objectIds()
        else:
            for script_id in self.scripts.objectIds():
                if script_id_pattern in script_id:
                    to_delete.append(script_id)
        for id in to_delete:
            del self.scripts[id]

    security.declarePublic('compileFormulaScript')

    def compileFormulaScript(self, script_id, formula, with_args=False):
        # disable CSRF to allow script saving
        if hasattr(self, "REQUEST"):
            alsoProvides(self.REQUEST, IDisableCSRFProtection)

        # Remember the current user
        member = self.getCurrentMember()
        if member.__class__.__name__ == "SpecialUser":
            user = member
        else:
            user = member.getUser()

        # Switch to the db's owner (formula must be compiled with the higher
        # access rights, but their execution will always be perform with the
        # current access rights)
        owner = self.getOwner()
        newSecurityManager(None, owner)

        ps = self.getFormulaScript(script_id)
        if not ps:
            ps = PythonScript(script_id)
            self.scripts._setObject(script_id, ps)
        ps = self.getFormulaScript(script_id)

        ps._formula_hash = hash(formula) #TODO: should be incldes too

        if with_args:
            ps._params = "*args"
        safe_utils = get_utils()
        import_list = []
        for module in safe_utils:
            import_list.append(
                "from %s import %s" % (
                    module,
                    ", ".join(safe_utils[module]))
            )
        import_list = ";".join(import_list)

        formula = _expandIncludes(self, formula)

        if (formula.strip().count('\n') == 0 and
                not formula.startswith('return ')):
            formula = "return " + formula

        str_formula = STR_FORMULA % {
            'script_id': script_id,
            'import_list': import_list,
            'formula': formula
        }
        ps.write(str_formula)
        if self.debugMode:
            logger.info(script_id + " compiled")

        # Switch back to the original user
        newSecurityManager(None, user)

        return ps

    security.declarePublic('runFormulaScript')

    @plomino_profiler('formulas')
    def runFormulaScript(self, script_id, context, formula,
            with_args=False, *args, **kwargs):
        formula_str = formula or ''
        compilation_errors = []
        ps = self.getFormulaScript(script_id, formula)
        if not ps:
            ps = self.compileFormulaScript(
                script_id,
                formula_str,
                with_args)
        if ps and getattr(ps, 'errors', None):
            compilation_errors = ps.errors

        request_context = context
        script_type, obj_id, _ = script_id.split(SCRIPT_ID_DELIMITER, 2)
        add_request_run_as_owner = True
        if script_type in ALL_SCRIPT_TYPES:
            any_obj = self.getForm(obj_id)
            if any_obj:
                request_context = any_obj
            else:
                any_obj = self.getView(obj_id)
                if any_obj:
                    request_context = any_obj
                else:
                    # should not happen
                    raise PlominoScriptException(
                        request_context,
                        Exception(),
                        formula_str,
                        script_id,
                        compilation_errors)
        elif script_type in FORM_SCRIPT_TYPES:
            form_obj = self.getForm(obj_id)
            if form_obj:
                request_context = form_obj
            else:
                # should not happen
                raise PlominoScriptException(
                    request_context,
                    Exception(),
                    formula_str,
                    script_id,
                    compilation_errors)
        elif script_type in VIEW_SCRIPT_TYPES:
            view_obj = self.getView(obj_id)
            if view_obj:
                request_context = view_obj
            else:
                # should not happen
                raise PlominoScriptException(
                    request_context,
                    Exception(),
                    formula_str,
                    script_id,
                    compilation_errors)
        elif script_type in IGNORE_SCRIPT_TYPES:
            # should remain the same as original for script and agent
            # run_as_owner in request should not use in these scripts
            add_request_run_as_owner = False
        else:
            # should not happen
            raise PlominoScriptException(
                request_context,
                Exception(),
                formula_str,
                script_id,
                compilation_errors)

        # set a context manager in the request so formula can raise
        # it's security level if it wants
        # use cache request instead of global request as
        # it causes problems for temp document caching
        # if alter the request itself.
        previous_plomino_run_as_owner = None
        if add_request_run_as_owner:
            cache_plomino_run_as_owner = self.getRequestCache(
                '_plomino_run_as_owner_')
            if cache_plomino_run_as_owner:
                # could be script calling script
                # so need to capture previous script
                previous_plomino_run_as_owner = cache_plomino_run_as_owner
            self.setRequestCache(
                '_plomino_run_as_owner_',
                run_as_owner(request_context))

        result = None
        try:
            contextual_ps = ps.__of__(context)
            if with_args:
                result = contextual_ps(*args, **kwargs)
            else:
                result = contextual_ps()
            if (self.debugMode and
                    hasattr(contextual_ps, 'errors') and
                    contextual_ps.errors):
                logger.info('python errors at %s in %s: %s' % (
                    str(context),
                    script_id,
                    str(contextual_ps.errors)))

        except Exception, e:
            logger.info(
                "Plomino Script Exception: %s, %s" % (
                    formula_str,
                    script_id),
                exc_info=True)
            if self.getRequestCache("ABORT_ON_ERROR"):
                transaction.abort()
            raise PlominoScriptException(
                context,
                e,
                formula_str,
                script_id,
                compilation_errors)
        finally:
            self.setRequestCache(
                '_plomino_run_as_owner_',
                previous_plomino_run_as_owner)
        return result

    security.declarePublic('runAsOwner')

    def runAsOwner(self):
        """ return a context manager for use in formulas which will
        raise the security context to run apis which require greater
        permission.
        """
        return self.getRequestCache('_plomino_run_as_owner_')

    def queue_run(self, executable, doc=None, *args, **kwargs):
        """
        use p.a.async or other async lib to queue executing code.
        Code is text of a pythonscript, or a Form or and Agent
        """
        if IAsyncService is None:
            raise ImportError("plone.app.async is not installed")
        async = component.getUtility(IAsyncService)
        #TODO: limit what extra args we pass in
        #TODO: check callable to make sure it doesn't let us bypass security

        # if there is an extra context check its a document
        if doc is not None:
            if IPlominoDocument.providedBy(doc):
                kwargs['__document_id__'] = doc.id

        if IPlominoAgent.providedBy(executable):
            context = executable
        elif IPlominoForm.providedBy(executable):
            context = executable
            if not hasattr(context, 'onDisplay') or not context.onDisplay:
                raise SyntaxError("Form must have onDisplay formula to queue it")
        elif IPlominoField.providedBy(executable):
            context = executable
            if not hasattr(context, 'formula') or not context.formula:
                raise SyntaxError("Field must have a formula to queue it")
        elif IPlominoDocument.providedBy(executable):
            doc = executable
            kwargs['__document_id__'] = doc.id #ignore any doc that was passsed in
            form = doc.getForm()
            if not hasattr(form, 'onDisplay') or not form.onDisplay:
                raise SyntaxError("Form must have onDisplay formula to queue it")
            context = form
        elif type(executable) == type(""):
            if doc is not None:
                context = doc
            else:
                context = self
            try:
                ps = makePythonScript(executable)
            except SyntaxError:
                # better we raise this before the job is queued
                raise
            kwargs['__async_script__'] = unicode(executable)
        else:
            # TODO: do we allow other things?
            context = executable

        request = dict(getattr(context, 'REQUEST', {}))
        if request:
            for k, v in request.items():
                if type(v) not in [str, unicode]:
                    del request[k]


        job = async.queueJob(asyncExecute, context, original_request=request, *args, **kwargs)
        # we will turn the job into an id so it can be retrieved later
        job_id = u64(job._p_oid)
        return job_id

    def queue_status(self, job_id):
        if not job_id:
            raise ValueError("Invalid job_id")
        if IAsyncService is None:
            raise ImportError("plone.app.async is not installed")
        status, job = self._find_job(job_id)
        if status:
            return status, job.result
        else:
            return None, None

    def _find_job(self, job_id):
        service = component.getUtility(IAsyncService)
        queue = service.getQueues()['']
        def ours(job):
            return u64(job._p_oid) == job_id
                   #and job.args[0].startswith(self.absolute_path())
        for status, job in self._find_jobs():
            if ours(job):
                return job.status, job
        return None, None

    def _find_jobs(self):
        service = component.getUtility(IAsyncService)
        queue = service.getQueues()['']
        for job in queue:
            yield 'queued', job
        for da in queue.dispatchers.values():
            for agent in da.values():
                for job in agent:
                    yield 'active', job
                for job in agent.completed:
                    if isinstance(job.result, Failure):
                        yield 'dead', job
                    else:
                        yield 'completed', job

    def _filter_jobs(self):
        for job_status, job in self._find_jobs():
            if len(job.args) == 0:
                continue
            job_context = job.args[0]
            if type(job_context) == tuple and \
                    job_context[:len(self.portal_path)] == self.portal_path:
                yield job_status, job


    security.declarePrivate('traceRenderingErr')

    def traceRenderingErr(self, e, context):
        """ Trace rendering errors
        """
        if self.debugMode:
            # traceback
            formatted_lines = traceback.format_exc().splitlines()
            msg = "\n".join(formatted_lines[-3:]).strip()
            # code / value
            msg = "%s\nPlomino rendering error with context: %s" % (
                msg,
                '/'.join(context.getPhysicalPath()))
        else:
            msg = None

        if msg:
            logger.error(msg)

    security.declarePublic('callScriptMethod')

    def callScriptMethod(self, scriptname, funcname, *args):
        """ Calls a function named ``funcname`` in a file named
        ``scriptname``, stored in the ``resources`` folder.
        If the called function allows it, you may pass some arguments.
        """
        script_id = SCRIPT_ID_DELIMITER.join(['script', scriptname, funcname])
        try:
            script_code = self.resources._getOb(scriptname).read()
        except:
            logger.warning(
                "callScriptMethod> %s not found in resources" % scriptname)
            script_code = "#ALERT: " + scriptname + " not found in resources"
        formula = script_code + '\n\nreturn ' + funcname + '(*args)'

        return self.runFormulaScript(script_id, self, formula, True, *args)

    security.declarePublic('writeMessageOnPage')

    def writeMessageOnPage(self, infoMsg, REQUEST, error=False):
        """ Adds portal message
        """
        if error:
            msgType = 'error'
        else:
            msgType = 'info'
        infoMsg = infoMsg.split(MSG_SEPARATOR)
        for msg in infoMsg:
            if msg:
                api.portal.show_message(
                    message=msg,
                    request=REQUEST,
                    type=msgType
                )

    security.declarePublic('getRenderingTemplate')

    def getRenderingTemplate(self, templatename, request=None):
        """ Look up a Plomino form or field template from portal skin layers.
        """
        # The portal_skins machinery will look through layers in order
        if hasattr(self.portal_skins, templatename):
            pt = getattr(self.portal_skins, templatename)
            if request:
                pt.REQUEST = request
            else:
                request = getattr(pt, 'REQUEST', None)
                proper_request = (request and
                        pt.REQUEST.__class__.__name__ == 'HTTPRequest')
                if not proper_request:
                    # XXX What *else* could REQUEST be here?
                    # we are not in an actual web context, but we a need a
                    # request object to have the template working
                    response = HTTPResponse(stdout=sys.stdout)
                    env = {'SERVER_NAME': 'fake_server',
                        'SERVER_PORT': '80',
                        'REQUEST_METHOD': 'GET'}
                    pt.REQUEST = HTTPRequest(sys.stdin, env, response)
            # we also need a RESPONSE
            if 'RESPONSE' not in pt.REQUEST:
                pt.REQUEST['RESPONSE'] = HTTPResponse()
            return pt

    security.declareProtected(DESIGN_PERMISSION, 'exportDesignAsZip')

    def exportDesignAsZip(self, designelements=None, dbsettings=True):
        """
        """
        db_id = self.id
        if not designelements:
            designelements = (
                 [id for id in self.objectIds(['Dexterity Container',
                                                'Dexterity Item'])] +
                ["resources/" + id for id in self.resources.objectIds()]
            )
        file_string = StringIO()
        zip_file = ZipFile(file_string, 'w', ZIP_DEFLATED)
        for id in designelements:
            if id.startswith('resources/'):
                filename = os.path.join(
                    db_id,
                    'resources',
                    id.split('/')[-1] + '.json')
                jsonstring = self.exportDesignAsJSON(
                    elementids=[id],
                    dbsettings=False,
                    bundle=True)
                zip_file.writestr(filename, jsonstring)
                filename = os.path.join(
                    db_id,
                    'resources',
                    id.split('/')[-1] + '.py')
                filestring = self.exportResourceAsPy(
                    self.resources[id.split('/')[-1]])
                zip_file.writestr(filename, filestring)
            else:
                bundle = self.exportDesignAsBundle(
                    elementid=id)
                for obj_id, obj_type, content in bundle.contents():
                    if content:
                        filename = os.path.join(db_id, obj_id + "." + obj_type)
                        zip_file.writestr(filename, content)
        if dbsettings:
            filename = os.path.join(db_id, 'dbsettings.json')
            jsonstring = self.exportDesignAsJSON(
                elementids=[],
                dbsettings=True)
            zip_file.writestr(filename, jsonstring)
        zip_file.close()
        return file_string

    security.declareProtected(DESIGN_PERMISSION, 'exportDesignAsJSON')

    def exportDesignAsJSON(
        self, elementids=None, REQUEST=None, dbsettings=True, bundle=False
    ):
        """
        """
        data = OrderedDict()

        if REQUEST:
            str_elementids = REQUEST.get("elementids")
            if str_elementids is not None:
                elementids = str_elementids.split("@")

        if elementids is None:
            elements = (self.getDesignElements(sortbyid=False)
                + [o for o in self.resources.getChildNodes()]
            )
        else:
            elements = []
            for id in elementids:
                if id.startswith('resources/'):
                    e = getattr(self.resources, id.split('/')[1])
                else:
                    e = getattr(self, id)
                elements.append(e)

        # Sort elements by type (to store forms before views), then by id
        #elements.sort(key=lambda elt: elt.getId())
        #elements.sort(key=lambda elt: elt.Type())

        design = OrderedDict()
        # export database settings
        if dbsettings:
            design['dbsettings'] = self.exportElementAsJSON(
                self, isDatabase=True)
        design['resources'] = OrderedDict()

        # export database design elements
        for element in elements:
            if 'Dexterity' in element.meta_type:
                design[element.id] = self.exportElementAsJSON(element)
            else:
                # resources
                resource_id = element.id
                if callable(resource_id):
                    resource_id = resource_id()
                design['resources'][resource_id] = self.exportResourceAsJSON(
                    element, bundle=bundle)

        data['design'] = design

        if REQUEST:
            REQUEST.RESPONSE.setHeader(
                'content-type', "application/json;charset=utf-8")
        # Python JSON lib bug: JSON dump with indent option appending trailing space after comma
        # Temporary fix by applying regex on json string
        json_string =  json.dumps(data, sort_keys=False, indent=4).encode('utf-8')
        return '\n'.join([ re.sub("(\s)*$","",line) for line in json_string.splitlines()])


    def getMethods(self, element):
        """ type comes in the form of ViewAction, FormAction etc
        """
        schema = element.getTypeInfo().lookupSchema()
        assignable = IBehaviorAssignable(element)
        schemas = [schema] + [behaviour.interface for behaviour in assignable.enumerateBehaviors()]
        methods = []
        for schema in schemas:
            widgets = schema.queryTaggedValue(u'plone.autoform.widgets', {})
            for name,field in getFieldsInOrder(schema):
                #field = schema.get(name)
                widget = widgets.get(name, None)
                if widget is None:
                    continue
                # bit of a HACK
                if widget.params.get('klass') == 'plomino-formula':
                    methods.append(name)
        return methods


    security.declareProtected(DESIGN_PERMISSION, 'exportDesignAsBundle')

    def exportDesignAsBundle(
            self, elementid
    ):
        """
        """
        bundle = Bundle()
        rootElement = getattr(self, elementid)
        html = getattr(rootElement, HTML_PROPERTY, None)
        if html:
            bundle.addContent(elementid , "html", html)
        bundle.addContent(elementid , "py", self.extractScriptFromElement(rootElement))
        childElementslist = rootElement.objectIds()
        if childElementslist:
            for id in childElementslist:
                childElement = getattr(rootElement, id)
                bundle.addContent(elementid + "." + id ,"py", self.extractScriptFromElement(childElement))
        # export database design elements
        data = OrderedDict()
        design = OrderedDict()
        design['resources'] = OrderedDict()
        design[rootElement.id] = self.exportElementAsJSON(rootElement, isDatabase = False, stripFlag=True)
        data['design'] = design

        # Python JSON lib bug: JSON dump with indent option appending trailing space after comma
        # Temporary fix by applying regex on json string
        json_string = json.dumps(data, sort_keys=False, indent=4).encode('utf-8')
        bundle.addContent(elementid ,"json",  '\n'.join([re.sub("(\s)*$", "", line) for line in json_string.splitlines()]))
        return bundle



    def extractScriptFromElement(self,element):
        codes = []
        for method in self.getMethods(element):
            script = getattr(element, method, None)
            if script:
                code = ["## START "+method+" {"] +\
                    script.splitlines() +\
                    ["## END "+method+" }"]
                codes.append('\n'.join(code))
        return '\n'.join(codes)


    security.declareProtected(DESIGN_PERMISSION, 'exportElementAsJSON')

    def exportElementAsJSON(self, obj, isDatabase=False, stripFlag = False):
        """
        """
        data = OrderedDict({})
        if not isDatabase:
            data['id'] = obj.id
            data['type'] = obj.portal_type
            data['title'] = obj.title
        schema = component.getUtility(
            IDexterityFTI, name=obj.portal_type).lookupSchema()

        params = OrderedDict({})
        def get_data(obj, schema):
            fields = getFieldsInOrder(schema)
            striplist = []
            if stripFlag:
                striplist.append(HTML_PROPERTY)
                striplist.extend(self.getMethods(obj))
            for (id, attr) in fields:
                if id == 'id' or id in striplist:
                    # 'id' is not needed as it is the same as obj.id
                    # it will cause 'CatalogError: The object unique id must
                    #  be a string. ' error when import this exported file.
                    continue
                #params[id] = getattr(obj, id, None)
                dm = getMultiAdapter((obj, attr), IDataManager)
                #TODO: needs to be the same as import due to form_layout
                #params[id] = dm.get()
                params[id] = getattr(obj, id, None)
        get_data(obj, schema)
        for behaviour in IBehaviorAssignable(obj).enumerateBehaviors():
            get_data(obj,behaviour.interface)

        data['params'] = params

        if not isDatabase:
            elementslist = obj.objectIds()
            if elementslist:
                elements = OrderedDict({})
                for id in elementslist:
                    elements[id] = self.exportElementAsJSON(getattr(obj, id), isDatabase, stripFlag)
                data['elements'] = elements

        if isDatabase:
            data['acl'] = {
                'AnomynousAccessRight': obj.AnomynousAccessRight,
                'AuthenticatedAccessRight': obj.AuthenticatedAccessRight,
                'UserRoles': obj.UserRoles,
                'SpecificRights': obj.getSpecificRights(),
            }
            data['version'] = obj.plomino_version

        return data



    security.declareProtected(DESIGN_PERMISSION, 'exportResourceAsJSON')

    def exportResourceAsJSON(self, obj, bundle=False):
        """
        """
        id = obj.id
        if callable(id):
            id = id()
        data = OrderedDict({
            'id': id,
            'type': obj.meta_type,
            'title': obj.title,
        })
        if bundle is True:
            return data
        if hasattr(obj, 'read'):
            data['data'] = obj.read()
        elif isinstance(obj, Folder):
            for name, sub_obj in obj.objectItems():
                data[name] = self.exportResourceAsJSON(sub_obj)
        else:
            data['contenttype'] = obj.getContentType()
            stream = obj.data
            if not hasattr(stream, "encode"):
                stream = stream.data
            data['data'] = stream.encode('base64')

        return data

    security.declareProtected(DESIGN_PERMISSION, 'exportResourceAsPy')

    def exportResourceAsPy(self, obj):
        if hasattr(obj, 'read'):
            data = obj.read()
        elif isinstance(obj, Folder):
            for name, sub_obj in obj.objectItems():
                data = self.exportResourceAsPy(sub_obj)
        else:
            stream = obj.data
            if not hasattr(stream, "encode"):
                stream = stream.data
            data = stream.encode('base64')

        return data

    security.declareProtected(DESIGN_PERMISSION, 'importDesignFromJSON')

    def importDesignFromJSON(self, jsonstring=None, REQUEST=None,
            from_folder=None, from_zip=None, replace=False):
        """
        """
        logger.info("Start design import")
        self.setStatus("Importing design")
        self.getIndex().no_refresh = True
        txn = transaction.get()
        json_strings = []
        count = 0
        total = 0
        bundle = None
        if from_folder is not None or from_zip is not None:
            if from_folder is not None:
                if not os.path.isdir(from_folder):
                    raise PlominoDesignException('%s does not exist' % from_folder)
                bundle = Bundle(folder=from_folder)
            elif from_zip is not None:
                bundle = Bundle(zip_file=from_zip)
            else:
                raise PlominoDesignException('No file to import')

            total_elements = 0
            for obj_id, obj_type, jsonstring in bundle.contents('json'):
                total_elements += 1
                json_strings.append(jsonstring)
        else:
            if REQUEST:
                filename = REQUEST.get('filename')
                f = REQUEST.get(filename)
                cte = f.headers.get('content-transfer-encoding')
                if cte == 'base64':
                    filecontent = base64.decodestring(f.read())
                else:
                    filecontent = f.read()
                json_strings.append(asUnicode(filecontent))
            else:
                json_strings.append(asUnicode(jsonstring))
            total_elements = None

        if replace:
            logger.info("Replace mode: removing current design")
            designelements = [o.id for o in
                    self.getDesignElements(sortbyid=False)]
            ObjectManager.manage_delObjects(self, designelements)
            ObjectManager.manage_delObjects(
                self.resources,
                # Un-lazify BTree
                list(self.resources.objectIds()))
            logger.info("Current design removed")

        for jsonstring in json_strings:
            try:
                design = json.loads(jsonstring.encode('utf-8'), object_pairs_hook=OrderedDict)["design"]
            except ValueError:
                withlines = '\n'.join(['{:4d}: {}'.format(i, x.rstrip()) for i, x in enumerate(jsonstring.split('\n'), start=1)])
                logger.error('Could not import \n'+withlines)
                raise
            elements = design.items()

            if not total_elements:
                total_elements = len(elements)

            pos = 6 # have these existing elements 'plomino_documents', 'plomino_index', 'resources', 'scripts', 'temporary_files'
            for (name, element) in design.items():
                if name == 'dbsettings':
                    logger.info("Import db settings")
                    self.importDbSettingsFromJSON(element)
                elif name == 'resources':
                    res_pos = 0
                    for (res_id, res) in design['resources'].items():
                        logger.info("Import resource" + res_id)
                        self.importResourceFromJSON(
                            self.resources, res_id, res, pos=res_pos)
                        res_pos += 1
                else:
                    logger.info("Import " + name)
                    if bundle:
                        self.composeJsonElementFromBundle(name, element, bundle)
                    self.importElementFromJSON(self, name, element, pos=pos)
                    pos += 1
                count = count + 1
                total = total + 1
                if count == 10:
                    self.setStatus(
                        "Importing design (%d%%)" % int(
                            100 * total / total_elements))
                    logger.info(
                        "(%d elements committed, still running...)" % total)
                    txn.savepoint(optimistic=True)
                    count = 0
            #TODO: should remove any orphaned elements?

        logger.info("(%d elements imported)" % total)
        self.setStatus("Ready")
        txn.commit()
        self.getIndex().no_refresh = False

    security.declareProtected(DESIGN_PERMISSION, 'composeJsonElementFromBundle')

    def composeJsonElementFromBundle(self, id, element, bundle):
        for contentId, _ , html in bundle.contents("html"):
            if contentId == id and html:
                element["params"][HTML_PROPERTY] = html
        for contentId, _, pythonScript in bundle.contents("py"):
            if contentId == id and pythonScript:
                self.loadScriptIntoElement(element, pythonScript)
            if "elements" in element:
                for childId, child in element["elements"].iteritems():
                    if contentId == id + '.' + childId and pythonScript:
                        self.loadScriptIntoElement(child, pythonScript)

    def loadScriptIntoElement(self, element, pythonScript):
        content = ""
        inside = False
        for lineNumber, line in enumerate(pythonScript.split('\n')):
            start_reg = re.match(r'^##\s*START\s+(.*){(\s*)$', line)
            end_reg = re.match(r'^##\s*END\s+(.*)}(\s*)$',line)
            if start_reg and not inside:
                methodName = start_reg.group(1).strip()
                inside = True
            elif end_reg and inside:
                element["params"][methodName] = content
                inside = False
                content = ''
            elif not start_reg and not end_reg and inside:
                content+= line+"\n"

    security.declareProtected(DESIGN_PERMISSION, 'loadScriptIntoResource')

    def loadScriptIntoResource(self, res_id, res, bundle):
        for contentId, _, pythonScript in bundle.contents("py"):
            if contentId == res_id:
                res['data'] = pythonScript

    security.declareProtected(DESIGN_PERMISSION, 'importElementFromJSON')

    def importElementFromJSON(self, container, id, element, pos):
        """
        """
        #TODO: security problem. Shouldn't allow any type to be created
        element_type = element['type']
        if id in container.objectIds():
            ob = getattr(container, id)
            if wl_isLocked(ob):
                ob.wl_clearLocks()
            old_pos = container.getObjectPosition(id)
            #container.manage_delObjects([id])
        else:
            container.invokeFactory(element_type, id=id)
            old_pos = container.getObjectPosition(id)
        #TODO What happens if import order is different from order in DB? e.g. field order.
        # Do we move things not in the import to the end or start? or just ensure relative positions are the same?
        #if pos != old_pos:
        #    container.moveObject(id, pos)
            #TODO above line seems to turn id into unicode for some reason
        params = element['params']
        obj = getattr(container, id)
        obj.title = element['title']

        schema = component.getUtility(
            IDexterityFTI, name=obj.portal_type).lookupSchema()

        def set_data(obj, schema):
            fields = getFieldsInOrder(schema)
            for (id, attr) in fields:
                #params[id] = getattr(obj, id, None)
                dm = getMultiAdapter((obj, attr), IDataManager)
                #dm.set(params[id])
                #TODO: should be using the dm but getting adapt error
                # Can only import if the ID is in the params
                if id in params:
                    setattr(obj, id, params[id])
        set_data(obj, schema)
        #HACK to enable the instance behaviour
        if element_type == "PlominoField":
            afterFieldModified(obj, None)
        for behaviour in IBehaviorAssignable(obj).enumerateBehaviors():
            set_data(obj,behaviour.interface)

        obj.reindexObject()

        # if element_type == "PlominoField":
        #     # some params comes from the type-specific schema
        #     # they must be re-set
        #     for param in params:
        #         setattr(obj, param, params[param])
        if 'elements' not in element:
            return
        pos = 0
        for (child_id, child) in element['elements'].items():
            self.importElementFromJSON(obj, child_id, child, pos)
            pos+=1
        # remove any left over children
        for child_id in set(obj.objectIds()) - set(element['elements'].keys()):
            obj.manage_delObjects([child_id])




    security.declareProtected(DESIGN_PERMISSION, 'importDbSettingsFromJSON')

    def importDbSettingsFromJSON(self, settings):
        """
        """
        version = settings['version']
        if version:
            self.plomino_version = version
        if 'params' in settings:
            for (key, value) in settings['params'].items():
                setattr(self, key, value)
        if 'acl' in settings:
            acl = settings['acl']
            if 'AnomynousAccessRight' in acl:
                self.AnomynousAccessRight = acl['AnomynousAccessRight']
                self.setPlominoPermissions(
                    "Anonymous", acl['AnomynousAccessRight'])
            if 'AuthenticatedAccessRight' in acl:
                self.AuthenticatedAccessRight = acl['AuthenticatedAccessRight']
                self.setPlominoPermissions(
                    "Authenticated", acl['AuthenticatedAccessRight'])
            if 'SpecificRights' in acl:
                self.specific_rights = acl['SpecificRights']
            if 'UserRoles' in acl:
                self.UserRoles = acl['UserRoles']

    security.declareProtected(DESIGN_PERMISSION, 'importResourceFromJSON')

    def importResourceFromJSON(self, container, id, element):
        """
        """
        id = id.encode('utf-8')
        resource_type = element['type']
        if id in container.objectIds():
            container.manage_delObjects([id])

        if resource_type == "Page Template":
            obj = manage_addPageTemplate(container, id)
            obj.title = element['title']
            obj.write(element['data'])
        elif resource_type == "Script (Python)":
            manage_addPythonScript(container, id)
            obj = container._getOb(id)
            obj.ZPythonScript_setTitle(element['title'])
            obj.write(element['data'])
        elif resource_type == "Image":
            id = manage_addImage(container, id,
                element['data'].decode('base64'),
                content_type=element['contenttype'])
        else:
            container.manage_addFile(id)
            obj = getattr(container, id)
            obj.meta_type = resource_type
            obj.title = element['title']
            data = element['data'].decode('base64')
            obj.update_data(data, content_type=element['contenttype'])

    def is_profiling(self):
        from Products.CMFPlomino import PROFILING
        return PROFILING

    def profiling_results(self):
        profiling = self.getCache("plomino.profiling")
        if not profiling:
            return {}
        if 'formulas' in profiling.keys():
            grouped_formulas = {}
            for (id, duration) in profiling['formulas']:
                grouped = grouped_formulas.setdefault(id, [0, 0])
                grouped[0] = grouped[0] + 1
                grouped[1] = grouped[0] + duration
                grouped_formulas[id] = grouped
            profiling['distinct formulas'] = [
                [
                    "%s (%d times)" % (
                        id,
                        totals[0]
                    ),
                    totals[1]
                ] for (id, totals) in grouped_formulas.items()]
        for (aspect, durations) in profiling.items():
            maximum = max([d[1] for d in durations])
            durations.sort(key=lambda d: d[1], reverse=True)
            profiling[aspect] = [
                [d[0], d[1], int(100 * d[1] / maximum)] for d in durations
            ]
        self.cleanCache("plomino.profiling")
        return profiling

    security.declarePublic('set_profiling_level')

    def set_profiling_level(self, REQUEST):
        """
        """
        level = REQUEST.get('level', '')
        REQUEST.RESPONSE.setCookie('plomino_profiler', level, path='/')

    security.declarePublic('abortOnError')

    def abortOnError(self):
        """
        """
        self.setRequestCache("ABORT_ON_ERROR", True)

    security.declarePublic('getTemplateList')

    def getTemplateList(self):
        """ Get a list of available template databases
        """
        resource = get_resource_directory()
        if not resource:
            return []
        return resource.listDirectory()

    security.declareProtected(DESIGN_PERMISSION, 'importTemplate')

    def importTemplate(self, REQUEST=None, template_id=None):
        """ Import a template database design
        """
        if REQUEST:
            template_id = REQUEST.get("template_id")
        resource = get_resource_directory()
        if template_id in resource:
            self.importTemplateElement(resource[template_id])
        if REQUEST:
            REQUEST.RESPONSE.redirect(
                "%s/DatabaseDesign" % (self.absolute_url())
            )

    security.declareProtected(DESIGN_PERMISSION, 'importTemplate')

    def importTemplateElement(self, source):
        for name in source.listDirectory():
            if source.isDirectory(name):
                self.importTemplateElement(source[name])
            else:
                json = source.readFile(name)
                self.importDesignFromJSON(jsonstring=json)

from AccessControl import allow_class, allow_module
from AccessControl.SecurityManagement import newSecurityManager


## Context manager which is used inside formulas to raise the security level
## to the that of the owner of the formula

class run_as_owner():

    def __init__(self, context):
        self.context = context
        member = self.context.getParentDatabase().getCurrentMember()
        if member.__class__.__name__ == "SpecialUser":
            self.user = member
        else:
            self.user = member.getUser()

    def __enter__(self):
        owner = self.context.getOwner()
        newSecurityManager(None, owner)

    def __exit__(self, exc_type, exc_value, traceback):
        newSecurityManager(None, self.user)

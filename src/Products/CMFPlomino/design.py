from AccessControl import ClassSecurityInfo
from AccessControl.requestmethod import postonly
from AccessControl.SecurityManagement import newSecurityManager
import base64
import codecs
from cStringIO import StringIO
from DateTime import DateTime
import glob
import json
import logging
from OFS.Folder import Folder
from OFS.Image import manage_addImage
from OFS.ObjectManager import ObjectManager
import os
from plone import api
from plone.dexterity.interfaces import IDexterityFTI
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
from zope.schema import getFieldsInOrder
from ZPublisher.HTTPRequest import FileUpload
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPResponse import HTTPResponse

from .config import (
    DESIGN_PERMISSION,
    MSG_SEPARATOR,
    TIMEZONE,
)
from . import plomino_profiler, get_utils, get_resource_directory
from .config import SCRIPT_ID_DELIMITER
import contents
from .exceptions import PlominoDesignException, PlominoScriptException
from .HttpUtils import authenticateAndLoadURL, authenticateAndPostToURL
from .index.index import PlominoIndex
from .migration import migrate
from .utils import (
    _expandIncludes,
    asUnicode,
    DateToString,
)

logger = logging.getLogger('Plomino')

STR_FORMULA = """plominoContext = context
plominoDocument = context
script_id = '%(script_id)s'
%(import_list)s

%(formula)s
"""


class DesignManager:

    security = ClassSecurityInfo()

    security.declarePublic('manage_refreshDB')

    @postonly
    def manage_refreshDB(self, REQUEST):
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
                v_obj.declareColumn(c.id, c, index=index)
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
                    [o.id for o in self.getForms()] +
                    [o.id for o in self.getViews()] +
                    [o.id for o in self.getAgents()] +
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
                        dbsettings=False)
                    self.saveFile(path, jsonstring)
                else:
                    path = os.path.join(exportpath, (id + '.json'))
                    jsonstring = self.exportDesignAsJSON(
                        elementids=[id],
                        dbsettings=False)
                    self.saveFile(path, jsonstring)
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
                    self.importDesignFromZip(zip_file, replace=replace)
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

    def getFormulaScript(self, script_id):
        return self.scripts._getOb(script_id, None)

    security.declarePublic('cleanFormulaScripts')

    def cleanFormulaScripts(self, script_id_pattern=None):
        for script_id in self.scripts.objectIds():
            if not script_id_pattern or script_id_pattern in script_id:
                self.scripts._delObject(script_id)

    security.declarePublic('compileFormulaScript')

    def compileFormulaScript(self, script_id, formula, with_args=False):
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
            with_args=False, *args):
        formula_str = formula or ''
        compilation_errors = []
        ps = self.getFormulaScript(script_id)
        if not ps:
            ps = self.compileFormulaScript(
                script_id,
                formula_str,
                with_args)
        try:
            contextual_ps = ps.__of__(context)
            result = None
            if with_args:
                result = contextual_ps(*args)
            else:
                result = contextual_ps()
            if (self.debugMode and
                    hasattr(contextual_ps, 'errors') and
                    contextual_ps.errors):
                logger.info('python errors at %s in %s: %s' % (
                    str(context),
                    script_id,
                    str(contextual_ps.errors)))
            return result
        except Exception, e:
            if ps and getattr(ps, 'errors', None):
                compilation_errors = ps.errors
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
                [o.id for o in self.getForms()] +
                [o.id for o in self.getViews()] +
                [o.id for o in self.getAgents()] +
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
                    dbsettings=False)
                zip_file.writestr(filename, jsonstring)
            else:
                filename = os.path.join(db_id, id + '.json')
                jsonstring = self.exportDesignAsJSON(
                    elementids=[id],
                    dbsettings=False)
                zip_file.writestr(filename, jsonstring)
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
        self, elementids=None, REQUEST=None, dbsettings=True
    ):
        """
        """
        data = {'id': self.id, }

        if REQUEST:
            str_elementids = REQUEST.get("elementids")
            if str_elementids is not None:
                elementids = str_elementids.split("@")

        if elementids is None:
            elements = (self.getForms()
                + self.getViews()
                + self.getAgents()
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
        elements.sort(key=lambda elt: elt.getId())
        elements.sort(key=lambda elt: elt.Type())

        design = {'resources': {}, }
        # export database settings
        if dbsettings:
            design['dbsettings'] = self.exportElementAsJSON(
                self, isDatabase=True)

        # export database design elements
        for element in elements:
            if 'Dexterity' in element.meta_type:
                design[element.id] = self.exportElementAsJSON(element)
            else:
                design['resources'][element.id] = self.exportResourceAsJSON(
                    element)

        data['design'] = design

        if REQUEST:
            REQUEST.RESPONSE.setHeader(
                'content-type', "application/json;charset=utf-8")
        return json.dumps(data, sort_keys=True, indent=4).encode('utf-8')

    security.declareProtected(DESIGN_PERMISSION, 'exportElementAsJSON')

    def exportElementAsJSON(self, obj, isDatabase=False):
        """
        """
        data = {}
        if not isDatabase:
            data['id'] = obj.id
            data['type'] = obj.portal_type
            data['title'] = obj.title
        schema = component.getUtility(
            IDexterityFTI, name=obj.portal_type).lookupSchema()

        attributes = getFieldsInOrder(schema)
        if obj.Type() == "PlominoField":
            specific_schema = obj.getSchema()
            for param in specific_schema.names():
                attributes.append((param, specific_schema.get(param)))

        params = {}
        for (id, attr) in attributes:
            params[id] = getattr(obj, id)
        data['params'] = params

        if not isDatabase:
            elementslist = obj.objectIds()
            if elementslist:
                elements = {}
                for id in elementslist:
                    elements[id] = self.exportElementAsJSON(getattr(obj, id))
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

    def exportResourceAsJSON(self, obj):
        """
        """
        id = obj.id
        if callable(id):
            id = id()
        data = {
            'id': id,
            'type': obj.meta_type,
            'title': obj.title,
        }
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

    security.declareProtected(DESIGN_PERMISSION, 'importDesignFromJSON')

    def importDesignFromJSON(self, jsonstring=None, REQUEST=None,
            from_folder=None, replace=False):
        """
        """
        logger.info("Start design import")
        self.setStatus("Importing design")
        self.getIndex().no_refresh = True
        txn = transaction.get()
        json_strings = []
        count = 0
        total = 0
        if from_folder:
            if not os.path.isdir(from_folder):
                raise PlominoDesignException('%s does not exist' % from_folder)
            json_files = (glob.glob(os.path.join(from_folder, '*.json')) +
                glob.glob(os.path.join(from_folder, 'resources/*.json')))
            total_elements = len(json_files)
            for p in json_files:
                fileobj = codecs.open(p, 'r', 'utf-8')
                json_strings.append(fileobj.read())
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
                    self.getForms() +
                    self.getViews() +
                    self.getAgents()]
            ObjectManager.manage_delObjects(self, designelements)
            ObjectManager.manage_delObjects(
                self.resources,
                # Un-lazify BTree
                list(self.resources.objectIds()))
            logger.info("Current design removed")

        for jsonstring in json_strings:
            design = json.loads(jsonstring.encode('utf-8'))["design"]
            elements = design.items()

            if not total_elements:
                total_elements = len(elements)

            for (name, element) in design.items():
                if name == 'dbsettings':
                    logger.info("Import db settings")
                    self.importDbSettingsFromJSON(element)
                elif name == 'resources':
                    for (res_id, res) in design['resources'].items():
                        logger.info("Import resource" + res_id)
                        self.importResourceFromJSON(
                            self.resources, res_id, res)
                else:
                    logger.info("Import " + name)
                    self.importElementFromJSON(self, name, element)
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

        logger.info("(%d elements imported)" % total)
        self.setStatus("Ready")
        txn.commit()
        self.getIndex().no_refresh = False

    security.declareProtected(DESIGN_PERMISSION, 'importDesignFromZip')

    def importDesignFromZip(self, zip_file, replace=False):
        """Import the design from a zip file
        """
        logger.info("Start design import")
        self.setStatus("Importing design")
        self.getIndex().no_refresh = True
        txn = transaction.get()
        count = 0
        total = 0
        if replace:
            logger.info("Replace mode: removing current design")
            designelements = (
                [o.id for o in self.getForms()] +
                [o.id for o in self.getViews()] +
                [o.id for o in self.getAgents()])
            ObjectManager.manage_delObjects(self, designelements)
            ObjectManager.manage_delObjects(
                self.resources,
                list(self.resources.objectIds()))
            logger.info("Current design removed")
        total_elements = None
        file_names = zip_file.namelist()
        for file_name in file_names:
            json_string = zip_file.open(file_name).read()
            if not json_string:
                # E.g. if the zipfile contains entries for directories
                continue
            design = json.loads(json_string)["design"]
            elements = design.items()
            if not total_elements:
                total_elements = len(elements)
            for (name, element) in elements:
                if name in ('resource', 'element', 'dbsettings'):
                    if name == 'dbsettings':
                        logger.info("Import db settings")
                        self.importDbSettingsFromJSON(name, element)
                    if name == 'element':
                        logger.info("Import " + name)
                        self.importElementFromJSON(self, name, element)
                    if name == 'resource':
                        logger.info("Import resource " + name)
                        self.importResourceFromJSON(
                            self.resources, name, element)
                    count = count + 1
                    total = total + 1
                if count == 10:
                    self.setStatus("Importing design (%d%%)" % int(
                        100 * total / total_elements))
                    logger.info(
                        "(%d elements committed, still running...)" % total)
                    txn.savepoint(optimistic=True)
                    count = 0

        logger.info("(%d elements imported)" % total)
        self.setStatus("Ready")
        txn.commit()
        self.getIndex().no_refresh = False

    security.declareProtected(DESIGN_PERMISSION, 'importElementFromJSON')

    def importElementFromJSON(self, container, id, element):
        """
        """
        element_type = element['type']
        if id in container.objectIds():
            ob = getattr(container, id)
            if wl_isLocked(ob):
                ob.wl_clearLocks()
            container.manage_delObjects([id])
        params = element['params']
        container.invokeFactory(element_type, id=id, **params)
        obj = getattr(container, id)
        if element_type == "PlominoField":
            # some params comes from the type-specific schema
            # they must be re-set
            for param in params:
                setattr(obj, param, params[param])
        if 'elements' in element:
            for (child_id, child) in element['elements'].items():
                self.importElementFromJSON(obj, child_id, child)

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

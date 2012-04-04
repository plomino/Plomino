# -*- coding: utf-8 -*-
#
# File: PlominoDesignManager.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from Products.CMFPlomino.config import *

from Acquisition import *
from HttpUtils import authenticateAndLoadURL, authenticateAndPostToURL
from Products.PythonScripts.PythonScript import PythonScript
import re
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPRequest import FileUpload
from OFS.ObjectManager import ObjectManager
from DateTime import DateTime
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from Products.PythonScripts.PythonScript import manage_addPythonScript
from OFS.Image import manage_addImage
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Persistence import Persistent
from webdav.Lockable import wl_isLocked
from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString
import xmlrpclib
from cStringIO import StringIO
import traceback
import codecs
import os
import sys
import glob
import transaction
from zope import event
from Products.Archetypes.event import ObjectEditedEvent
from zope.component import getUtility
from dm.sharedresource import get_resource
try:
    from plone.app.async.interfaces import IAsyncService
    ASYNC = True
except:
    ASYNC = False

from migration.migration import migrate
from index.PlominoIndex import PlominoIndex
from exceptions import PlominoScriptException, PlominoDesignException
from PlominoUtils import asUnicode
from Products.CMFPlomino import get_utils
# get AT specific schemas for each Plomino class
from Products.CMFPlomino.PlominoForm import schema as form_schema
from Products.CMFPlomino.PlominoAction import schema as action_schema
from Products.CMFPlomino.PlominoField import schema as field_schema
from Products.CMFPlomino.PlominoHidewhen import schema as hidewhen_schema
from Products.CMFPlomino.PlominoAgent import schema as agent_schema
from Products.CMFPlomino.PlominoView import schema as view_schema
from Products.CMFPlomino.PlominoColumn import schema as column_schema

plomino_schemas = {'PlominoForm': form_schema, 
                   'PlominoAction': action_schema,
                   'PlominoField': field_schema,
                   'PlominoHidewhen': hidewhen_schema,
                   'PlominoAgent': agent_schema,
                   'PlominoView': view_schema,
                   'PlominoColumn': column_schema
                   }
extra_schema_attributes = ['excludeFromNav']

import logging
logger = logging.getLogger('Plomino')

def run_refreshdb(context):
    # for async call
    context.refreshDB()

class PlominoDesignManager(Persistent):
    """Plomino design import/export features
    """
    security = ClassSecurityInfo()

    # Methods
    security.declarePublic('manage_refreshDB')
    def manage_refreshDB(self, REQUEST):
        """launch refreshDB
        """
        if ASYNC:
            self.refreshDB_async()
            report = ['Database refreshing has been launched in asynchronous mode.']
        else:
            report = self.refreshDB()
            
        self.writeMessageOnPage(MSG_SEPARATOR.join(report), REQUEST, False)
        REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign")
    
    security.declarePublic('refreshDB_async')
    def refreshDB_async(self):
        """refresh db in asynchronous mode
        """
        async = getUtility(IAsyncService)
        job = async.queueJob(run_refreshdb, self)
        all_db_status = get_resource("plomino_status", dict)
        all_db_status[self.absolute_url_path()] = job
        
    security.declareProtected(DESIGN_PERMISSION, 'refreshDB')
    def refreshDB(self):
        """all actions to take when reseting a DB (after import for instance)
        """
        logger.info('Refreshing database '+self.id)
        report = []

        self.setStatus("Refreshing design")
        # migrate to current version
        messages = migrate(self)
        for msg in messages:
            report.append(msg)
            logger.info(msg)

        #check folders
        if not hasattr(self, 'resources'):
            resources = Folder('resources')
            resources.title='resources'
            self._setObject('resources', resources)
        msg = 'Resources folder OK'
        report.append(msg)
        logger.info(msg)
        if not hasattr(self, 'scripts'):
            scripts = Folder('scripts')
            scripts.title='scripts'
            self._setObject('scripts', scripts)
        self.cleanFormulaScripts()
        msg = 'Scripts folder OK and clean'
        report.append(msg)
        logger.info(msg)

        # clean portal_catalog
        portal_catalog = self.portal_catalog
        catalog_entries = portal_catalog.search({'portal_type' : ['PlominoDocument'], 'path': '/'.join(self.getPhysicalPath())})
        for d in catalog_entries:
            portal_catalog.uncatalog_object(d.getPath())
        msg = 'Portal catalog clean'
        report.append(msg)
        logger.info(msg)

        #create new blank index (without fulltext)
        index = PlominoIndex(FULLTEXT=False).__of__(self)
        index.no_refresh = True
        msg = 'New index created'
        report.append(msg)
        logger.info(msg)

        #declare all indexed fields
        for f_obj in self.getForms() :
            for f in f_obj.getFormFields():
                if f.getToBeIndexed() :
                    index.createFieldIndex(f.id, f.getFieldType())
        logger.info('Field indexing initialized')

        #declare all the view formulas and columns index entries
        for v_obj in self.getViews():
            index.createSelectionIndex('PlominoViewFormula_'+v_obj.getViewName())
            for c in v_obj.getColumns():
                v_obj.declareColumn(c.getColumnName(), c, index=index)
        # add fulltext if needed
        if self.FulltextIndex:
            index.createFieldIndex('SearchableText', 'RICHTEXT')
        logger.info('Views indexing initialized')
        
        # re-index documents
        start_time = DateTime().toZone('UTC')
        msg = self.reindexDocuments(index)
        report.append(msg)
        
        # as it takes time, re-indexed documents changed since re-indexing started
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
        if self.getIndexInPortal():
            self.refreshPortalCatalog()
            
        # update Plone workflow state and role permissions
        self.refreshWorkflowState()
        self.refreshPlominoRolesPermissions()
        
        self.setStatus("Ready")
        return report

    security.declareProtected(DESIGN_PERMISSION, 'reindexDocuments')
    def reindexDocuments(self, plomino_index, items_only=False, views_only=False, update_metadata=1, changed_since=None):
        documents = self.getAllDocuments()
        if changed_since:
            documents = [doc for doc in documents if doc.plomino_modification_time > changed_since]
            total_docs = len(documents)
            logger.info('Re-indexing %d changed document(s) since %s' % (total_docs, str(changed_since)))
        else:
            total_docs = len(self.plomino_documents)
            logger.info('Existing documents: '+ str(total_docs))
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
        view_indexes = [idx for idx in indexes if idx.startswith("PlominoView")]
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
                plomino_index.indexDocument(d, idxs=idxs, update_metadata=update_metadata)
                txn.commit()
                total = total + 1
            except Exception, e:
                errors = errors + 1
                logger.info("Ouch! \n%s\n%s" % (e, `d`))
            counter = counter + 1
            if counter == 10:
                self.setStatus("Re-indexing %s (%d%%)" % (label, int(100*(total+errors)/total_docs)))
                counter = 0
                logger.info("Re-indexing %s: %d indexed successfully, %d errors(s)..." % (label, total, errors))
        if changed_since:
            msg = "Intermediary changes: %d modified documents re-indexed successfully, %d errors(s)" % (total, errors)
        else:
            msg = "Re-indexing %s: %d documents indexed successfully, %d errors(s)" % (label, total, errors)
        logger.info(msg)
        return msg

    security.declareProtected(DESIGN_PERMISSION, 'refreshDB')
    def recomputeAllDocuments(self, REQUEST=None):
        """
        """
        logger.info('Re-compute documents in '+self.id)
        documents = self.getAllDocuments()
        total_docs = len(self.plomino_documents)
        logger.info('Existing documents: '+ str(total_docs))
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
                logger.info("Ouch! \n%s\n%s" % (e, `d`))
            counter = counter + 1
            if counter == 10:
                self.setStatus("Re-compute documents (%d%%)" % int(100*(total+errors)/total_docs))
                counter = 0
                logger.info("Re-compute documents: %d computed successfully, %d errors(s) ..." % (total, errors))
        msg = "Re-compute documents: %d documents computed successfully, %d errors(s)" % (total, errors)
        logger.info(msg)
        self.setStatus("Ready")
        if REQUEST:
            self.writeMessageOnPage(msg, REQUEST, False)
            REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign")

    security.declareProtected(DESIGN_PERMISSION, 'refreshPortalCatalog')
    def refreshPortalCatalog(self, REQUEST=None):
        """
        """
        msg = ""
        portal_catalog = self.portal_catalog
        if self.getIndexInPortal():
            logger.info('Refresh documents from '+self.id+' in portal catalog')
            documents = self.getAllDocuments()
            total_docs = len(self.plomino_documents)
            logger.info('Existing documents: '+ str(total_docs))
            for d in documents:
                portal_catalog.catalog_object(d, "/".join(self.getPhysicalPath() + (d.id,)))
            msg = '%d documents re-cataloged' % total_docs
        else:
            logger.info('Database '+self.id+' does not allow portal catalog indexing.')
            catalog_entries = portal_catalog.search({'portal_type' : ['PlominoDocument'], 'path': '/'.join(self.getPhysicalPath())})
            if catalog_entries:
                for d in catalog_entries:
                    portal_catalog.uncatalog_object(d.getPath())
                logger.info('Related portal catalog entries have been removed.')
            msg = 'Database is not cataloged'
        
        logger.info(msg)
        if REQUEST:
            self.writeMessageOnPage(msg, REQUEST, False)
            REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign")

    security.declareProtected(DESIGN_PERMISSION, 'refreshWorkflowState')
    def refreshWorkflowState(self):
        """ Prevent Plone security inconsistencies when refreshing design
        """
        workflow_tool = getToolByName(self, 'portal_workflow')
        wfs = workflow_tool.getWorkflowsFor(self)
        for wf in wfs:
            if not isinstance( wf, DCWorkflowDefinition ):
                continue
            wf.updateRoleMappingsFor( self )
        logger.info('Plone workflow update')

    security.declareProtected(DESIGN_PERMISSION, 'exportDesign')
    def exportDesign(self, targettype='file', targetfolder='', dbsettings=True, designelements=None, REQUEST=None, **kw):
        """ Export design elements to XML.
        The targettype can be file, server, or folder.
        """
        if REQUEST:
            entire=REQUEST.get('entire')
            targettype=REQUEST.get('targettype')
            targetfolder=REQUEST.get('targetfolder')
            dbsettings=REQUEST.get('dbsettings')

        if dbsettings == "Yes":
            dbsettings = True
        else:
            dbsettings = False

        if not designelements is None:
            if entire=="Yes":
                designelements = None
            else:
                designelements=REQUEST.get('designelements')
                if designelements:
                    if type(designelements)==str:
                        designelements=[designelements]

        if targettype in ["server", "file"]:
            xmlstring = self.exportDesignAsXML(elementids=designelements, dbsettings=dbsettings)

            if targettype == "server":
                if REQUEST:
                    targetURL=REQUEST.get('targetURL')
                    username=REQUEST.get('username')
                    password=REQUEST.get('password')
                result=authenticateAndPostToURL(targetURL+"/importDesignFromXML", username, password, 'exportDesignAsXML.xml', xmlstring)
                REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign")
            elif targettype == "file":
                if REQUEST:
                    REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
                    REQUEST.RESPONSE.setHeader("Content-Disposition", "attachment; filename="+self.id+".xml")
                return xmlstring
        elif targettype == "folder":
            if not designelements:
                designelements = ([o.id for o in self.getForms()] +
                                  [o.id for o in self.getViews()] +
                                  [o.id for o in self.getAgents()] +
                                  ["resources/"+id for id in self.resources.objectIds()])
            exportpath = os.path.join(targetfolder,(self.id))
            resources_exportpath = os.path.join(exportpath,('resources'))
            if os.path.isdir(exportpath):
                # remove previous export
                for f in glob.glob(os.path.join(exportpath,"*.xml")):
                    os.remove(f)
                if os.path.isdir(resources_exportpath):
                    for f in glob.glob(os.path.join(resources_exportpath,"*.xml")):
                        os.remove(f)
            else:
                os.makedirs(exportpath)
            if len([id for id in designelements if id.startswith('resources/')]) > 0:
                if not os.path.isdir(resources_exportpath):
                    os.makedirs(resources_exportpath)

            for id in designelements:
                if id.startswith('resources/'):
                    path = os.path.join(resources_exportpath, (id.split('/')[-1]+'.xml'))
                    xmlstring = self.exportDesignAsXML(elementids=[id], dbsettings=False)
                    self.saveFile(path, xmlstring)
                else:
                    path = os.path.join(exportpath, (id+'.xml'))
                    xmlstring = self.exportDesignAsXML(elementids=[id], dbsettings=False)
                    self.saveFile(path, xmlstring)
            if dbsettings:
                path = os.path.join(exportpath, ('dbsettings.xml'))
                xmlstring = self.exportDesignAsXML(elementids=[], dbsettings=True)
                self.saveFile(path, xmlstring.decode('utf-8'))


    @staticmethod
    def saveFile(path, content):
        fileobj = codecs.open(path, "w", "utf-8")
        try:
          logger.info('saveFile> write with no decode')
          fileobj.write(content)
        except UnicodeDecodeError, e:
          fileobj.write(content.decode('utf-8'))
          logger.info('saveFile> write.decode("utf-8"): %s'%path)
        fileobj.close()


    security.declareProtected(DESIGN_PERMISSION, 'importDesign')
    def importDesign(self, REQUEST=None):
        """import design elements in current database
        """
        submit_import=REQUEST.get('submit_import')
        entire=REQUEST.get('entire')
        sourcetype=REQUEST.get('sourcetype')
        sourceURL=REQUEST.get('sourceURL')
        username=REQUEST.get('username')
        password=REQUEST.get('password')
        replace_design=REQUEST.get('replace_design')
        replace = replace_design == "Yes"
        if submit_import:
            if sourcetype=="server":
                export_url=sourceURL+"/exportDesignAsXML"
                if not entire=="Yes":
                    designelements=REQUEST.get('designelements')
                    if designelements:
                        if type(designelements)==str:
                            designelements=[designelements]
                        export_url=export_url+"?elementids="+"@".join(designelements)
                xmlstring=authenticateAndLoadURL(export_url, username, password).read()
                self.importDesignFromXML(xmlstring, replace=replace)

            elif sourcetype =="folder":
                path = REQUEST.get('sourcefolder')
                self.importDesignFromXML(from_folder=path, replace=replace)

            else:
                fileToImport = REQUEST.get('sourceFile',None)
                if not fileToImport:
                    raise PlominoDesignException, 'file required'
                if not isinstance(fileToImport, FileUpload):
                    raise PlominoDesignException, 'unrecognized file uploaded'
                xmlstring=fileToImport.read()
                self.importDesignFromXML(xmlstring, replace=replace)

            no_refresh_documents = REQUEST.get('no_refresh_documents', 'No')
            if no_refresh_documents == 'No':
                self.refreshDB()
            else:
                self.refreshWorkflowState()
            REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign")
        else:
            REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign?username="+username+"&password="+password+"&sourceURL="+sourceURL)

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
        ids = self.resources.objectIds()
        ids.sort()
        return '/'.join(ids)

    security.declareProtected(DESIGN_PERMISSION, 'getRemoteViews')
    def getRemoteViews(self, sourceURL, username, password):
        """ Get views ids list from remote database
        """
        views = authenticateAndLoadURL(sourceURL+"/getViewsList", username, password).read()
        ids = views.split('/')
        ids.pop()
        return ids

    security.declareProtected(DESIGN_PERMISSION, 'getRemoteForms')
    def getRemoteForms(self, sourceURL, username, password):
        """ Get forms ids list from remote database
        """
        forms = authenticateAndLoadURL(sourceURL+"/getFormsList", username, password).read()
        ids = forms.split('/')
        ids.pop()
        return ids

    security.declareProtected(DESIGN_PERMISSION, 'getRemoteAgents')
    def getRemoteAgents(self, sourceURL, username, password):
        """ Get agents ids list from remote database
        """
        agents = authenticateAndLoadURL(sourceURL+"/getAgentsList", username, password).read()
        ids = agents.split('/')
        ids.pop()
        return ids

    security.declareProtected(DESIGN_PERMISSION, 'getRemoteResources')
    def getRemoteResources(self, sourceURL, username, password):
        """ Get resources ids list from remote database
        """
        res = authenticateAndLoadURL(sourceURL+"/getResourcesList", username, password).read()
        ids = res.split('/')
        ids.pop()
        return ['resources/'+i for i in ids]

    security.declarePublic('getFormulaScript')
    def getFormulaScript(self, script_id):
        if hasattr(self.scripts, script_id):
            ps=getattr(self.scripts, script_id)
            return ps
        else:
            return None

    security.declarePublic('cleanFormulaScripts')
    def cleanFormulaScripts(self, script_id_pattern=None):
        for s in self.scripts.objectIds():
            if script_id_pattern is None:
                self.scripts._delObject(s)
            elif s.startswith(script_id_pattern):
                self.scripts._delObject(s)

    security.declarePublic('compileFormulaScript')
    def compileFormulaScript(self, script_id, formula, with_args=False):
        ps = self.getFormulaScript(script_id)
        if ps is None:
            ps=PythonScript(script_id)
            self.scripts._setObject(script_id, ps)
        ps = self.getFormulaScript(script_id)

        if with_args:
            ps._params="*args"
        str_formula="plominoContext = context\n"
        str_formula=str_formula+"plominoDocument = context\n"
        #str_formula=str_formula+"from Products.CMFPlomino.PlominoUtils import "+SAFE_UTILS+'\n'
        safe_utils = get_utils()
        import_list = []
        for module in safe_utils:
            import_list.append("from %s import %s" % (module, ", ".join(safe_utils[module])))
        str_formula=str_formula+";".join(import_list)+'\n'

        r = re.compile('#Plomino import (.+)[\r\n]')
        for i in r.findall(formula):
            scriptname=i.strip()
            try:
                script_code = self.resources._getOb(scriptname).read()
            except:
                script_code = "#ALERT: "+scriptname+" not found in resources"
            formula = formula.replace('#Plomino import '+scriptname, script_code)

        if formula.strip().count('\n')>0:
            str_formula=str_formula+formula
        else:
            if formula.startswith('return '):
                str_formula=str_formula+formula
            else:
                str_formula=str_formula+"return "+formula
        ps.write(str_formula)
        if self.debugMode:
            logger.info(script_id + " compiled")
        return ps

    security.declarePublic('runFormulaScript')
    def runFormulaScript(self, script_id, context, formula_getter, with_args=False, *args):
        try:
            ps = self.getFormulaScript(script_id)
            if ps is None:
                ps = self.compileFormulaScript(script_id, formula_getter(), with_args)
                if self.debugMode and hasattr(ps, 'errors') and ps.errors:
                    logger.info('ps.errors : ' + str(ps.errors))
            contextual_ps=ps.__of__(context)
            result = None
            if with_args:
                result = contextual_ps(*args)
            else:
                result = contextual_ps()
            if self.debugMode and hasattr(contextual_ps, 'errors') and contextual_ps.errors:
                logger.info('python errors at '+str(context)+' in '+script_id+': ' + str(contextual_ps.errors))
            return result
        except Exception, e:
            raise PlominoScriptException(context, e, formula_getter, script_id)

    security.declarePrivate('traceRenderingErr')
    def traceRenderingErr(self, e, context):
        """trace rendering errors
        """
        if self.debugMode:
            #traceback
            formatted_lines = traceback.format_exc().splitlines()
            msg = "\n".join(formatted_lines[-3:]).strip()
            #code / value
            msg = msg + "\nPlomino rendering error with context: " + '/'.join(context.getPhysicalPath())
        else:
            msg = None

        if msg:
            logger.error(msg)

    security.declarePublic('callScriptMethod')
    def callScriptMethod(self, scriptname, methodname, *args):
        id="script_"+scriptname+"_"+methodname
        try:
            script_code = self.resources._getOb(scriptname).read()
        except:
            script_code = "#ALERT: "+scriptname+" not found in resources"
        formula=lambda:script_code+'\n\nreturn '+methodname+'(*args)'

        return self.runFormulaScript(id, self, formula, True, *args)

    security.declarePublic('writeMessageOnPage')
    def writeMessageOnPage(self, infoMsg, REQUEST, error = False):
        """adds portal message        
        """
        #message
        plone_tools = getToolByName(self, 'plone_utils')
        if plone_tools is not None:
            #portal message type
            if error:
                msgType = 'error'
            else:
                msgType = 'info'

            #split message   
            infoMsg = infoMsg.split(MSG_SEPARATOR)

            #display it
            for msg in infoMsg:
                if msg:
                    plone_tools.addPortalMessage(msg, msgType, REQUEST)

    security.declarePublic('getRenderingTemplate')
    def getRenderingTemplate(self, templatename, request=None):
        """
        """
        skin=self.portal_skins.cmfplomino_templates
        if hasattr(skin, templatename):
            pt = getattr(skin, templatename)
            if request:
                pt.REQUEST = request
            else:
                request = getattr(pt, 'REQUEST', None)
                proper_request = request and pt.REQUEST.__class__.__name__=='HTTPRequest'
                if not proper_request:
                    # XXX What *else* could REQUEST be here?
                    # we are not in an actual web context, but we a need a
                    # request object to have the template working
                    response = HTTPResponse(stdout=sys.stdout)
                    env = {'SERVER_NAME':'fake_server',
                           'SERVER_PORT':'80',
                           'REQUEST_METHOD':'GET'}
                    pt.REQUEST = HTTPRequest(sys.stdin, env, response)

            # we also need a RESPONSE
            if not pt.REQUEST.has_key('RESPONSE'):
                pt.REQUEST['RESPONSE']=HTTPResponse()

            return pt
        else:
            return None

    security.declareProtected(DESIGN_PERMISSION, 'exportDesignAsXML')
    def exportDesignAsXML(self, elementids=None, REQUEST=None, dbsettings=True):
        """
        """
        impl = getDOMImplementation()
        doc = impl.createDocument(None, "plominodatabase", None)
        root = doc.documentElement
        root.setAttribute("id", self.id)

        if REQUEST:
            str_elementids=REQUEST.get("elementids")
            if str_elementids is not None:
                elementids = str_elementids.split("@")

        if elementids is None:
            elements = self.getForms() + self.getViews() + self.getAgents() + [o for o in self.resources.getChildNodes()] 
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

        designNode = doc.createElement('design')

        # export database settings
        if dbsettings:
            node = self.exportElementAsXML(doc, self, isDatabase=True)
            designNode.appendChild(node)

        # export database design elements
        for e in elements:
            if e.meta_type in plomino_schemas.keys():
                node = self.exportElementAsXML(doc, e)
            else:
                node = self.exportResourceAsXML(doc, e)

            designNode.appendChild(node)

        root.appendChild(designNode)
        s = doc.toxml()

        if REQUEST:
            REQUEST.RESPONSE.setHeader('content-type', "text/xml;charset=utf-8")

        # Usage of lxml to make a pretty output
        try:
            from lxml import etree
            parser = etree.XMLParser(strip_cdata=False, encoding="utf-8")
            return etree.tostring(etree.XML(s, parser), encoding="utf-8", pretty_print=True)
        except ImportError:
            return s.encode('utf-8').replace("><", ">\n<")

    security.declareProtected(DESIGN_PERMISSION, 'exportElementAsXML')
    def exportElementAsXML(self, xmldoc, obj, isDatabase=False):
        """
        """
        if isDatabase:
            node = xmldoc.createElement('dbsettings')
            schema = sys.modules[self.__module__].schema
        else:
            node = xmldoc.createElement('element')
            node.setAttribute('id', obj.id)
            node.setAttribute('type', obj.Type())
            title = obj.title
            node.setAttribute('title', title)
            schema = plomino_schemas[obj.Type()]

        for f in schema.fields():
            fieldNode = xmldoc.createElement(f.getName())
            field_type = f.getType()
            fieldNode.setAttribute('type', field_type)
            v = f.get(obj)
            if v is not None:
                if field_type=="Products.Archetypes.Field.TextField":
                    text = xmldoc.createCDATASection(f.getRaw(obj).decode('utf-8'))
                else:
                    text = xmldoc.createTextNode(str(f.get(obj)))
                fieldNode.appendChild(text)
            node.appendChild(fieldNode)

        # add AT standard extra attributes
        for extra in extra_schema_attributes:
            f = obj.Schema().getField(extra)
            if f is not None:
                fieldNode = xmldoc.createElement(extra)
                field_type = f.getType()
                fieldNode.setAttribute('type', field_type)
                v = f.get(obj)
                if v is not None:
                    if field_type=="Products.Archetypes.Field.TextField":
                        text = xmldoc.createCDATASection(f.getRaw(obj).decode('utf-8'))
                    else:
                        text = xmldoc.createTextNode(str(f.get(obj)))
                    fieldNode.appendChild(text)
                node.appendChild(fieldNode)
#        
        if obj.Type() == "PlominoField":
            adapt = obj.getSettings()
            if adapt is not None:
                items = {}
                for k in adapt.parameters.keys():
                    if hasattr(adapt, k):
                        items[k] = adapt.parameters[k]
                #items = dict(adapt.parameters)
                if len(items)>0:
                    # export field settings
                    str_items = xmlrpclib.dumps((items,), allow_none=1)
                    dom_items = parseString(str_items)
                    node.appendChild(dom_items.documentElement)
        if not isDatabase:
            elementslist = obj.objectIds()
            if len(elementslist)>0:
                elements = xmldoc.createElement('elements')
                for id in elementslist:
                    elementNode = self.exportElementAsXML(xmldoc, getattr(obj, id))
                    elements.appendChild(elementNode)
                node.appendChild(elements)

        if isDatabase:
           acl = xmldoc.createElement('acl')
           acl.setAttribute('AnomynousAccessRight', obj.AnomynousAccessRight)
           acl.setAttribute('AuthenticatedAccessRight', obj.AuthenticatedAccessRight)
           str_UserRoles = xmlrpclib.dumps((obj.UserRoles,), allow_none=1)
           dom_UserRoles = parseString(str_UserRoles)
           dom_UserRoles.firstChild.setAttribute('id', 'UserRoles')
           acl.appendChild(dom_UserRoles.documentElement)
           str_SpecificRights = xmlrpclib.dumps((obj.getSpecificRights(),), allow_none=1)
           dom_SpecificRights = parseString(str_SpecificRights)
           dom_SpecificRights.firstChild.setAttribute('id', 'SpecificRights')
           acl.appendChild(dom_SpecificRights.documentElement)
           node.appendChild(acl)
           node.setAttribute('version', obj.plomino_version)

        return node

    security.declareProtected(DESIGN_PERMISSION, 'exportResourceAsXML')
    def exportResourceAsXML(self, xmldoc, obj):
        """
        """
        node = xmldoc.createElement('resource')
        id = obj.id
        if callable(id):
            id=id()
        node.setAttribute('id', id)
        resource_type = obj.meta_type
        node.setAttribute('type', resource_type)
        node.setAttribute('title', obj.title)
        #if resource_type in ["Page Template", "Script (Python)"]:
        if hasattr(obj, 'read'):
            data = xmldoc.createCDATASection(obj.read())
        else:
            node.setAttribute('contenttype', obj.getContentType())
            stream = obj.data
            if not hasattr(stream, "encode"):
                stream = stream.data
            data = xmldoc.createCDATASection(stream.encode('base64'))
        node.appendChild(data)
        return node

    security.declareProtected(DESIGN_PERMISSION, 'importDesignFromXML')
    def importDesignFromXML(self, xmlstring=None, REQUEST=None, from_folder=None, replace=False):
        """
        """
        logger.info("Start design import")
        self.setStatus("Importing design")
        self.getIndex().no_refresh = True
        txn = transaction.get()
        xml_strings = []
        count = 0
        total = 0
        if from_folder:
            if not os.path.isdir(from_folder):
                raise PlominoDesignException, '%s does not exist' % path
            xml_files = (glob.glob(os.path.join(from_folder, '*.xml')) +
                     glob.glob(os.path.join(from_folder, 'resources/*.xml')))
            total_elements = len(xml_files)
            for p in xml_files:
                fileobj = codecs.open(p, 'r', 'utf-8')
                xml_strings.append(fileobj.read())
        else:
            if REQUEST:
                f=REQUEST.get("file")
                xml_strings.append(asUnicode(f.read()))
            else:
                xml_strings.append(asUnicode(xmlstring))
            total_elements = None

        if replace:
            logger.info("Replace mode: removing current design")
            designelements = [o.id for o in self.getForms()] \
                                 + [o.id for o in self.getViews()] \
                                 + [o.id for o in self.getAgents()]
            ObjectManager.manage_delObjects(self, designelements)
            ObjectManager.manage_delObjects(self.resources, self.resources.objectIds())
            logger.info("Current design removed")

        for xmlstring in xml_strings:
            xmlstring = xmlstring.replace(">\n<", "><")
            xmldoc = parseString(xmlstring.encode('utf-8'))
            design = xmldoc.getElementsByTagName("design")[0]
            elements = [e for e in design.childNodes
                            if e.nodeName in ('resource', 'element', 'dbsettings')]

            if not total_elements:
                total_elements = len(elements)

            e = design.firstChild
            while e is not None:
                name = str(e.nodeName)
                if name in ('resource', 'element', 'dbsettings'):
                    if name == 'dbsettings':
                        logger.info("Import db settings")
                        self.importDbSettingsFromXML(e)
                    if name == 'element':
                        logger.info("Import "+e.getAttribute('id'))
                        self.importElementFromXML(self, e)
                    if name == 'resource':
                        logger.info("Import resource "+e.getAttribute('id'))
                        self.importResourceFromXML(self.resources, e)
                    count = count + 1
                    total = total + 1
                if count == 10:
                    self.setStatus("Importing design (%d%%)" % int(100*total/total_elements))
                    logger.info("(%d elements committed, still running...)" % total)
                    txn.savepoint(optimistic=True)
                    count = 0
                e = e.nextSibling

        logger.info("(%d elements imported)" % total)
        self.setStatus("Ready")
        txn.commit()
        self.getIndex().no_refresh = False

    security.declareProtected(DESIGN_PERMISSION, 'importElementFromXML')
    def importElementFromXML(self, container, node):
        """
        """
        id = node.getAttribute('id')
        element_type = node.getAttribute('type')
        if id in container.objectIds():
            ob = getattr(container, id)
            if wl_isLocked(ob):
                ob.wl_clearLocks()
            container.manage_delObjects([id])
        container.invokeFactory(element_type, id=id)
#        if not(hasattr(container, id)):
#            container.invokeFactory(element_type, id=id)
        obj = getattr(container, id)
        if obj.Type() == element_type:
            # note: there might be an existing object with the same id but with a
            # different type, in this case, we do not import
            title = node.getAttribute('title')
            obj.setTitle(title)
            child = node.firstChild
            at_values = {}
            settings_values = {}
            while child is not None:
                name = child.nodeName
                if name == 'id':
                    pass
                elif name == 'elements':
                    # current object is a form or a view, it contains sub-objects
                    # (fields, actions, columns, hide-when)
                    subchild = child.firstChild
                    while subchild is not None:
                        if subchild.nodeType == subchild.ELEMENT_NODE:
                            self.importElementFromXML(obj, subchild)
                        subchild = subchild.nextSibling
                elif name == 'params':
                    # current object is a field, the params tag contains the
                    # specific settings
                    result, method = xmlrpclib.loads(node.toxml().encode('utf-8'))
                    parameters = result[0]
                    for key in parameters.keys():
                        v = parameters[key]
                        if v is not None:
                            if hasattr(v, 'encode'):
                                v = unicode(v)
                            else:
                                if hasattr(v, 'append'):
                                    uv = []
                                    for e in v:
                                        if hasattr(e, 'encode'):
                                            uv.append(unicode(e))
                                        else:
                                            uv.append(e)
                                    v = uv
                            settings_values[key] = v
                else:
                    if child.hasChildNodes():
                        field = obj.Schema().getField(name)

                        # Get cdata content if available, else get text node
                        cdatas = [n for n in child.childNodes if n.nodeType == n.CDATA_SECTION_NODE]
                        if len(cdatas) > 0:
                            v = cdatas[0].data
                        else:
                            v = child.firstChild.data
                        v = v.strip()
                        at_values[name] = v
                child = child.nextSibling

            if element_type == "PlominoForm":
                at_values['FormLayout_text_format'] = "text/html"
                
            if len(at_values) > 0:
                obj.processForm(REQUEST=None, values=at_values)
            
            if len(settings_values) > 0:
                adapt = obj.getSettings()
                for key in settings_values.keys():
                    setattr(adapt, key, settings_values[key])

    security.declareProtected(DESIGN_PERMISSION, 'importDbSettingsFromXML')
    def importDbSettingsFromXML(self, node):
        """
        """
        version = node.getAttribute('version')
        if version:
            self.plomino_version = version
        child = node.firstChild
        while child is not None:
            name = child.nodeName
            logger.info(name)
            if name=='acl':
                anonymousaccessright = child.getAttribute('AnomynousAccessRight')
                self.AnomynousAccessRight = anonymousaccessright
                self.setPlominoPermissions("Anonymous", anonymousaccessright)
                authenticatedaccessright = child.getAttribute('AuthenticatedAccessRight')
                self.AuthenticatedAccessRight = authenticatedaccessright
                self.setPlominoPermissions("Authenticated", authenticatedaccessright)
                subchild = child.firstChild
                while subchild is not None:
                    if subchild.nodeType == subchild.ELEMENT_NODE:
                        result, method = xmlrpclib.loads(subchild.toxml())
                        object_type = subchild.getAttribute('id')
                        if object_type=="SpecificRights":
                            self.specific_rights = result[0]
                        else:
                            self.UserRoles = result[0]
                    subchild = subchild.nextSibling

            else:
                if child.hasChildNodes():
                    field = self.Schema().getField(name)
                    #field.set(self, child.firstChild.data)
                    result=field.widget.process_form(self, field, {name : child.firstChild.data})
                    field.set(self, result[0])
            child = child.nextSibling

    security.declareProtected(DESIGN_PERMISSION, 'importResourceFromXML')
    def importResourceFromXML(self, container, node):
        """
        """
        id = str(node.getAttribute('id'))
        resource_type = node.getAttribute('type')
        if hasattr(container, id):
            container.manage_delObjects([id])

        if resource_type == "Page Template":
            obj = manage_addPageTemplate(container, id)
            obj.title = node.getAttribute('title')
            obj.write(node.firstChild.data)
        elif resource_type == "Script (Python)":
            manage_addPythonScript(container, id)
            obj = container._getOb(id)
            obj.ZPythonScript_setTitle(node.getAttribute('title'))
            obj.write(node.firstChild.data)
        elif resource_type == "Image":
            id = manage_addImage(container, id,
                    node.firstChild.data.decode('base64'),
                    content_type=node.getAttribute('contenttype'))
        else:
            container.manage_addFile(id)
            obj = getattr(container, id)
            obj.meta_type = resource_type
            obj.title = node.getAttribute('title')
            obj.update_data(
                    node.firstChild.data.decode('base64'),
                    content_type=node.getAttribute('contenttype'))




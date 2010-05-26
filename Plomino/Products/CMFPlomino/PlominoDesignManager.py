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

from cStringIO import StringIO
from traceback import print_exc
from Acquisition import *
from index.PlominoIndex import PlominoIndex
from Products.CMFPlomino.exceptions import PlominoDesignException
from HttpUtils import authenticateAndLoadURL, authenticateAndPostToURL
from Products.PythonScripts.PythonScript import PythonScript
import re
from ZPublisher.HTTPResponse import HTTPResponse
from ZPublisher.HTTPRequest import HTTPRequest
from ZPublisher.HTTPRequest import FileUpload
from Products.PageTemplates.ZopePageTemplate import manage_addPageTemplate
from Products.CMFCore.utils import getToolByName
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Persistence import Persistent
from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString
from xml.sax.saxutils import escape, unescape
import xmlrpclib
from cStringIO import StringIO
import sys

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


class PlominoDesignManager(Persistent):
    """Plomino design import/export features
    """
    security = ClassSecurityInfo()

    # Methods

    security.declareProtected(DESIGN_PERMISSION, 'refreshDB')
    def refreshDB(self, REQUEST=None):
        """all actions to take when reseting a DB (after import for instance)
        """
        logger.info('Refreshing database '+self.id)
        report = []
        
        # migrate to current version
        if not(hasattr(self, "plomino_version")):
            msg = 'Migration to 1.3.0'
            report.append(msg)
            logger.info(msg)
            from migration.migration import migrate_to_130
            msg = migrate_to_130(self)
            report.append(msg)
            logger.info(msg)
        if self.plomino_version=="1.3.0":
            # no migration needed here
            self.plomino_version = "1.4.0"
        if self.plomino_version=="1.4.0":
            from migration.migration import migrate_to_15
            msg = migrate_to_15(self)
            report.append(msg)
            logger.info(msg)
        if self.plomino_version=="1.5":
            from migration.migration import migrate_to_16
            msg = migrate_to_16(self)
            report.append(msg)
            logger.info(msg)
        if self.plomino_version=="1.6":
            from migration.migration import migrate_to_161
            msg = migrate_to_161(self)
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
        
        # destroy the index
        self.manage_delObjects(self.getIndex().getId())
        msg = 'Old index removed'
        report.append(msg)
        logger.info(msg)
        
        #create new blank index
        index = PlominoIndex(FULLTEXT=self.FulltextIndex)
        self._setObject(index.getId(), index)
        self.getIndex().no_refresh = True
        msg = 'New index created'
        report.append(msg)
        logger.info(msg)
            
        #declare all the view formulas and columns index entries
        for v_obj in self.getViews():
            self.getIndex().createSelectionIndex('PlominoViewFormula_'+v_obj.getViewName())
            for c in v_obj.getColumns():
                v_obj.declareColumn(c.getColumnName(), c)
        for f_obj in self.getForms() :
            for f in f_obj.getFields() :
                if f.getToBeIndexed() :
                    self.getIndex().createFieldIndex(f.id, f.getFieldType())
        self.getIndex().no_refresh = False
        msg = 'Index structure initialized'
        report.append(msg)
        logger.info(msg)
        
        #reindex all the documents
        #getAllDocuments use the PlominoIndex. To get the documents to reindex, use portal catalog
        #for d in self.getAllDocuments():
        documents = [d.getObject() for d in self.portal_catalog.search({'portal_type' : ['PlominoDocument'], 'path': '/'.join(self.getPhysicalPath())})]
        msg = 'Existing documents: '+ str(len(documents))
        report.append(msg)
        logger.info(msg)
        count = 0
        for d in documents:
            try:
                #self.getIndex().indexDocument(d)
                d.save(onSaveEvent=False)
                count = count + 1
            except:
                pass
        msg = '%d documents re-indexed' % (count)
        report.append(msg)
        logger.info(msg)
        
        # update Plone workflow state
        workflow_tool = getToolByName(self, 'portal_workflow')
        wfs = workflow_tool.getWorkflowsFor(self)
        for wf in wfs:
            if not isinstance( wf, DCWorkflowDefinition ):
                continue
            wf.updateRoleMappingsFor( self )
        msg = 'Plone workflow update'
        report.append(msg)
        logger.info(msg)
        
        if REQUEST:
            self.writeMessageOnPage(MSG_SEPARATOR.join(report), REQUEST, "", False)
            REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign")
            
    security.declareProtected(DESIGN_PERMISSION, 'exportDesign')
    def exportDesign(self, REQUEST=None):
        """export design elements from current database to remote database
        """
        targetURL=REQUEST.get('targetURL')
        username=REQUEST.get('username')
        password=REQUEST.get('password')
        entire=REQUEST.get('entire')
        targettype=REQUEST.get('targettype')
        if entire=="Yes":
            xmlstring = self.exportDesignAsXML()
        else:
            designelements=REQUEST.get('designelements')
            if designelements:
                if type(designelements)==str:
                    designelements=[designelements]
                xmlstring = self.exportDesignAsXML(elementids=designelements)
        if targettype=="server":
            result=authenticateAndPostToURL(targetURL+"/importDesignFromXML", username, password, 'exportDesignAsXML.xml', xmlstring)
            REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign")
        else:
            REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
            REQUEST.RESPONSE.setHeader("Content-Disposition", "attachment; filename="+self.id+".xml")
            return xmlstring

            
    security.declareProtected(DESIGN_PERMISSION, 'importDesign')
    def importDesign(self, REQUEST=None):
        """import design elements in current database
        """
        submit_import=REQUEST.get('submit_import')
        sourceURL=REQUEST.get('sourceURL')
        username=REQUEST.get('username')
        password=REQUEST.get('password')
        entire=REQUEST.get('entire')
        sourcetype=REQUEST.get('sourcetype')
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
            else:
                fileToImport = REQUEST.get('sourceFile',None)
                if not fileToImport:
                    raise PlominoDesignException, 'file required'
                if not isinstance(fileToImport, FileUpload):
                    raise PlominoDesignException, 'unrecognized file uploaded'
                xmlstring=fileToImport.read()
        
            self.importDesignFromXML(xmlstring)
            no_refresh_documents = REQUEST.get('no_refresh_documents', 'No')
            if no_refresh_documents == 'No':
                self.refreshDB()
            REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign")
        else:
            REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign?username="+username+"&password="+password+"&sourceURL="+sourceURL)
              
    security.declareProtected(DESIGN_PERMISSION, 'getViewsList')
    def getViewsList(self):
        """return the database views ids in a string
        """
        views = self.getViews()
        ids = ""
        for v in views:
            ids=ids+v.id+"/"
        return ids
    
    security.declareProtected(DESIGN_PERMISSION, 'getFormsList')
    def getFormsList(self):
        """return the database forms ids in a string
        """
        forms = self.getForms()
        ids = ""
        for f in forms:
            ids=ids+f.id+"/"
        return ids

    security.declareProtected(DESIGN_PERMISSION, 'getAgentsList')
    def getAgentsList(self):
        """return the database agents ids in a string
        """
        agents = self.getAgents()
        ids = ""
        for a in agents:
            ids=ids+a.id+"/"
        return ids
            
    security.declareProtected(DESIGN_PERMISSION, 'getResourcesList')
    def getResourcesList(self):
        """return the database resources objects ids in a string
        """
        res = self.resources.objectIds()
        ids = ""
        for i in res:
            ids=ids+i+"/"
        return ids

    security.declareProtected(DESIGN_PERMISSION, 'getRemoteViews')
    def getRemoteViews(self, sourceURL, username, password):
        """get views ids list from remote database
        """
        views = authenticateAndLoadURL(sourceURL+"/getViewsList", username, password).read()
        ids = views.split('/')
        ids.pop()
        return ids

    security.declareProtected(DESIGN_PERMISSION, 'getRemoteForms')
    def getRemoteForms(self, sourceURL, username, password):
        """get forms ids list from remote database
        """
        forms = authenticateAndLoadURL(sourceURL+"/getFormsList", username, password).read()
        ids = forms.split('/')
        ids.pop()
        return ids
    
    security.declareProtected(DESIGN_PERMISSION, 'getRemoteAgents')
    def getRemoteAgents(self, sourceURL, username, password):
        """get agents ids list from remote database
        """
        agents = authenticateAndLoadURL(sourceURL+"/getAgentsList", username, password).read()
        ids = agents.split('/')
        ids.pop()
        return ids

    security.declareProtected(DESIGN_PERMISSION, 'getRemoteResources')
    def getRemoteResources(self, sourceURL, username, password):
        """get resources ids list from remote database
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
        str_formula=str_formula+"from Products.CMFPlomino.PlominoUtils import "+SAFE_UTILS+'\n'
        
        r = re.compile('#Plomino import (.+)[\r\n]')
        for i in r.findall(formula):
            scriptname=i.strip()
            try:
                script_code = str(self.resources._getOb(scriptname))
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
#        if self.debugMode:
#            logger.info('Evaluating '+script_id+' with context '+str(context))
        try:
            ps = self.getFormulaScript(script_id)
            if ps is None:
                ps = self.compileFormulaScript(script_id, formula_getter(), with_args)
                if self.debugMode and hasattr(ps, 'errors') and ps.errors:
                    logger.info('ps.errors : ' + str(ps.errors))
            contextual_ps=ps.__of__(context)
            result = None
            try:
                if with_args:
                    result = contextual_ps(*args)
                else:
                    result = contextual_ps()
                if self.debugMode and hasattr(contextual_ps, 'errors') and contextual_ps.errors:
                    logger.info('python errors at '+str(context)+' in '+script_id+': ' + str(contextual_ps.errors))
            except Exception, e:
                self.traceErr(e, context, script_id, formula_getter)
                raise
            return result
        
        except Exception, e:
            if self.debugMode:
                logger.info('runFormulaScript Exception evaluating '+script_id+' with context '+str(context)+ ':' + str(e))
    
    security.declarePrivate('traceErr')
    def traceErr(self, e, context, script_id, formula_getter):
        """trace errors from Scripts
        """
        if self.debugMode:
            #traceback
            f = StringIO()
            print_exc(limit=50, file=f)
            msg = str(f.getvalue())
            #code / value
            msg = msg + "Plomino formula error in "+script_id+": " + str(e)
            msg = msg + "\n   in code : \n" + formula_getter()
            msg = msg + "\n   with context : " + str(context)            
        else:
            msg = None
        
        if msg:
            logger.error(msg)
    
    security.declarePrivate('traceRenderingErr')
    def traceRenderingErr(self, e, context):
        """trace rendering errors
        """
        if self.debugMode:
            #traceback
            f = StringIO()
            print_exc(limit=50, file=f)
            msg = str(f.getvalue())
            #code / value
            msg = msg + "Plomino rendering error : " + str(e)
            msg = msg + "\n   with context : " + str(context)            
        else:
            msg = None
        
        if msg:
            logger.error(msg)
    
    security.declarePublic('callScriptMethod')
    def callScriptMethod(self, scriptname, methodname, *args):
        id="script_"+scriptname+"_"+methodname
        try:
            script_code = str(self.resources._getOb(scriptname))
        except:
            script_code = "#ALERT: "+scriptname+" not found in resources"
        formula=lambda:script_code+'\n\nreturn '+methodname+'(*args)'
        return self.runFormulaScript(id, self, formula, True, *args)
    
    security.declarePublic('writeMessageOnPage')
    def writeMessageOnPage(self, infoMsg, REQUEST, ifMsgEmpty = '', error = False):
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
            
            #if empty
            if (infoMsg == ''):
               infoMsg = ifMsgEmpty
                
            #split message   
            infoMsg = infoMsg.split(MSG_SEPARATOR)
            
            #display it
            for msg in infoMsg:
                if len(msg)==0:
                    mess = ifMsgEmpty
                else:
                    mess = msg
                if len(mess)>0:
                    plone_tools.addPortalMessage(mess, msgType, REQUEST)
                  
    security.declarePublic('getRenderingTemplate')
    def getRenderingTemplate(self, templatename):
        """
        """
        req = self.REQUEST
        try:
            rep=self.REQUEST['RESPONSE']
        except Exception:
            self.REQUEST['RESPONSE']=HTTPResponse()

        skin=self.portal_skins.cmfplomino_templates
        if hasattr(skin, templatename):
            pt = getattr(skin, templatename)
            if not pt.REQUEST.__class__.__name__=='HTTPRequest':
                # probably ZpCron context, so we create a fake HTTPRequest
                response = HTTPResponse(stdout=sys.stdout)
                env = {'SERVER_NAME':'fake_server',
                       'SERVER_PORT':'80',
                       'REQUEST_METHOD':'GET'}
                fakerequest = HTTPRequest(sys.stdin, env, response)
                pt.REQUEST = fakerequest
            return pt
        else:
            return None
          
    security.declareProtected(DESIGN_PERMISSION, 'exportDesignAsXML')
    def exportDesignAsXML(self, elementids=None, REQUEST=None):
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
        
        elements.sort()
        designNode = doc.createElement('design')
        
        # if export all design, export also database settings
        if elementids is None:
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
        s=StringIO()
        doc.writexml(s, encoding='utf-8')
        if REQUEST:
            REQUEST.RESPONSE.setHeader('content-type', "text/xml;charset=utf-8")
        return s.getvalue()
    
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
            type = obj.Type()
            node.setAttribute('type', type)
            title = obj.Title()
            node.setAttribute('title', title)
            schema = plomino_schemas[type]
            
        for f in schema.fields():
            fieldNode = xmldoc.createElement(f.getName())
            type = f.getType()
            fieldNode.setAttribute('type', type)
            v = f.get(obj)
            if v is not None:
                if type=="Products.Archetypes.Field.TextField":
                    text = xmldoc.createCDATASection(escape(str(f.getRaw(obj))))
                else:
                    text = xmldoc.createTextNode(str(f.get(obj)))
                fieldNode.appendChild(text)
            node.appendChild(fieldNode)
            
        # add AT standard extra attributes
        for extra in extra_schema_attributes:
            f = obj.Schema().getField(extra)
            if f is not None:
                fieldNode = xmldoc.createElement(extra)
                type = f.getType()
                fieldNode.setAttribute('type', type)
                v = f.get(obj)
                if v is not None:
                    if type=="Products.Archetypes.Field.TextField":
                        text = xmldoc.createCDATASection(escape(str(f.getRaw(obj))))
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
                    str_items = xmlrpclib.dumps((items,), allow_none=1, encoding='utf-8')
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
           str_UserRoles = xmlrpclib.dumps((obj.UserRoles,), allow_none=1, encoding='utf-8')
           dom_UserRoles = parseString(str_UserRoles)
           dom_UserRoles.firstChild.setAttribute('id', 'UserRoles')
           acl.appendChild(dom_UserRoles.documentElement)
           str_SpecificRights = xmlrpclib.dumps((obj.getSpecificRights(),), allow_none=1, encoding='utf-8')
           dom_SpecificRights = parseString(str_SpecificRights)
           dom_SpecificRights.firstChild.setAttribute('id', 'SpecificRights')
           acl.appendChild(dom_SpecificRights.documentElement)
           node.appendChild(acl)
           
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
        type = obj.meta_type
        node.setAttribute('type', type)
        node.setAttribute('title', obj.title)
        if type=="Page Template":
            data = xmldoc.createCDATASection(escape(obj.read()))
        else:
            node.setAttribute('contenttype', obj.getContentType())
            stream = obj.data
            if not hasattr(stream, "encode"):
                stream = stream.data
            data = xmldoc.createCDATASection(stream.encode('base64'))
        node.appendChild(data)
        return node
        
    security.declareProtected(DESIGN_PERMISSION, 'importDesignFromXML')
    def importDesignFromXML(self, xmlstring=None, REQUEST=None):
        """
        """
        logger.info("Start import")
        self.getIndex().no_refresh = True
        if REQUEST:
            f=REQUEST.get("file")
            xmlstring = f.read()
        xmldoc = parseString(xmlstring)
        design = xmldoc.getElementsByTagName("design")[0]
        e = design.firstChild
        while e is not None:
            name = str(e.nodeName)
            if name == 'dbsettings':
                logger.info("Import db settings")
                self.importDbSettingsFromXML(e)
            if name == 'element':
                logger.info("Import "+e.getAttribute('id'))
                self.importElementFromXML(self, e)
            if name == 'resource':
                logger.info("Import resource "+e.getAttribute('id'))
                self.importResourceFromXML(self.resources, e)
            e = e.nextSibling
        self.getIndex().no_refresh = False
        
    security.declareProtected(DESIGN_PERMISSION, 'importElementFromXML')
    def importElementFromXML(self, container, node):
        """
        """
        id = node.getAttribute('id')
        type = node.getAttribute('type')
        if id in container.objectIds():
            container.manage_delObjects([id])
        container.invokeFactory(type, id=id)
#        if not(hasattr(container, id)):
#            container.invokeFactory(type, id=id)
        obj = getattr(container, id)
        if obj.Type() == type:
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
                        self.importElementFromXML(obj, subchild)
                        subchild = subchild.nextSibling
                elif name == 'params':
                    # current object is a field, the params tag contains the
                    # specific settings
                    result, method = xmlrpclib.loads(node.toxml())
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
                        v = child.firstChild.data
                        if child.firstChild.nodeType == child.CDATA_SECTION_NODE:
                          v = unescape(v)
                        at_values[name] = v
                child = child.nextSibling
                
            if len(at_values) > 0:
                obj.processForm(REQUEST='dummy', values=at_values)
            if len(settings_values) > 0:
                adapt = obj.getSettings()
                for key in settings_values.keys():
                    setattr(adapt, key, settings_values[key])

    security.declareProtected(DESIGN_PERMISSION, 'importDbSettingsFromXML')
    def importDbSettingsFromXML(self, node):
        """
        """
        child = node.firstChild
        while child is not None:
            name = child.nodeName
            if name=='acl':
                anonymousaccessright = child.getAttribute('AnomynousAccessRight')
                self.AnomynousAccessRight = anonymousaccessright
                self.setPlominoPermissions("Anonymous", anonymousaccessright)
                authenticatedaccessright = child.getAttribute('AuthenticatedAccessRight')
                self.AuthenticatedAccessRight = authenticatedaccessright
                self.setPlominoPermissions("Authenticated", authenticatedaccessright)
                subchild = child.firstChild
                while subchild is not None:
                    result, method = xmlrpclib.loads(subchild.toxml())
                    type = subchild.getAttribute('id')
                    if type=="SpecificRights":
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
        type = node.getAttribute('type')
        if type == "Page Template":
            if not(hasattr(container, id)):
                obj = manage_addPageTemplate(container, id)
            else:
                obj = getattr(container, id)
            obj.title = node.getAttribute('title')
            obj.write(unescape(node.firstChild.data))
        else:
            if not(hasattr(container, id)):
                container.manage_addFile(id)
            obj = getattr(container, id)
            obj.meta_type = type
            obj.title = node.getAttribute('title')
            obj.update_data(node.firstChild.data.decode('base64'), content_type=node.getAttribute('contenttype'))

                
        

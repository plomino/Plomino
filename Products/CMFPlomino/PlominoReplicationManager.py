# -*- coding: utf-8 -*-
#
# File: PlominoReplicationManager.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Xavier PERROT  - Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'

from Products.CMFPlomino.config import *

from DateTime import DateTime
from cStringIO import StringIO
from Acquisition import *
from index.PlominoIndex import PlominoIndex
from HttpUtils import authenticateAndLoadURL, authenticateAndPostToURL
from Products.CMFCore.utils import getToolByName
from Products.CMFPlomino.exceptions import PlominoReplicationException
from Products.CMFPlomino.PlominoUtils import StringToDate
import re
from Persistence import Persistent
from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString
import xmlrpclib
import codecs
import os
import sys
import glob
import transaction

from ZPublisher.HTTPRequest import FileUpload
import csv

import logging
logger=logging.getLogger("Replication")

REMOTE_DOC_ID_SEPARATOR = '#'
REMOTE_DOC_DATE_SEPARATOR = '@'
REMOTE_DOC_IDS_HEADER = 'REMOTE_DOC_IDS'
REMOTE_URL_ADDED = 'url to replicate with'
REPLICATION_TYPES = {'push' : 'push', 'pull' : 'pull', 'pushpull' : 'push and pull'}
CONFLICT_RESOLUTION_TYPE = {'localwins' : 'local wins', 'remotewins' : 'remote wins', 'lastwins' : 'last wins'}
REPLICATION_MODES = {'view' : 'view', 'edit' : 'edit', 'add' : 'add'}
PASSWORD_DISPLAY_CAR = '*'
PLOMINO_IMPORT_SEPARATORS = {'semicolon (;)' : ';',
                             'comma (,)' : ',', 
                             'tabulation' : '\t', 
                             'white space' : ' ',
                             'end of line' : '\n',
                             'dash (-)' : '-'}

class PlominoReplicationManager(Persistent):
    """Plomino replication push/pull features
    """
    security = ClassSecurityInfo()

    # Methods
    security.declareProtected(EDIT_PERMISSION, 'manage_replications')
    def manage_replications(self, REQUEST=None):
        """replication form manager
        """
        #init
        infoMsg = ''
        error = False
        actionType = REQUEST.get('actionType', None)

        if actionType=='add':

            if not self.getReplicationEditingId():
                #new replication
                replication = self.newReplication()
                replication['mode'] = 'add'
                self.setReplication(replication)

        elif actionType=='cancel':

            #get the current replication editing
            replicationEditingId = self.getReplicationEditingId()
            #get replication
            replication = self.getReplication(replicationEditingId)
            if replication:
                if replication['mode'] == 'add':
                    self.deleteReplications([replicationEditingId])
                else:
                    replication['mode'] == 'view'
                    self.setReplication(replication)

        elif actionType=='save':

            #save params
            try:
                infoMsg = infoMsg + self.saveReplication(REQUEST) + MSG_SEPARATOR
            except PlominoReplicationException, e:
                infoMsg = infoMsg + 'error while saving : %s' % (e) + MSG_SEPARATOR 
                error = True    
        else:
            #actions on selection
            replicIds = REQUEST.get('selection', None)
            if replicIds:
                #check if simple url
                if type(replicIds)==str:
                    replicIds=[replicIds]

                #get the replications
                replications = self.getReplications()

                if actionType=='replicate':
                    #launch replications
                    for replicId in replicIds:

                        error = False
                        try:
                            infoMsg = self.replicate(replicId)
                        except PlominoReplicationException, e:
                            infoMsg = 'error while replicating ' + replicId + ' : %s' % (e) + MSG_SEPARATOR
                            error = True

                        #write message
                        self.writeMessageOnPage(infoMsg, REQUEST, error)

                    #no end message
                    error = False
                    infoMsg = ''

                elif actionType=='delete':
                    try:
                        infoMsg = self.deleteReplications(replicIds)
                    except PlominoReplicationException, e:
                        infoMsg = infoMsg + 'error while deleting all : %s' % (e) + MSG_SEPARATOR
                        error = True

                elif actionType=='edit':

                    #set mode to edit
                    if not self.getReplicationEditingId():
                        replicId = replicIds[0]
                        replication = self.getReplication(replicId)
                        replication['mode'] = 'edit'
                        self.setReplication(replication)

                else:
                    infoMsg = infoMsg + actionType + ' : unmanaged action' + MSG_SEPARATOR
                    error = True
            else:
                infoMsg = infoMsg + 'empty selection' + MSG_SEPARATOR
                error = True

        #write message
        self.writeMessageOnPage(infoMsg, REQUEST, error)

        #redirect
        REQUEST.RESPONSE.redirect(self.absolute_url()+'/DatabaseReplication')

    security.declareProtected(EDIT_PERMISSION, 'deleteReplications')
    def deleteReplications(self, replicationIds):
        """delete remoteUrl list        
        """
        #init
        infoMsg = ''
        error = False

        #replications
        replications = self.getReplications()

        for replicationId in replicationIds:
            try:
                replications.pop(replicationId)
                infoMsg = infoMsg + 'replication ' + str(replicationId) + ' deleted' + MSG_SEPARATOR
            except PlominoReplicationException, e:
                infoMsg = infoMsg + 'error while deletion of replication ' + replicationId + ' : %s' % (e) + MSG_SEPARATOR
                error = True

        if error:
            raise PlominoReplicationException, infoMsg

        #save replications
        self.setReplications(replications)

        return infoMsg

    security.declareProtected(EDIT_PERMISSION, 'saveReplication')
    def saveReplication(self, REQUEST=None):
        """save replication        
        """
        try:
            replication = self.buidReplicationFromRequest(REQUEST)
        except PlominoReplicationException, e:
            infoMsg = 'error while checking parameters : %s' % (e) + MSG_SEPARATOR
            raise PlominoReplicationException, infoMsg 

        #mode
        replication['mode'] = 'view'

        #save
        self.setReplication(replication)

        #result
        return "replication saved"

    security.declareProtected(EDIT_PERMISSION, 'replicate')
    def replicate(self, replicationId=None):
        """launch replication with just remote url passed
        """
        #check param
        if not replicationId:
            raise PlominoReplicationException, 'Replication id required'

        #get replication
        replication = self.getReplication(replicationId)
        if not replication:
            raise PlominoReplicationException, 'Unknown replication id'

        try:
            infoMsg = replication['remoteUrl'] + ' : ' + self.launchReplication(replication)
        except PlominoReplicationException, e:
            infoMsg = 'error while replicating ' + replication['remoteUrl'] + ' : %s' % (e) + MSG_SEPARATOR
            error = True

        #launch replication
        return infoMsg        

    security.declareProtected(EDIT_PERMISSION, 'launchReplication')
    def launchReplication(self, replication):
        """launch replication with params
        """

        #init
        infoMsg = ''
        error = False
        nbDocPushed = 0
        nbDocNotPushed = 0
        nbDocPulled = 0
        nbDocNotPulled = 0
        lastReplicationDatePush = None
        lastReplicationDatePull = None

        #check replication
        try:
            self.checkReplication(replication)
        except PlominoReplicationException, e:
            infoMsg = infoMsg + 'error while cheking parameters : %s' % (e) + MSG_SEPARATOR
            error = True

        #get remote documents ->  id:lastEditDate
        if not error:
            try:
                remoteDocuments = self.getRemoteDocuments(replication)
            except PlominoReplicationException, e:
                infoMsg = infoMsg + 'error while getting remote documents : %s' % (e) + MSG_SEPARATOR
                error = True

        #get local documents
        if not error:
            if replication.has_key('restricttoview'):
                restricttoview=replication['restricttoview']
                if restricttoview is not None and not(restricttoview==''):
                    try:
                        localDocuments = self.getView(restricttoview).getAllDocuments()
                    except PlominoReplicationException, e:
                        infoMsg = infoMsg + 'error while getting local documents : %s' % (e) + MSG_SEPARATOR
                        error = True
                else:
                    localDocuments = self.getAllDocuments()
            else:
                localDocuments = self.getAllDocuments()

        #flag replication begin on remote
        if not error:
            try:
                authenticateAndLoadURL(replication['remoteUrl'] + '/startReplicationRemote?RemoteUrl='+ self.absolute_url() +'&repType='+replication['repType'],replication['username'],replication['password'])
            except Exception, e:
                infoMsg = infoMsg + 'error while flagging replication on remote : %s' % (e) + MSG_SEPARATOR
                error = True

        #flag replication begin on local
        lastReplicationDatePull = self.getReplicationDate(replication['remoteUrl'],'pull')
        lastReplicationDatePush = self.getReplicationDate(replication['remoteUrl'],'push')
        self.startReplication(replication['remoteUrl'],replication['repType'])   


        #push documents
        if not error:
            if replication['repType']=='push' or replication['repType']=='pushpull':
                for doc in localDocuments:
                    #check if document can be exported
                    if self.exportableDoc(doc, remoteDocuments, lastReplicationDatePush, replication['whoWins']):
                        #export
                        try:
                            self.exportDocumentPush(doc, replication['remoteUrl'], replication['username'], replication['password'])
                            #infoMsg = infoMsg + 'document ' + doc.getId() + ' : push done' + MSG_SEPARATOR
                            nbDocPushed = nbDocPushed + 1
                        except PlominoReplicationException, e:
                            infoMsg = infoMsg + doc.getId() + ' push error : %s' % (e) + MSG_SEPARATOR
                            error = True
                    else:
                        #infoMsg = infoMsg + 'document ' + doc.getId() + ' : not pushed (not an error)' + MSG_SEPARATOR
                        nbDocNotPushed = nbDocNotPushed + 1

        #pull documents
        if not error:
            if replication['repType']=='pull' or replication['repType']=='pushpull':
                for docId in remoteDocuments:
                    #check if document can be imported
                    if self.importableDoc(docId, remoteDocuments[docId], lastReplicationDatePull, replication['whoWins']):
                        #import
                        try:
                            self.importDocumentPull(docId, replication['remoteUrl'], replication['username'], replication['password'])
                            #infoMsg = infoMsg + 'document ' + docId + ' : pull done' + MSG_SEPARATOR
                            nbDocPulled = nbDocPulled + 1
                        except PlominoReplicationException, e:                            
                            infoMsg = infoMsg + docId + ' pull error : %s' % (e) + MSG_SEPARATOR
                            error = True
                    else:
                        #infoMsg = infoMsg + 'document ' + docId + ' : not pulled (not an error)' + MSG_SEPARATOR
                        nbDocNotPulled = nbDocNotPulled + 1

        #add doc pushed number
        if nbDocPushed == 0:
            infoMsg = infoMsg + 'no document pushed '
        elif nbDocPushed == 1:
            infoMsg = infoMsg + '1 document pushed '
        else:
            infoMsg = infoMsg + str(nbDocPushed) + ' documents pushed '
        infoMsg = infoMsg + '(not pushed : ' + str(nbDocNotPushed) + '), ' 

        #add doc pulled number
        if nbDocPulled == 0:
            infoMsg = infoMsg + 'no document pulled '
        elif nbDocPulled == 1:
            infoMsg = infoMsg + '1 document pulled '
        else:
            infoMsg = infoMsg + str(nbDocPulled) + ' documents pulled '
        infoMsg = infoMsg + '(not pulled : ' + str(nbDocNotPulled) + ') '

        #errors
        if error:
            raise PlominoReplicationException, infoMsg

        return infoMsg

    security.declareProtected(EDIT_PERMISSION, 'getRemoteDocuments')
    def getRemoteDocuments(self, replication):
        """return the database documents
        """
        self.checkReplication(replication)

        #get remote documents
        url=replication['remoteUrl'] + '/getDocumentsIds'
        if replication.has_key('restricttoview'):
            restricttoview=replication['restricttoview']
            if restricttoview is not None and not(restricttoview==''):
                url=url+"?restricttoview="+restricttoview
        remoteDocumentsIds = authenticateAndLoadURL(url, replication['username'], replication['password']).read()

        #check if starts with REMOTE_DOC_IDS_HEADER
        if not remoteDocumentsIds.startswith(REMOTE_DOC_IDS_HEADER):
            raise PlominoReplicationException, "Connection error"

        #string ids
        docs = remoteDocumentsIds.split(REMOTE_DOC_ID_SEPARATOR)
        #remove header
        docs.pop(0)
        docs.pop()
        result={}
        for d in docs:
            (docid, modifdate) = d.split(REMOTE_DOC_DATE_SEPARATOR)
            result[docid]=DateTime(modifdate)
        return result

    security.declareProtected(READ_PERMISSION, 'getDocumentsIds')
    def getDocumentsIds(self, REQUEST=None):
        """return the database documents ids in a string
        """
        if REQUEST is not None:
            restricttoview=REQUEST.get('restricttoview',None)
            if restricttoview is not None:
                docs = self.getView(restricttoview).getAllDocuments()
            else:
                docs = self.getAllDocuments()
        else:
            docs = self.getAllDocuments()
        ids = REMOTE_DOC_IDS_HEADER+REMOTE_DOC_ID_SEPARATOR
        for d in docs:
            ids=ids+d.id+REMOTE_DOC_DATE_SEPARATOR+d.getLastModified(asString=True)+REMOTE_DOC_ID_SEPARATOR
        return ids

    security.declarePrivate('exportableDoc')
    def exportableDoc(self, doc, remoteDocuments, lastReplicationDate, whowins):
        """check if document can be exported to remoteUrl
        """
        #initialization
        res = False
        lastEditRemoteDocumentDate = None

        #search for doc in remoteDocuments
        if doc.id in remoteDocuments:
            lastEditRemoteDocumentDate = remoteDocuments[doc.id]

        #no remoteDoc found -> export 
        if not lastEditRemoteDocumentDate:
            res = True
        else:
            #zope modification time (plone modification time is not 
            #set while document modified thru script)
            #TODO : UTC
            lastEditDocumentDate = doc.getLastModified()
            #check dates
            if not lastReplicationDate:
                #no replication before
                res = (whowins == 'localwins') or ((whowins == 'lastwins') and (lastEditRemoteDocumentDate < lastEditDocumentDate))
            elif (lastEditDocumentDate > lastReplicationDate):
                #check conflict
                if (lastEditRemoteDocumentDate > lastReplicationDate):
                    res = (whowins == 'localwins') or ((whowins == 'lastwins') and (lastEditRemoteDocumentDate < lastEditDocumentDate))
                else:
                   res = True

        #result
        return res

    security.declarePrivate('exportDocumentPush')
    def exportDocumentPush(self, doc, remoteUrl, username, password):
        """ exports document to remoteUrl
            send object as a xml stream via HTTP multipart POST
        """
        id=doc.id
        xmlstring=self.exportAsXML(docids=[id])
        result = authenticateAndPostToURL(remoteUrl+"/importFromXML", username, password, '%s.%s' % (id, 'xml'), xmlstring.encode('utf-8'))

    security.declarePrivate('importableDoc')
    def importableDoc(self, docId, lastEditRemoteDocumentDate, lastReplicationDate, whowins):
        """check if document can be imported to remoteUrl
        """
        res = False

        #search for doc locally
        localDoc = self.getDocument(docId)
                
        #if no local doc found -> import 
        if localDoc is None:
            res = True 
        else:
            #zope modification time (plone modification time is not 
            #set while document modified thru script)
            #TODO : UTC
            lastEditDocumentDate = localDoc.getLastModified()

            #check dates
            if not lastReplicationDate:
                #no replication before
                res = (whowins == 'remotewins') or ((whowins == 'lastwins') and (lastEditRemoteDocumentDate > lastEditDocumentDate))
            elif (lastEditRemoteDocumentDate > lastReplicationDate):
                #check conflict
                if (lastEditDocumentDate > lastReplicationDate):
                    res = (whowins == 'remotewins') or ((whowins == 'lastwins') and (lastEditRemoteDocumentDate > lastEditDocumentDate))
                else:
                   res = True

        #result
        return res

    security.declarePrivate('importDocumentPull')
    def importDocumentPull(self, id, remoteUrl, username, password):
        """ imports document from remoteurl
            send object as a .zexp stream via HTTP multipart POST
        """
        f=authenticateAndLoadURL(remoteUrl+"/exportAsXML?docids="+id, username, password)
        self.importFromXML(xmlstring=f.read())

    security.declareProtected(EDIT_PERMISSION, 'getReplications')
    def getReplications(self):
        """returns a hash map representing replication history
        key : id
        value : replication hash map 
        """
        if not (hasattr(self,'replicationHistory')):
            self.replicationHistory = {}
        return self.replicationHistory

    security.declareProtected(EDIT_PERMISSION, 'setReplications')
    def setReplications(self, replications):
        """sets the replications hashmap 
        """
        self.replicationHistory = replications

        self.managePlominoCronTab()

        return self.replicationHistory

    security.declareProtected(EDIT_PERMISSION, 'getReplicationEditingId')
    def getReplicationEditingId(self):
        """returns the replication Id being edited
        """
        res = None
        replications = self.getReplications()
        for replicationId in replications:
            replication = self.getReplication(replicationId)
            if replication['mode'] == 'edit' or replication['mode'] == 'add':
                res = replicationId            
        return res

    security.declareProtected(EDIT_PERMISSION, 'getReplication')
    def getReplication(self, id):
        """returns the replication Id being edited
        """
        res = None
        #replication list
        replications = self.getReplications()
        #serach id
        searchId = str(id)
        if replications.has_key(searchId):
            res = replications[searchId]
        return res


    security.declarePrivate('setReplication')
    def setReplication(self, replication):
        """add the replication to the the replication hash map
        """
        #check replication
        replication = self.checkReplication(replication)
                        
        #replication list
        replications = self.getReplications()        

        replications[str(replication['id'])] = replication

        #set
        self.setReplications(replications)

    security.declareProtected(EDIT_PERMISSION, 'getReplicationsDates')
    def getReplicationsDates(self):
        """returns a hash map representing replication history
        key : url
        value : hash map {push, pull} 
        """
        if not (hasattr(self,'replicationsDates')):
            self.replicationsDates = {}
        return self.replicationsDates

    security.declareProtected(EDIT_PERMISSION, 'setReplicationsDates')
    def setReplicationsDates(self, repDates):
        """sets the replications hashmap 
        """
        self.replicationsDates = repDates
        return self.replicationsDates

    security.declarePrivate('getReplicationDate')
    def getReplicationDate(self, remoteUrl, replicationtype):
        """returns the replication date for id and type
        """
        #test params
        if not replicationtype in REPLICATION_TYPES.keys():
            raise PlominoReplicationException, 'Unknown replication type "' + replication['repType'] + '" (' + str(REPLICATION_TYPES.keys()) + ' expected)'

        #push pull not allowed
        if replicationtype == 'pushpull':
            raise PlominoReplicationException, 'Unable to return two dates for push pull. Choose push or pull.'

        #get hash map
        repDates = self.getReplicationsDates()

        #test if remoteurl is in
        if not repDates.has_key(remoteUrl):
            return None
        elif not repDates[remoteUrl].has_key(replicationtype):
            return None
        else:
            #return date
            return repDates[remoteUrl][replicationtype]

    security.declarePrivate('setReplicationDate')
    def setReplicationDate(self, remoteUrl, replicationtype, date):
        """sets the replication date for url and type
        """
        if not replicationtype in REPLICATION_TYPES.keys():
            raise PlominoReplicationException, 'Unknown replication type "' + replication['repType'] + '" (' + str(REPLICATION_TYPES.keys()) + ' expected)'

        #get hash map
        repDates = self.getReplicationsDates()

        #get url dates
        if repDates.has_key(remoteUrl):
            repDate = repDates[remoteUrl]
        else:
            repDate = {'push' : None, 'pull' : None}

        #add parameters
        if replicationtype == 'pushpull':
            repDate['push'] = date
            repDate['pull'] = date
        else:
            repDate[replicationtype] = date

        #add it
        repDates[remoteUrl] = repDate

        #set
        self.setReplicationsDates(repDates)

    security.declarePublic('displayDates')
    def displayDates(self, remoteUrl, context):
        """returns a string for displaying dates on template
        """
        #init
        res = ''

        #date formater
        util = getToolByName(context, 'translation_service')

        #dates
        datePush = self.getReplicationDate(remoteUrl, 'push')
        datePull = self.getReplicationDate(remoteUrl, 'pull')
        if datePush:
            datePush = util.ulocalized_time(datePush, True, context, domain='plonelocales')
            res = 'last push : ' + str(datePush) + ', '
        else: 
            res = 'no last push, '
        if datePull:
            datePull = util.ulocalized_time(datePull, True, context, domain='plonelocales')
            res = res + 'last pull : ' + str(datePull)
        else: 
            res = res + 'no last pull'    
        return res

    security.declarePrivate('setReplicationMode')
    def setReplicationMode(self, remoteId, mode):
        """sets the replication mode for url 
        """
        #test params
        if (mode != 'view') and (mode != 'edit') and (mode != 'add'):
            raise PlominoReplicationException, "Replication mode expected : view, edit or add"

        replicationEditingId = self.getReplicationEditingId()

        if (replicationEditingId) and (mode =='edit'):
            raise PlominoReplicationException, "Multiple replication editing forbidden"

        if (replicationEditingId) and (mode =='add'):
            raise PlominoReplicationException, "Unable to add, another replication already editing or adding"

        #current replication
        replication = self.getReplication(replicId)
        if not replication:
            raise PlominoReplicationException, "Replication unknown (%s)" % (str(replicId))

        #add parameter
        replication['mode'] = mode

        #set
        self.setReplication(replication)

    security.declarePublic('startReplicationRemote')
    def startReplicationRemote(self, REQUEST = None):
        """flags the begining of the transaction        
        """
        if not REQUEST is None:
            remoteUrl = REQUEST.get('RemoteUrl',None)
            repType = REQUEST.get('repType',None)
        else:
            remoteUrl = self.absolute_url()
            repType = 'push'

        self.startReplication(remoteUrl, repType)


    security.declarePublic('startReplication')
    def startReplication(self,remoteUrl, repType):
        """flags the beginning of the transaction        
        """
        now = DateTime().toZone('UTC')
        self.setReplicationDate(remoteUrl, repType, now)

    security.declarePublic('hideIt')
    def hideIt(self, it, hideCar = PASSWORD_DISPLAY_CAR):
        """return an hidden string to display
        """
        if it:
            count = len(it)
        else:
            count = 0
        return hideCar*count

    security.declarePublic('displayItNice')
    def displayItNice(self, it, hashMapName):
        """return a nice display title for type passed
        """
        res = None
        if hashMapName == 'REPLICATION_TYPES':
            hashmap = REPLICATION_TYPES
        elif hashMapName == 'CONFLICT_RESOLUTION_TYPE':
            hashmap = CONFLICT_RESOLUTION_TYPE
        elif hashMapName == 'REPLICATION_MODES':
            hashmap = REPLICATION_MODES
        else:
            hashmap = None
        if hashmap:
            if hashmap.has_key(it):
                res = hashmap[it]         
        return res

    security.declarePublic('resetReplications')
    def resetReplications(self):
        """reset the replication hashmap
        """
        self.replicationHistory = {}
        self.replicationsDates = {}

    security.declarePrivate('getNewId')
    def getNewId(self):
        """return a new id
        """
        res = 0
        replications = self.getReplications()
        for replicId in replications:
            if replicId > res:
                res = int(replicId)
        return res + 1

    security.declarePrivate('newReplication')
    def newReplication(self):
        """return an empty replication
        """
        return self.buildReplication(self.getNewId(),'', REMOTE_URL_ADDED, '', '', 'pull', 'localwins', False, '', '', 'view')

    security.declarePrivate('createReplication')
    def buidReplicationFromRequest(self, REQUEST = None):
        """returns a replication from request
        """
        if not REQUEST:
            raise PlominoReplicationException, "Request is required" 

        #params
        id = REQUEST.get('replicationId', None)
        name = REQUEST.get('name', None)
        remoteUrl = REQUEST.get('remoteUrl', None)
        username = REQUEST.get('username', None)
        password = REQUEST.get('password', None)
        repType = REQUEST.get('repType', None)
        whoWins = REQUEST.get('whoWins', None)
        scheduled = REQUEST.get('scheduled', False)
        restricttoview = REQUEST.get('restricttoview', None)
        cron = REQUEST.get('cron', None)
        mode = REQUEST.get('mode', None)

        return self.buildReplication(id, name, remoteUrl, username, password, repType, whoWins, scheduled, cron, restricttoview, mode)

    security.declarePrivate('createReplication')
    def buildReplication(self, id, name, remoteUrl, username, password, repType, whoWins, scheduled, cron, restricttoview, mode):
        """return an empty replication
        """
        return self.checkReplication({'id': id,
                                    'name' : name,
                                    'remoteUrl' : remoteUrl,
                                    'username' : username,
                                    'password' : password,
                                    'repType' : repType,
                                    'whoWins' : whoWins,
                                    'scheduled' : scheduled,
                                    'restricttoview':restricttoview,
                                    'cron':cron,
                                    'mode':mode})

    security.declarePrivate('checkReplication')
    def checkReplication(self, replication):
        """tests the replication params
        """
        try:
            if not replication:
                raise PlominoReplicationException, "replication empty"

            if not replication.has_key('id'):
                raise PlominoReplicationException, "id not set"
            if not replication.has_key('name'):
                raise PlominoReplicationException, "name not set"
            if not replication.has_key('remoteUrl'):
                raise PlominoReplicationException, "remote Url not set"
            if not replication.has_key('username'):
                raise PlominoReplicationException, "username not set"
            if not replication.has_key('password'):
                raise PlominoReplicationException, "password not set"
            if not replication.has_key('repType'):
                raise PlominoReplicationException, "replication type not set"
            if not replication.has_key('whoWins'):
                raise PlominoReplicationException, "conflict resolution type not set"
            if not replication.has_key('scheduled'):
                raise PlominoReplicationException, "scheduled type not set"
            if not replication.has_key('restricttoview'):
                raise PlominoReplicationException, "restricttoview not set"
            if not replication.has_key('cron'):
                raise PlominoReplicationException, "cron not set"
            if not replication.has_key('mode'):
                raise PlominoReplicationException, "mode not set"

            if replication['mode'] != 'add' and not replication['id']:
                raise PlominoReplicationException, "id required"

            #name not checked

            if not replication['remoteUrl']:
                raise PlominoReplicationException, 'Remote URL required'
            if replication['remoteUrl'] == self.absolute_url():
                raise PlominoReplicationException, 'Replication on current base forbidden'

            #user name and pwd not checked

            if not replication['repType'] in REPLICATION_TYPES.keys():
                raise PlominoReplicationException, 'Unknown replication type "' + replication['repType'] + '" (' + str(REPLICATION_TYPES.keys()) + ' expected)'

            if not replication['whoWins'] in CONFLICT_RESOLUTION_TYPE.keys():
                raise PlominoReplicationException, 'Unknown conflict resolution type "' + replication['whoWins'] + '" (' + str(CONFLICT_RESOLUTION_TYPE.keys()) + ' expected)'

            if replication['scheduled'] and (not replication['cron'] or len(replication['cron'])==0):
                raise PlominoReplicationException, 'Cron required if scheduled'

            if not replication['mode'] in REPLICATION_MODES.keys():
                raise PlominoReplicationException, 'Unknown replication mode "' + replication['mode'] + '" (' + str(REPLICATION_MODES.keys()) + ' expected)'

            return replication

        except PlominoReplicationException, e:
            raise PlominoReplicationException, 'replication has problem : %s' % (e)

    security.declareProtected(EDIT_PERMISSION, 'manage_importation')
    def manage_importation(self, REQUEST=None):
        """CSV import form manager
        """

        #init
        infoMsg = ''
        error = False
        actionType = REQUEST.get('actionType', None)

        #clear report
        self.resetReport()

        if actionType=='import':

            #get file name
            try:
                infoMsg = self.processImport(REQUEST)
            except PlominoReplicationException, e:
                infoMsg = infoMsg + 'error while importing : %s' % (e) + MSG_SEPARATOR 
                error = True

        elif actionType=='reset_report':
            self.resetReport()
        else:
            infoMsg = infoMsg + actionType + ' : unmanaged action' + MSG_SEPARATOR
            error = True

        #write message
        self.writeMessageOnPage(infoMsg, REQUEST, error)

        #redirect
        REQUEST.RESPONSE.redirect(self.absolute_url()+'/DatabaseReplication')

    security.declarePublic('getSeparators')
    def getSeparators(self):
        """returns the separator list
        """
        return PLOMINO_IMPORT_SEPARATORS

    security.declareProtected(EDIT_PERMISSION, 'processImport')
    def processImport(self, REQUEST):
        """
        Process the importation.
        """
        #result message
        infoMsg = ''

        if REQUEST:
            formName = REQUEST.get('formSelected',None)
            separatorName = REQUEST.get('separator',None)
            fileToImport = REQUEST.get('import_file',None)
            file_encoding = REQUEST.get('file_encoding', "utf-8")

        #form name
        if not formName:
            raise PlominoReplicationException, 'form required'

        #form obj
        formObj = self.getForm(formName)
        if not formObj:
            raise PlominoReplicationException, 'form ' + formName +  ' is unknown'

        #separator
        if not separatorName:
            raise PlominoReplicationException, 'separator required'
        separator = None
        if PLOMINO_IMPORT_SEPARATORS.has_key(separatorName):
            separator = PLOMINO_IMPORT_SEPARATORS[separatorName]

        #file
        if not fileToImport:
            raise PlominoReplicationException, 'file required'

        #check type
        if not isinstance(fileToImport, FileUpload):
            raise PlominoReplicationException, 'unrecognized file uploaded'

        #parse
        fileContent = self.parseFile(fileToImport, formName, separator, file_encoding)

        #import
        nbDocDone, nbDocFailed = self.importCsv(fileContent)

        #message
        infoMsg = fileToImport.filename + ' processed : ' + str(nbDocDone) + ' document(s) imported, ' + str(nbDocFailed) + ' document(s) failed.'
        return infoMsg

    security.declareProtected(EDIT_PERMISSION, 'processImport')
    def processImportAPI(self, formName, separator, fileToImport, file_encoding='utf-8'):
        """
        Process import API method.
        """

        #form name
        if not formName:
            raise PlominoReplicationException, 'form required'

        #form obj
        formObj = self.getForm(formName)
        if not formObj:
            raise PlominoReplicationException, 'form ' + formName +  ' is unknown'

        #separator
        if not separator:
            raise PlominoReplicationException, 'separator required'

        #file
        if not fileToImport:
            raise PlominoReplicationException, 'file required'

        #check type
        #if not isinstance(fileToImport, File):
         #   raise PlominoReplicationException, 'unrecognized file uploaded'

        #parse and import
        fileContent = self.parseFile(fileToImport, formName, separator, file_encoding)

        nbDocDone, nbDocFailed = self.importCsv(fileContent)        
        logger.info('Import processed : ' + str(nbDocDone) + ' document(s) imported, ' + str(nbDocFailed) + ' document(s) failed.')       

    security.declareProtected(EDIT_PERMISSION, 'parseFile')
    def parseFile(self, fileToImport, formName, separator, file_encoding='utf-8'):
        """
        """
        res= []
        try:
            if not fileToImport:
                raise PlominoReplicationException, 'file not set'

            if not separator:
                raise PlominoReplicationException, 'separator not set'

            #use the python cvs module
            reader = csv.DictReader(fileToImport.readlines(), delimiter=separator)

            #add the form name and copy reader values
            for line in reader:
                docInfos = {}

                #add form name
                docInfos['Form'] = formName

                #copy col values
                for col in line:
                    v = line[col]
                    if v is None:
                        v = u''
                    docInfos[col] = v.decode(file_encoding)

                #add doc infos to res
                res.append(docInfos)

            #result
            return res

        except PlominoReplicationException, e:
            raise PlominoReplicationException, 'error while parsing file (%s)' % (e)            

    security.declareProtected(EDIT_PERMISSION, 'importCsv')
    def importCsv(self, fileContent):
        """
        Import csv from content parsed.
        """

        #import
        nbDocDone = 0
        nbDocFailed = 0
        counter = 0

        i = 2
        logger.info("Documents count: %d" % len(fileContent))
        txn = transaction.get()
        for docInfos in fileContent:
            try:
                #create doc
                doc = self.createDocument()
                #fill it
                form = self.getForm(docInfos['Form'])
                form.readInputs(doc, docInfos, process_attachments=False, applyhidewhen=False)
                doc.setItem('Form', docInfos['Form'])
                #add items that don't correspond to any field 
                computedItems = doc.getItems()
                for info in docInfos:
                    if info not in computedItems:
                        v = docInfos[info]
                        if isinstance(v, str):
                            v.decode('utf-8')
                        doc.setItem(info, v)
                #save
                doc.save(creation=True, refresh_index=True)
                #count
                nbDocDone = nbDocDone + 1

            except PlominoReplicationException, e:
                nbDocFailed = nbDocFailed + 1
                self.addToReport(i, e, True)
            #next 
            i = i + 1
            counter = counter + 1
            if counter == 100:
                txn.savepoint(optimistic=True)
                counter = 0
                logger.info("%d documents imported successfully, %d errors(s) ...(still running)" % (nbDocDone, nbDocFailed))
        txn.commit()
        logger.info("Importation finished: %d documents imported successfully, %d document(s) not imported" % (nbDocDone, nbDocFailed)) 
        
        #result sent
        return (nbDocDone, nbDocFailed)

    security.declarePublic('getReport')
    def getReport(self):
        """returns last importation report
        """
        if not (hasattr(self,'importReport')):
            self.importReport = None
        return self.importReport

    security.declareProtected(EDIT_PERMISSION, 'resetReport')
    def resetReport(self):
        """clears report
        """
        self.importReport = None

    security.declareProtected(EDIT_PERMISSION, 'addToReport')
    def addToReport(self, lineNumber, infoMessage, error = False):
        """ adds entry to report
        """
        if not self.getReport():
            self.importReport = []
        if error:
            state = 'error'
        else:
            state = 'success'

        self.importReport.append({'line' : lineNumber, 'state' : state, 'infoMsg' : infoMessage})

    security.declareProtected(READ_PERMISSION, 'manage_exportAsXML')
    def manage_exportAsXML(self, REQUEST):
        """
        """
        restricttoview = REQUEST.get("restricttoview", "")
        if restricttoview != "":
            sourceview = self.getView(restricttoview)
            docids = [b.id for b in sourceview.getAllDocuments(getObject=False)]
        else:
            docids = None
        if REQUEST.get('targettype') == "file":
            REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
            if restricttoview:
                label = restricttoview
            else:
                label = "all"
            REQUEST.RESPONSE.setHeader("Content-Disposition", "attachment; filename=%s-%s-documents.xml" % (self.id, label))
        return self.exportAsXML(docids, REQUEST=REQUEST)

    security.declareProtected(READ_PERMISSION, 'exportAsXML')
    def exportAsXML(self, docids=None, targettype='file', targetfolder='', REQUEST=None):
        """ Export documents to XML.
        The targettype can be file or folder.
        """
        if REQUEST:
            targettype=REQUEST.get('targettype', 'file')
            targetfolder=REQUEST.get('targetfolder')
            str_docids=REQUEST.get("docids")
            if str_docids is not None:
                docids = str_docids.split("@")

        impl = getDOMImplementation()

        if docids is None:
            docs = self.getAllDocuments()
        else:
            docs = [self.getDocument(id) for id in docids]

        if targettype == 'file':
            xmldoc = impl.createDocument(None, "plominodatabase", None)
            root = xmldoc.documentElement
            root.setAttribute("id", self.id)

            for d in docs:
                node = self.exportDocumentAsXML(xmldoc, d)
                root.appendChild(node)

            if REQUEST is not None:
                REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
            return xmldoc.toxml()

        if targettype == 'folder':

            if REQUEST:
                targetfolder=REQUEST.get('targetfolder')

            exportpath = os.path.join(targetfolder,(self.id))
            if os.path.isdir(exportpath):
                # remove previous export
                for f in glob.glob(os.path.join(exportpath,"*.xml")):
                    os.remove(f)
            else:
                os.makedirs(exportpath)

            for d in docs:
                docfilepath = os.path.join(exportpath, (d.id+'.xml'))
                #DBG if os.path.exists(docfilepath):
                #DBG     logger.info("Skipping %s"%docfilepath)
                #DBG     continue
                logger.info("Exporting %s"%docfilepath)
                xmldoc = impl.createDocument(None, "plominodatabase", None)
                root = xmldoc.documentElement
                root.setAttribute("id", d.id)
                node = self.exportDocumentAsXML(xmldoc, d)
                root.appendChild(node)
                xmlstring = xmldoc.toxml()
                self.saveFile(docfilepath, xmlstring)

    @staticmethod
    def saveFile(path, content):
        fileobj = codecs.open(path, "w", "utf-8")
        fileobj.write(content)
        fileobj.close()

    security.declareProtected(READ_PERMISSION, 'exportDocumentAsXML')
    def exportDocumentAsXML(self, xmldoc, doc):
        """
        """
        node = xmldoc.createElement('document')
        node.setAttribute('id', doc.id)
        node.setAttribute('lastmodified', doc.getLastModified(asString=True))

        # export items
        str_items = xmlrpclib.dumps((doc.items,), allow_none=True)
        dom_items = parseString(str_items)
        node.appendChild(dom_items.documentElement)

        # export attached files
        for f in doc.getFilenames():
            attached_file = doc.getfile(f)
            fnode = xmldoc.createElement('attachment')
            fnode.setAttribute('id', f)
            fnode.setAttribute('contenttype', getattr(attached_file, 'content_type',''))
            data = xmldoc.createCDATASection(str(attached_file).encode('base64'))
            fnode.appendChild(data)
            node.appendChild(fnode)

        return node

    security.declareProtected(REMOVE_PERMISSION, 'manage_importFromXML')
    def manage_importFromXML(self, REQUEST):
        """
        """
        (imports, errors) = self.importFromXML(REQUEST=REQUEST)
        self.writeMessageOnPage("%d documents imported successfully, %d document(s) not imported" % (imports, errors), REQUEST, False)
        REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseReplication")

    security.declareProtected(REMOVE_PERMISSION, 'importFromXML')
    def importFromXML(self, xmlstring=None, sourcetype='sourceFile', file=None, from_folder=None, REQUEST=None):
        """ Import documents from XML.
        The sourcetype can be sourceFile or sourceFolder.
        """
        logger.info("Start documents import")
        self.setStatus("Importing documents (0%)")
        xml_files = []
        txn = transaction.get()
        if REQUEST:
            sourcetype = REQUEST.get('sourcetype', sourcetype)
        if sourcetype == 'sourceFile':
            if REQUEST:
                xml_files = [REQUEST.get("file")]
            else:
                xml_files = [xmlstring]
        elif sourcetype == 'folder':
            if REQUEST:
                from_folder=REQUEST.get("from_folder")
            xml_files = glob.glob(os.path.join(from_folder, '*.xml'))

        files_counter = 0
        errors = 0
        imports = 0

        for xml_file in xml_files:
            if isinstance(xml_file, basestring):
                xmlstring = xml_file
            else:
                if hasattr(xml_file, 'read'):
                    xmlstring = xml_file.read()
                else:
                    fileobj = codecs.open(xml_file, 'r', 'utf-8')
                    xmlstring = fileobj.read().encode('utf-8')

            xmldoc = parseString(xmlstring)
            documents = xmldoc.getElementsByTagName("document")
            total_docs = len(documents)
            if total_docs > 1:
                logger.info("Documents count: %d" % total_docs)
            docs_counter = 0
            files_counter = files_counter + 1

            for d in documents:
                docid = d.getAttribute('id')
                try:
                    if self.documents.has_key(docid):
                        self.documents._delOb(docid)
                    self.importDocumentFromXML(d)
                    imports = imports + 1
                except PlominoReplicationException, e:
                    logger.info('error while importing %s (%s)' % (docid, e))
                    errors = errors + 1
                docs_counter = docs_counter + 1
                if docs_counter == 100:
                    self.setStatus("Importing documents (%d%%)" % int(100*docs_counter/total_docs))
                    txn.savepoint(optimistic=True)
                    docs_counter = 0
                    logger.info("%d documents imported successfully, %d errors(s) ...(still running)" % (imports, errors))
            if files_counter == 100:
                self.setStatus("Importing documents (%s)" % files_counter)
                txn.savepoint(optimistic=True)
                files_counter = 0
                logger.info("%d documents imported successfully, %d errors(s) ...(still running)" % (imports, errors))

        self.setStatus("Ready")
        logger.info("Importation finished: %d documents imported successfully, %d document(s) not imported" % (imports, errors))
        txn.commit()

        return (imports, errors)

    security.declareProtected(CREATE_PERMISSION, 'importDocumentFromXML')
    def importDocumentFromXML(self, node):
        docid = node.getAttribute('id')
        lastmodified = DateTime(node.getAttribute('lastmodified'))
        pt = getToolByName(self, 'portal_types')
        pt.constructContent('PlominoDocument', self.documents, docid)
        #self.invokeFactory(type_name='PlominoDocument', id=docid)
        doc = self.documents.get(docid)

        # restore items
        itemnode = node.getElementsByTagName("params")[0]
        #result, method = xmlrpclib.loads(node.firstChild.toxml())
        result, method = xmlrpclib.loads(itemnode.toxml().encode('utf-8'))
        items = result[0]
        for k in items.keys():
            # convert xmlrpclib.DateTime into DateTime
            if items[k].__class__.__name__=='DateTime':
                items[k]=StringToDate(items[k].value[:19], format="%Y-%m-%dT%H:%M:%S")
        doc.items = items

        # restore files
        for fnode in node.getElementsByTagName("attachment"):
            filename = str(fnode.getAttribute('id'))
            contenttype = str(fnode.getAttribute('contenttype'))
            doc.setfile(fnode.firstChild.data.decode('base64'), filename=filename, overwrite=True, contenttype=contenttype)
        doc.save(onSaveEvent=False)
        doc.plomino_modification_time = lastmodified


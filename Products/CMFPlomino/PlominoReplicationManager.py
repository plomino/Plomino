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

# Standard
from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
import codecs
import csv
import datetime
import glob
import os
import transaction
import xmlrpclib

import logging
logger = logging.getLogger("Replication")

# Zope
from Acquisition import *
from AccessControl.requestmethod import postonly
from DateTime import DateTime
from Persistence import Persistent
from persistent.dict import PersistentDict
from ZPublisher.HTTPRequest import FileUpload

# CMF / Archetypes / Plone
from Products.CMFCore.utils import getToolByName

# Plomino
from Products.CMFPlomino.config import *
from HttpUtils import authenticateAndLoadURL
from HttpUtils import authenticateAndPostToURL
from Products.CMFPlomino.exceptions import PlominoReplicationException
from Products.CMFPlomino.PlominoUtils import StringToDate
from Products.CMFPlomino.PlominoUtils import escape_xml_illegal_chars
from Products.CMFPlomino.PlominoUtils import plomino_decimal

REMOTE_DOC_ID_SEPARATOR = '#'
REMOTE_DOC_DATE_SEPARATOR = '@'
REMOTE_DOC_IDS_HEADER = 'REMOTE_DOC_IDS'
REPLICATION_TYPES = {
        'push': 'push',
        'pull': 'pull',
        'pushpull': 'push and pull'}
CONFLICT_RESOLUTION_TYPE = {
        'localwins': 'local wins',
        'remotewins': 'remote wins',
        'lastwins': 'last wins'}
REPLICATION_MODES = {
        'view': 'view',
        'edit': 'edit',
        'add': 'add'}
PASSWORD_DISPLAY_CAR = '*'
PLOMINO_IMPORT_SEPARATORS = {
        'semicolon (;)': ';',
        'comma (,)': ',',
        'tabulation': '\t',
        'white space': ' ',
        'end of line': '\n',
        'dash (-)': '-'}

# From http://hg.tryton.org/trytond/file/7fefd5066a68/trytond/protocols/xmlrpc.py
# vvv FROM HERE
def dump_struct(self, value, write, escape=xmlrpclib.escape):
    converted_value = {}
    for k, v in value.items():
        if type(k) in (int, long):
            k = str(int(k))
        elif type(k) == float:
            k = repr(k)
        converted_value[k] = v
    return self.dump_struct(converted_value, write, escape=escape)

def end_struct(self, data):
    mark = self._marks.pop()
    # map structs to Python dictionaries
    dct = {}
    items = self._stack[mark:]
    for i in range(0, len(items), 2):
        dct[xmlrpclib._stringify(items[i])] = items[i + 1]
    if '__class__' in dct:
        if dct['__class__'] == 'Decimal':
            dct = plomino_decimal(dct['decimal'])
        # if dct['__class__'] == 'date':
        #     dct = datetime.date(dct['year'], dct['month'], dct['day'])
        # elif dct['__class__'] == 'time':
        #     dct = datetime.time(dct['hour'], dct['minute'], dct['second'])
        # elif dct['__class__'] == 'DateTime':
        #     dct = DateTime([dct[i] for i in ('year', 'month', 'day')])
    self._stack[mark:] = [dct]
    self._value = 0

def dump_decimal(self, value, write):
    value = {'__class__': 'Decimal',
        'decimal': str(value),
        }
    self.dump_struct(value, write)

# def dump_time(self, value, write):
#     value = {'__class__': 'time',
#         'hour': value.hour,
#         'minute': value.minute,
#         'second': value.second,
#         }
#     self.dump_struct(value, write)
# 
# def dump_date(self, value, write):
#     value = {'__class__': 'date',
#             'year': value.year,
#             'month': value.month,
#             'day': value.day,
#             }
#     self.dump_struct(value, write)
# 
# def dump_DateTime(self, value, write):
#     value = {'__class__': 'DateTime',
#             'year': value.year,
#             'month': value.month,
#             'day': value.day,
#             }
#     self.dump_struct(value, write)

# xmlrpclib.Marshaller.dispatch[datetime.date] = dump_date
# xmlrpclib.Marshaller.dispatch[datetime.time] = dump_time 
# xmlrpclib.Marshaller.dispatch[DateTime] = dump_DateTime
xmlrpclib.Marshaller.dispatch[plomino_decimal] = dump_decimal

xmlrpclib.Unmarshaller.dispatch['struct'] = end_struct
# ^^^ TO HERE


class PlominoReplicationManager(Persistent):
    """ Plomino replication push/pull features
    """
    security = ClassSecurityInfo()

    # Methods
    security.declareProtected(EDIT_PERMISSION, 'manage_replications')
    def manage_replications(self, REQUEST=None):
        """ Replication form manager
        """
        #init
        infoMsg = ''
        error = False
        actionType = REQUEST.get('actionType', None)

        if actionType == 'add':
            if not self.getReplicationEditingId():
                #new replication
                replication = self.newReplication()
                replication['mode'] = 'add'
                self.setReplication(replication)

        elif actionType == 'cancel':
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

        elif actionType == 'save':
            #save params
            try:
                infoMsg = (infoMsg +
                        self.saveReplication(REQUEST) +
                        MSG_SEPARATOR)
            except PlominoReplicationException, e:
                infoMsg = '%s error while saving: %s %s' % (
                        infoMsg,
                        e,
                        MSG_SEPARATOR)
                error = True    
        else:
            #actions on selection
            replicIds = REQUEST.get('selection', None)
            if replicIds:
                #check if simple url
                if type(replicIds) == str:
                    replicIds = [replicIds]

                # get the replications
                replications = self.getReplications()

                if actionType == 'replicate':
                    #launch replications
                    for replicId in replicIds:
                        error = False
                        try:
                            infoMsg = self.replicate(replicId)
                        except PlominoReplicationException, e:
                            infoMsg = 'error while replicating %s: %s%s' % (
                                    replicId,
                                    e,
                                    MSG_SEPARATOR)
                            error = True

                        #write message
                        self.writeMessageOnPage(infoMsg, REQUEST, error)

                    #no end message
                    error = False
                    infoMsg = ''

                elif actionType == 'delete':
                    try:
                        infoMsg = self.deleteReplications(replicIds)
                    except PlominoReplicationException, e:
                        infoMsg = '%s error while deleting all: %s %s' % (
                                infoMsg,
                                e,
                                MSG_SEPARATOR)
                        error = True

                elif actionType == 'edit':

                    #set mode to edit
                    if not self.getReplicationEditingId():
                        replicId = replicIds[0]
                        replication = self.getReplication(replicId)
                        replication['mode'] = 'edit'
                        self.setReplication(replication)

                else:
                    infoMsg = '%s %s: unmanaged action %s' % (
                            infoMsg,
                            actionType,
                            MSG_SEPARATOR)
                    error = True
            else:
                infoMsg = '%s empty selection %s' % (
                        infoMsg,
                        MSG_SEPARATOR)
                error = True

        #write message
        self.writeMessageOnPage(infoMsg, REQUEST, error)

        #redirect
        REQUEST.RESPONSE.redirect(self.absolute_url()+'/DatabaseReplication')

    security.declareProtected(EDIT_PERMISSION, 'deleteReplications')
    def deleteReplications(self, replicationIds):
        """ Delete remoteUrl list
        """
        infoMsg = ''
        error = False

        #replications
        replications = self.getReplications()

        for replicationId in replicationIds:
            try:
                replications.pop(replicationId)
                infoMsg = '%s replication %s deleted %s' % (
                        infoMsg,
                        str(replicationId),
                        MSG_SEPARATOR)
            except PlominoReplicationException, e:
                infoMsg = '%s error deleting replication %s: %s %s' % (
                        infoMsg,
                        replicationId,
                        e,
                        MSG_SEPARATOR)
                error = True

        if error:
            raise PlominoReplicationException, infoMsg

        #save replications
        self.setReplications(replications)

        return infoMsg

    security.declareProtected(EDIT_PERMISSION, 'saveReplication')
    def saveReplication(self, REQUEST=None):
        """ Save replication        
        """
        try:
            replication = self.buildReplicationFromRequest(REQUEST)
        except PlominoReplicationException, e:
            infoMsg = 'error while checking parameters: %s %s' % (
                    e,
                    MSG_SEPARATOR)
            raise PlominoReplicationException, infoMsg 

        replication['mode'] = 'view'
        self.setReplication(replication)
        return "replication saved"

    security.declareProtected(EDIT_PERMISSION, 'replicate')
    def replicate(self, replicationId=None):
        """ Launch replication with just remote URL passed
        """
        if not replicationId:
            raise PlominoReplicationException, 'Replication id required'

        replication = self.getReplication(replicationId)
        if not replication:
            raise PlominoReplicationException, 'Unknown replication id'

        try:
            infoMsg = '%s: %s' % (
                    replication['remoteUrl'],
                    self.launchReplication(replication))
        except PlominoReplicationException, e:
            infoMsg = 'error while replicating %s: %s %s' % (
                    replication['remoteUrl'],
                    e,
                    MSG_SEPARATOR)
            error = True

        return infoMsg        

    security.declareProtected(EDIT_PERMISSION, 'launchReplication')
    def launchReplication(self, replication):
        """ Launch replication with params
        """
        infoMsg = ''
        error = False
        nbDocPushed = 0
        nbDocNotPushed = 0
        nbDocPulled = 0
        nbDocNotPulled = 0
        lastReplicationDatePush = None
        lastReplicationDatePull = None

        try:
            self.checkReplication(replication)
        except PlominoReplicationException, e:
            infoMsg = '%s error while cheking parameters: %s %s' % (
                    infoMsg,
                    e,
                    MSG_SEPARATOR)
            error = True

        # get remote documents. id: lastEditDate
        if not error:
            try:
                remoteDocuments = self.getRemoteDocuments(replication)
            except PlominoReplicationException, e:
                infoMsg = '%serror while getting remote documents: %s%s' % (
                        infoMsg,
                        e,
                        MSG_SEPARATOR)
                error = True

        # get local documents
        if not error:
            if replication.has_key('restricttoview'):
                restricttoview = replication['restricttoview']
                if restricttoview:
                    try:
                        view = self.getView(restricttoview)
                        localDocuments = view.getAllDocuments()
                    except PlominoReplicationException, e:
                        infoMsg = '%serror while getting local documents: %s%s' % (
                                infoMsg,
                                e,
                                MSG_SEPARATOR)
                        error = True
                else:
                    localDocuments = self.getAllDocuments()
            else:
                localDocuments = self.getAllDocuments()

        # flag replication begin on remote
        if not error:
            try:
                authenticateAndLoadURL(
                        '%s/startReplicationRemote'
                        '?RemoteUrl=%s'
                        '&repType=%s' % (
                            replication['remoteUrl'],
                            self.absolute_url(),
                            replication['repType']),
                        replication['username'],
                        replication['password'])
            except Exception, e:
                infoMsg = '%serror while flagging replication on remote: %s%s' % (
                        infoMsg,
                        e,
                        MSG_SEPARATOR)
                error = True

        #flag replication begin on local
        lastReplicationDatePull = self.getReplicationDate(
                replication['remoteUrl'],
                'pull')
        lastReplicationDatePush = self.getReplicationDate(
                replication['remoteUrl'],
                'push')
        self.startReplication(
                replication['remoteUrl'],
                replication['repType'])   


        #push documents
        if not error:
            if replication['repType'] in ('push', 'pushpull'):
                for doc in localDocuments:
                    #check if document can be exported
                    if self.exportableDoc(
                            doc,
                            remoteDocuments,
                            lastReplicationDatePush,
                            replication['whoWins']):
                        #export
                        try:
                            self.exportDocumentPush(
                                    doc,
                                    replication['remoteUrl'],
                                    replication['username'],
                                    replication['password'])
                            #infoMsg = infoMsg + 'document ' + doc.getId() + ' : push done' + MSG_SEPARATOR
                            nbDocPushed = nbDocPushed + 1
                        except PlominoReplicationException, e:
                            infoMsg = '%s %s push error: %s%s' % (
                                    infoMsg,
                                    doc.getId(),
                                    e,
                                    MSG_SEPARATOR)
                            error = True
                    else:
                        #infoMsg = infoMsg + 'document ' + doc.getId() + ' : not pushed (not an error)' + MSG_SEPARATOR
                        nbDocNotPushed = nbDocNotPushed + 1

        #pull documents
        if not error:
            if replication['repType'] in ('pull', 'pushpull'):
                for docId in remoteDocuments:
                    #check if document can be imported
                    if self.importableDoc(
                            docId,
                            remoteDocuments[docId],
                            lastReplicationDatePull,
                            replication['whoWins']):
                        #import
                        try:
                            self.importDocumentPull(
                                    docId,
                                    replication['remoteUrl'],
                                    replication['username'],
                                    replication['password'])
                            #infoMsg = infoMsg + 'document ' + docId + ' : pull done' + MSG_SEPARATOR
                            nbDocPulled = nbDocPulled + 1
                        except PlominoReplicationException, e:                            
                            infoMsg = '%s%s pull error: %s%s' % (
                                    infoMsg, 
                                    docId,
                                    e,
                                    MSG_SEPARATOR)
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
        """ Return the database documents
        """
        self.checkReplication(replication)

        # get remote documents
        url = replication['remoteUrl'] + '/getDocumentsIds'
        if replication.has_key('restricttoview'):
            restricttoview=replication['restricttoview']
            if restricttoview:
                url = url + "?restricttoview=" + restricttoview
        remoteDocumentsIds = authenticateAndLoadURL(
                url,
                replication['username'],
                replication['password']).read()

        # check if starts with REMOTE_DOC_IDS_HEADER
        if not remoteDocumentsIds.startswith(REMOTE_DOC_IDS_HEADER):
            raise PlominoReplicationException, "Connection error"

        # string ids
        docs = remoteDocumentsIds.split(REMOTE_DOC_ID_SEPARATOR)
        # remove header
        docs.pop(0)
        docs.pop()
        result = {}
        for d in docs:
            (docid, modification_date) = d.split(REMOTE_DOC_DATE_SEPARATOR)
            result[docid] = DateTime(modification_date)
        return result

    security.declareProtected(READ_PERMISSION, 'getDocumentsIds')
    def getDocumentsIds(self, REQUEST=None):
        """ Return the database document ids in a string
        """
        if REQUEST:
            restricttoview = REQUEST.get('restricttoview', None)
            if restricttoview:
                docs = self.getView(restricttoview).getAllDocuments()
            else:
                docs = self.getAllDocuments()
        else:
            docs = self.getAllDocuments()
        ids = REMOTE_DOC_IDS_HEADER + REMOTE_DOC_ID_SEPARATOR
        for d in docs:
            ids = (ids +
                    d.id +
                    REMOTE_DOC_DATE_SEPARATOR +
                    d.getLastModified(asString=True) +
                    REMOTE_DOC_ID_SEPARATOR)
        return ids

    security.declarePrivate('exportableDoc')
    def exportableDoc(self, doc, remoteDocuments, lastReplicationDate, whowins):
        """ Check if document can be exported to remoteUrl
        """
        # initialization
        result = False
        lastEditRemoteDocumentDate = None

        # search for doc in remoteDocuments
        if doc.id in remoteDocuments:
            lastEditRemoteDocumentDate = remoteDocuments[doc.id]

        # no remoteDoc found -> export 
        if not lastEditRemoteDocumentDate:
            result = True
        else:
            # Zope modification time (Plone modification time is not 
            # set while document modified via script)
            # TODO: UTC
            lastEditDocumentDate = doc.getLastModified()
            # check dates
            if not lastReplicationDate:
                # no replication before
                result = (whowins == 'localwins') or (
                        (whowins == 'lastwins') and 
                        (lastEditRemoteDocumentDate < lastEditDocumentDate)
                        )
            elif (lastEditDocumentDate > lastReplicationDate):
                #check conflict
                if (lastEditRemoteDocumentDate > lastReplicationDate):
                    result = (whowins == 'localwins') or (
                            (whowins == 'lastwins') and 
                            (lastEditRemoteDocumentDate < lastEditDocumentDate)
                            )
                else:
                   result = True

        return result

    security.declarePrivate('exportDocumentPush')
    def exportDocumentPush(self, doc, remoteUrl, username, password):
        """ Exports document to remoteUrl.
            Send object as a XML stream via HTTP multipart POST.
        """
        i = doc.id
        xmlstring = self.exportAsXML(docids=[i])
        result = authenticateAndPostToURL(
                remoteUrl+"/importFromXML",
                username,
                password,
                '%s.xml' % i,  # filename
                xmlstring.encode('utf-8')  # content
                )

    security.declarePrivate('importableDoc')
    def importableDoc(self, docId, lastEditRemoteDocumentDate, lastReplicationDate, whowins):
        """ Check if document can be imported to remoteUrl
        """
        result = False

        # search for doc locally
        localDoc = self.getDocument(docId)
                
        # if no local doc found -> import 
        if not localDoc:
            result = True 
        else:
            # Zope modification time (Plone modification time is not 
            # set while document modified via script)
            # TODO: UTC
            lastEditDocumentDate = localDoc.getLastModified()

            #check dates
            if not lastReplicationDate:
                #no replication before
                result = (whowins == 'remotewins') or (
                        (whowins == 'lastwins') and
                        (lastEditRemoteDocumentDate > lastEditDocumentDate)
                        )
            elif (lastEditRemoteDocumentDate > lastReplicationDate):
                #check conflict
                if (lastEditDocumentDate > lastReplicationDate):
                    result = (whowins == 'remotewins') or (
                            (whowins == 'lastwins') and 
                            (lastEditRemoteDocumentDate > lastEditDocumentDate)
                            )
                else:
                   result = True

        return result

    security.declarePrivate('importDocumentPull')
    def importDocumentPull(self, i, remoteUrl, username, password):
        """ Imports document from remoteurl.
            Send object as a .zexp stream via HTTP multipart POST
        """
        f = authenticateAndLoadURL(
                remoteUrl+"/exportAsXML?docids="+i,
                username,
                password)
        self.importFromXML(xmlstring=f.read())

    security.declareProtected(EDIT_PERMISSION, 'getReplications')
    def getReplications(self):
        """ Returns a hashmap representing replication history.
        key: id
        value: replication hash map 
        """
        if not hasattr(self,'replicationHistory'):
            self.replicationHistory = {}
        return self.replicationHistory

    security.declareProtected(EDIT_PERMISSION, 'setReplications')
    def setReplications(self, replications):
        """ Sets the replications hashmap.
        """
        self.replicationHistory = replications 
        return self.replicationHistory

    security.declareProtected(EDIT_PERMISSION, 'getReplicationEditingId')
    def getReplicationEditingId(self):
        """ Returns the replication id being edited.
        """
        result = None
        replications = self.getReplications()
        for i in replications:
            replication = self.getReplication(i)
            if replication['mode'] in ('edit', 'add'):
                result = i
        return result

    security.declareProtected(EDIT_PERMISSION, 'getReplication')
    def getReplication(self, search_id):
        """ Returns the replication being edited.
        """
        result = None
        replications = self.getReplications()
        search_id = str(search_id)
        if replications.has_key(search_id):
            result = replications[search_id]
        return result

    security.declarePrivate('setReplication')
    def setReplication(self, replication):
        """ Add the replication to the replication hashmap.
        """
        # Raises exception if check fails:
        replication = self.checkReplication(replication)
        replications = self.getReplications()        
        replications[str(replication['id'])] = replication
        self.setReplications(replications)

    security.declareProtected(EDIT_PERMISSION, 'getReplicationsDates')
    def getReplicationsDates(self):
        """ Returns a hashmap representing replication history.
        key: url
        value: hash map {push, pull} 
        """
        if not hasattr(self, 'replicationsDates'):
            self.replicationsDates = {}
        return self.replicationsDates

    security.declareProtected(EDIT_PERMISSION, 'setReplicationsDates')
    def setReplicationsDates(self, replication_dates):
        """ Sets the replications hashmap 
        """
        self.replicationsDates = replication_dates
        return self.replicationsDates

    security.declarePrivate('getReplicationDate')
    def getReplicationDate(self, remoteUrl, replicationtype):
        """ Returns the replication date for id and type
        """
        # test params
        if not replicationtype in REPLICATION_TYPES.keys():
            raise PlominoReplicationException, (
                    'Unknown replication type "%s" (%s expected)' % (
                        replication['repType'],
                        ', '.join(REPLICATION_TYPES.keys())))

        # pushpull not allowed
        if replicationtype == 'pushpull':
            raise PlominoReplicationException, (
                    'Unable to return two dates for push pull. '
                    'Choose push or pull.')

        # get hashmap
        replication_dates = self.getReplicationsDates()

        #test if remoteurl is in
        if not replication_dates.has_key(remoteUrl):
            return None
        elif not replication_dates[remoteUrl].has_key(replicationtype):
            return None
        else:
            #return date
            return replication_dates[remoteUrl][replicationtype]

    security.declarePrivate('setReplicationDate')
    def setReplicationDate(self, remoteUrl, replicationtype, date):
        """ Sets the replication date for URL and type
        """
        if not replicationtype in REPLICATION_TYPES.keys():
            raise PlominoReplicationException, (
                    'Unknown replication type "%s" (%s expected)' % (
                        replication['repType'],
                        ', '.join(REPLICATION_TYPES.keys())))

        # get hashmap
        replication_dates = self.getReplicationsDates()

        # get url dates
        if replication_dates.has_key(remoteUrl):
            repDate = replication_dates[remoteUrl]
        else:
            repDate = {'push': None, 'pull': None}

        # add parameters
        if replicationtype == 'pushpull':
            repDate['push'] = date
            repDate['pull'] = date
        else:
            repDate[replicationtype] = date

        replication_dates[remoteUrl] = repDate 
        self.setReplicationsDates(replication_dates)

    security.declarePublic('displayDates')
    def displayDates(self, remoteUrl, context):
        """ Returns a string for displaying dates on template
        """
        result = ''

        # date formatter
        translation_service = getToolByName(context, 'translation_service')

        #dates
        datePush = self.getReplicationDate(remoteUrl, 'push')
        datePull = self.getReplicationDate(remoteUrl, 'pull')
        if datePush:
            datePush = translation_service.ulocalized_time(
                    datePush, 
                    long_format=True,
                    context=context,
                    domain='plonelocales')
            result = 'last push : ' + str(datePush) + ', '
        else: 
            result = 'no last push, '
        if datePull:
            datePull = translation_service.ulocalized_time(
                    datePull,
                    long_format=True,
                    context=context,
                    domain='plonelocales')
            result = result + 'last pull : ' + str(datePull)
        else: 
            result = result + 'no last pull'    
        return result

    security.declarePrivate('setReplicationMode')
    def setReplicationMode(self, remoteId, mode):
        """ Sets the replication mode for URL 
        """
        # test params
        if mode not in ('view', 'edit', 'add'):
            raise PlominoReplicationException, (
                    "Replication mode expected : view, edit or add")

        replicationEditingId = self.getReplicationEditingId()
        if replicationEditingId and mode == 'edit':
            raise PlominoReplicationException, (
                    "Multiple replication editing forbidden")

        if replicationEditingId and mode =='add':
            raise PlominoReplicationException, (
                    "Unable to add, another replication already "
                    "being edited or added")

        # current replication
        replication = self.getReplication(replicId)
        if not replication:
            raise PlominoReplicationException, (
                    "Replication unknown (%s)" % replicId)

        replication['mode'] = mode
        self.setReplication(replication)

    security.declarePublic('startReplicationRemote')
    @postonly
    def startReplicationRemote(self, REQUEST=None):
        """ Flags the start of the transaction (remote).
        """
        if REQUEST:
            remoteUrl = REQUEST.get('RemoteUrl', None)
            repType = REQUEST.get('repType', None)
        else:
            remoteUrl = self.absolute_url()
            repType = 'push'
        self.startReplication(remoteUrl, repType)

    security.declarePublic('startReplication')
    def startReplication(self, remoteUrl, repType):
        """ Flags the start of the transaction (local).
        """
        now = DateTime().toZone('UTC')
        self.setReplicationDate(remoteUrl, repType, now)

    security.declarePublic('hideIt')
    def hideIt(self, hidden, mask=PASSWORD_DISPLAY_CAR):
        """ Return a hidden string to display
        """
        return mask * 12

    security.declarePublic('displayItNice')
    def displayItNice(self, key, hashmap_name):
        """ Return a nice display title for type passed.
        """
        result = None
        hashmap = {
            'REPLICATION_TYPES': REPLICATION_TYPES,
            'CONFLICT_RESOLUTION_TYPE': CONFLICT_RESOLUTION_TYPE,
            'REPLICATION_MODES': REPLICATION_MODES}.get(
                    hashmap_name, None)
        if hashmap:
            if hashmap.has_key(key):
                result = hashmap[key]         
        return result

    security.declarePublic('resetReplications')
    def resetReplications(self):
        """ Reset the replication hashmap
        """
        self.replicationHistory = {}
        self.replicationsDates = {}

    security.declarePrivate('getNewId')
    def getNewId(self):
        """ Return a new id
        """
        result = 0
        replications = self.getReplications()
        for r_id in replications:
            if r_id > result:
                result = int(r_id)
        return result + 1

    security.declarePrivate('newReplication')
    def newReplication(self):
        """ Return an empty replication
        """
        return self.buildReplication(
                self.getNewId(),
                '',  # name
                '',  # url
                '',  # username
                '',  # password
                'pull',
                'localwins',
                False,  # scheduled
                '',  # cron
                '',  # restricttoview
                'view')

    security.declarePrivate('createReplication')
    def buildReplicationFromRequest(self, REQUEST = None):
        """ Returns a replication from request
        """
        if not REQUEST:
            raise PlominoReplicationException, "Request is required" 

        #params
        i = REQUEST.get('replicationId', None)
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

        return self.buildReplication(i, name, remoteUrl, username, password,
                repType, whoWins, scheduled, cron, restricttoview, mode)

    security.declarePrivate('createReplication')
    def buildReplication(self, i, name, remoteUrl, username, password, repType, whoWins, scheduled, cron, restricttoview, mode):
        """ Return an empty replication
        """
        return self.checkReplication({
                    'id': i,
                    'name': name,
                    'remoteUrl': remoteUrl,
                    'username': username,
                    'password': password,
                    'repType': repType,
                    'whoWins': whoWins,
                    'scheduled': scheduled,
                    'restricttoview': restricttoview,
                    'cron': cron,
                    'mode': mode
                    })

    security.declarePrivate('checkReplication')
    def checkReplication(self, replication):
        """ Test the replication parameters.
        """
        errors = []
        if not replication:
            errors.append("Replication empty")
        if not replication.has_key('id'):
            errors.append("'id' not set")
        if not replication.has_key('name'):
            errors.append("'name' not set")
        if not replication.has_key('remoteUrl'):
            errors.append("'remoteUrl' not set.")
        elif replication['remoteUrl'] == self.absolute_url():
            errors.append('Replication to current base forbidden')
        if not replication.has_key('username'):
            errors.append("'username' not set")
        if not replication.has_key('password'):
            errors.append("'password' not set")
        #user name and pwd not checked
        if not replication.has_key('repType'):
            errors.append("'repType' (replication type) not set")
        elif not replication['repType'] in REPLICATION_TYPES.keys():
            errors.append('Unknown replication type: "%s" '
                    '(%s expected)' % (
                        replication['repType'],
                        ', '.join(REPLICATION_TYPES.keys())))
        if not replication.has_key('whoWins'):
            errors.append("'whoWins' (conflict resolution type) not set")
        elif not replication['whoWins'] in CONFLICT_RESOLUTION_TYPE.keys():
            errors.append('Unknown conflict resolution type: "%s" '
                    '(%s expected)' % (
                        replication['whoWins'],
                        ', '.join(CONFLICT_RESOLUTION_TYPE.keys())))
        if not replication.has_key('scheduled'):
            errors.append("'scheduled' type not set")
        elif replication.get('scheduled') and not replication.get('cron', None):
            errors.append('Cron required if scheduled')
        if not replication.has_key('restricttoview'):
            errors.append("'restricttoview' not set")
        if not replication.has_key('cron'):
            errors.append("'cron' not set")
        if not replication.has_key('mode'):
            errors.append("'mode' not set")
        if replication['mode'] != 'add' and not replication['id']:
            errors.append("'id' required when referring to "
                    "existing replication")
        if not replication['mode'] in REPLICATION_MODES.keys():
            errors.append('Unknown replication mode: "%s" '
                    '(%s expected)' % (
                        replication['mode'],
                        ', '.join(REPLICATION_MODES.keys())))
        if errors:
            raise PlominoReplicationException, (
                    'Replication configuration issues: %s' %
                    '\n'.join(errors))
        else:
            return replication

    security.declareProtected(EDIT_PERMISSION, 'manage_importation')
    def manage_importation(self, REQUEST=None):
        """ CSV import form manager.
        """
        error = False
        actionType = REQUEST.get('actionType', None)
        self.resetReport()

        if actionType == 'import':
            # get file name
            try:
                infoMsg = self.processImport(REQUEST)
            except PlominoReplicationException, e:
                infoMsg = 'error while importing: %s%s' % (
                        e, MSG_SEPARATOR)
                error = True
        elif actionType == 'reset_report':
            self.resetReport()
        else:
            infoMsg = '%s: unmanaged action%s' % (
                    actionType, MSG_SEPARATOR)
            error = True

        self.writeMessageOnPage(infoMsg, REQUEST, error)
        REQUEST.RESPONSE.redirect(self.absolute_url()+'/DatabaseReplication')

    security.declarePublic('getSeparators')
    def getSeparators(self):
        """ Returns the separator list
        """
        return PLOMINO_IMPORT_SEPARATORS

    security.declareProtected(EDIT_PERMISSION, 'processImport')
    @postonly
    def processImport(self, REQUEST):
        """ Process the importation.
        """
        if not REQUEST:
            return 'REQUEST required'

        formName = REQUEST.get('formSelected', None)
        separatorName = REQUEST.get('separator', None)
        fileToImport = REQUEST.get('import_file', None)
        file_encoding = REQUEST.get('file_encoding', "utf-8")

        # form name
        if not formName:
            raise PlominoReplicationException, 'form required'

        # form obj
        form = self.getForm(formName)
        if not form:
            raise PlominoReplicationException, (
                    "Form '%s' not found" % formName )

        # separator
        separator = None
        if PLOMINO_IMPORT_SEPARATORS.has_key(separatorName):
            separator = PLOMINO_IMPORT_SEPARATORS.get(separatorName, None)
        if not separator:
            raise PlominoReplicationException, 'separator not found'

        # file
        if not fileToImport:
            raise PlominoReplicationException, 'file required'

        # check type
        if not isinstance(fileToImport, FileUpload):
            raise PlominoReplicationException, 'unrecognized file uploaded'

        # parse
        fileContent = self.parseFile(
            fileToImport, formName, separator, file_encoding)

        nbDocDone, nbDocFailed = self.importCsv(fileContent)

        infoMsg = ("%s processed: %s document(s) imported, "
            "%s document(s) failed." % (
                fileToImport.filename,
                nbDocDone,
                nbDocFailed))

        return infoMsg

    security.declareProtected(EDIT_PERMISSION, 'processImport')
    def processImportAPI(self, formName, separator, fileToImport, file_encoding='utf-8'):
        """ Process import API method.
        """
        # form name
        if not formName:
            raise PlominoReplicationException, 'form required'

        # form obj
        formObj = self.getForm(formName)
        if not formObj:
            raise PlominoReplicationException, (
                'form %s not found' % formName)

        # separator
        if not separator:
            raise PlominoReplicationException, 'separator required'

        # file
        if not fileToImport:
            raise PlominoReplicationException, 'file required'

        # parse and import
        fileContent = self.parseFile(fileToImport, formName, separator,
                file_encoding)

        nbDocDone, nbDocFailed = self.importCsv(fileContent)        
        logger.info(
                'Import processed: %s document(s) imported, '
                '%s document(s) failed.' % (nbDocDone, nbDocFailed))

    security.declareProtected(EDIT_PERMISSION, 'parseFile')
    def parseFile(self, fileToImport, formName, separator, file_encoding='utf-8'):
        """ Read CSV file. 
        Assume that we have a header line. 
        Each line represents a document. Set `Form` to formName.
        """
        result = []
        try:
            if not fileToImport:
                raise PlominoReplicationException, 'file not set'

            if not separator:
                raise PlominoReplicationException, 'separator not set'

            # Use the python CSV module
            if not isinstance(fileToImport, basestring):
                fileToImport = fileToImport.readlines()
            reader = csv.DictReader(
                    fileToImport,
                    delimiter=separator)

            # Add the form name and copy reader values
            for line in reader:
                docInfos = {}

                # add form name
                docInfos['Form'] = formName

                # copy col values
                for col in line:
                    v = line[col]
                    if not v:
                        v = u''
                    docInfos[col] = v.decode(file_encoding)

                # add doc infos to result
                result.append(docInfos)

            return result

        except PlominoReplicationException, e:
            raise PlominoReplicationException, 'error while parsing file (%s)' % (e)            

    security.declareProtected(EDIT_PERMISSION, 'importCsv')
    def importCsv(self, fileContent):
        """ Import CSV from content parsed.
        """
        nbDocDone = 0
        nbDocFailed = 0
        counter = 0

        i = 2
        logger.info("Documents count: %d" % len(fileContent))
        txn = transaction.get()
        for docInfos in fileContent:
            try:
                # create doc
                doc = self.createDocument()
                # fill it
                form = self.getForm(docInfos['Form'])
                form.readInputs(
                        doc,
                        docInfos,
                        process_attachments=False,
                        applyhidewhen=False)
                doc.setItem('Form', docInfos['Form'])
                # add items that don't correspond to any field 
                computedItems = doc.getItems()
                for info in docInfos:
                    if info not in computedItems:
                        v = docInfos[info]
                        if isinstance(v, str):
                            v.decode('utf-8')
                        doc.setItem(info, v)
                doc.save(creation=True, refresh_index=True)
                # count
                nbDocDone = nbDocDone + 1

            except PlominoReplicationException, e:
                nbDocFailed = nbDocFailed + 1
                self.addToReport(i, e, True)

            # next 
            i = i + 1
            if not nbDocDone % 100:
                txn.savepoint(optimistic=True)
                logger.info(
                        "%d documents imported successfully, "
                        "%d errors(s) ...(still running)" % (
                            nbDocDone, nbDocFailed))
        txn.commit()
        logger.info(
                "Importation finished: %d documents imported successfully, "
                "%d document(s) not imported" % (nbDocDone, nbDocFailed)) 

        #result sent
        return (nbDocDone, nbDocFailed)

    security.declarePublic('getReport')
    def getReport(self):
        """ Returns last importation report
        """
        if not (hasattr(self, 'importReport')):
            self.importReport = None
        return self.importReport

    security.declareProtected(EDIT_PERMISSION, 'resetReport')
    def resetReport(self):
        """ Clears report
        """
        self.importReport = None

    security.declareProtected(EDIT_PERMISSION, 'addToReport')
    def addToReport(self, lineNumber, infoMessage, error=False):
        """ Adds entry to report
        """
        if not self.getReport():
            self.importReport = []
        if error:
            state = 'error'
        else:
            state = 'success'

        self.importReport.append({
                    'line': lineNumber,
                    'state': state,
                    'infoMsg': infoMessage})

    security.declareProtected(READ_PERMISSION, 'manage_exportAsXML')
    def manage_exportAsXML(self, REQUEST):
        """
        """
        restricttoview = REQUEST.get("restricttoview", "")
        if restricttoview:
            v = self.getView(restricttoview)
            docids = [b.id for b in v.getAllDocuments(getObject=False)]
        else:
            docids = None
        if REQUEST.get('targettype') == "file":
            REQUEST.RESPONSE.setHeader('content-type', 'text/xml')
            if restricttoview:
                label = restricttoview
            else:
                label = "all"
            REQUEST.RESPONSE.setHeader(
                    "Content-Disposition",
                    "attachment; filename=%s-%s-documents.xml" % (
                        self.id, label))
        return self.exportAsXML(docids, REQUEST=REQUEST)

    security.declareProtected(READ_PERMISSION, 'exportAsXML')
    def exportAsXML(self, docids=None, targettype='file', targetfolder='', REQUEST=None):
        """ Export documents to XML.
        The targettype can be file or folder.
        If supplied, the values on REQUEST override keyword parameters.
        """
        if REQUEST:
            targettype = REQUEST.get('targettype', 'file')
            targetfolder = REQUEST.get('targetfolder')
            str_docids = REQUEST.get("docids")
            if str_docids:
                docids = str_docids.split("@")

        if docids:
            docs = [self.getDocument(i) for i in docids]
        else:
            docs = self.getAllDocuments()

        dom = getDOMImplementation()
        if targettype == 'file':
            xmldoc = dom.createDocument(None, "plominodatabase", None)
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
                targetfolder = REQUEST.get('targetfolder')

            exportpath = os.path.join(targetfolder, self.id)
            if os.path.isdir(exportpath):
                # remove previous export
                for f in glob.glob(os.path.join(exportpath, "*.xml")):
                    os.remove(f)
            else:
                os.makedirs(exportpath)

            for d in docs:
                docfilepath = os.path.join(exportpath, (d.id + '.xml'))
                #DBG if os.path.exists(docfilepath):
                #DBG     logger.info("Skipping %s"%docfilepath)
                #DBG     continue
                logger.info("Exporting %s" % docfilepath)
                xmldoc = dom.createDocument(None, "plominodatabase", None)
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
        items = doc.items
        if type(items) is not dict:
            items = doc.items.data
        str_items = xmlrpclib.dumps((items,), allow_none=True)
        try:
            dom_items = parseString(str_items)
        except ExpatError:
            dom_items = parseString(escape_xml_illegal_chars(str_items))
        node.appendChild(dom_items.documentElement)

        # export attached files
        for f in doc.getFilenames():
            attached_file = doc.getfile(f)
            if not attached_file:
                continue
            fnode = xmldoc.createElement('attachment')
            fnode.setAttribute('id', f)
            fnode.setAttribute(
                    'contenttype',
                    getattr(attached_file, 'content_type',''))
            data = xmldoc.createCDATASection(
                    str(attached_file).encode('base64'))
            fnode.appendChild(data)
            node.appendChild(fnode)

        return node

    security.declareProtected(REMOVE_PERMISSION, 'manage_importFromXML')
    @postonly
    def manage_importFromXML(self, REQUEST):
        """
        """
        (imports, errors) = self.importFromXML(REQUEST=REQUEST)
        self.writeMessageOnPage(
                "%d documents imported successfully, "
                "%d document(s) not imported" % (
                    imports, errors),
                REQUEST, error=False)
        REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseReplication")

    security.declareProtected(REMOVE_PERMISSION, 'importFromXML')
    @postonly
    def importFromXML(self, xmlstring=None, sourcetype='sourceFile', from_file=None, from_folder=None, REQUEST=None):
        """ Import documents from XML.
        The sourcetype can be sourceFile or sourceFolder.
        """
        logger.info("Start documents import")
        self.setStatus("Importing documents (0%)")
        txn = transaction.get()
        xml_sources = []
        if xmlstring:
            xmlstring_arg = True
            xml_sources = [xmlstring]
        else:
            xmlstring_arg = False
            if REQUEST:
                sourcetype = REQUEST.get('sourcetype', sourcetype)
            if sourcetype == 'sourceFile':
                if REQUEST:
                    xml_sources = [REQUEST.get("file")]
                elif from_file:
                    xml_sources = [from_file]
            elif sourcetype == 'folder':
                if REQUEST:
                    from_folder = REQUEST.get("from_folder")
                xml_sources = glob.glob(os.path.join(from_folder, '*.xml'))

        files_counter = 0
        errors = 0
        imports = 0

        # xml_sources contains either:
        # - a string, or
        # - file objects and/or filenames.
        for source in xml_sources:
            if xmlstring_arg:
                xmlstring = source
            else:
                if hasattr(source, 'read'):
                    xmlstring = source.read()
                else:
                    fileobj = codecs.open(source, 'r', 'utf-8')
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
                    self.setStatus("Importing documents (%d%%)" % 
                            (100 * docs_counter / total_docs))
                    txn.savepoint(optimistic=True)
                    docs_counter = 0
                    logger.info("%d documents imported successfully, "
                            "%d errors(s) ... (still running)" % (
                                imports, errors))
            if files_counter == 100:
                self.setStatus("Importing documents (%s)" % files_counter)
                txn.savepoint(optimistic=True)
                files_counter = 0
                logger.info("%d documents imported successfully, "
                        "%d errors(s) ... (still running)" % (
                            imports, errors))

        self.setStatus("Ready")
        logger.info("Importation finished: "
                "%d documents imported successfully, "
                "%d document(s) not imported" % (imports, errors))
        txn.commit()

        return (imports, errors)

    security.declareProtected(CREATE_PERMISSION, 'importDocumentFromXML')
    def importDocumentFromXML(self, node):
        docid = node.getAttribute('id').encode('ascii')
        lastmodified = DateTime(node.getAttribute('lastmodified'))
        doc = self.createDocument(docid)

        # restore items
        itemnode = node.getElementsByTagName("params")[0]
        #result, method = xmlrpclib.loads(node.firstChild.toxml())
        result, method = xmlrpclib.loads(itemnode.toxml().encode('utf-8'))
        items = result[0]
        for k in items.keys():
            # convert xmlrpclib.DateTime into DateTime
            if items[k].__class__.__name__ == 'DateTime':
                items[k] = StringToDate(
                        items[k].value[:19],
                        format="%Y-%m-%dT%H:%M:%S")
        doc.items = PersistentDict(items)

        # restore files
        for fnode in node.getElementsByTagName("attachment"):
            filename = str(fnode.getAttribute('id'))
            contenttype = str(fnode.getAttribute('contenttype'))
            doc.setfile(
                    fnode.firstChild.data.decode('base64'),
                    filename=filename,
                    overwrite=True,
                    contenttype=contenttype)
        doc.save(onSaveEvent=False)
        doc.plomino_modification_time = lastmodified


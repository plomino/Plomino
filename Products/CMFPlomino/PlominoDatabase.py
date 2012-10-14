# -*- coding: utf-8 -*-
#
# File: PlominoDatabase.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'

# Standard
import Globals
import string

# Zope
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from OFS.Folder import *
from OFS.ObjectManager import ObjectManager
from zope.annotation.interfaces import IAnnotations
# 4.3 compatibility
try:
    from zope.container.contained import ObjectRemovedEvent
except ImportError:
    from zope.app.container.contained import ObjectRemovedEvent
from zope.component import queryUtility
from zope import event
from zope.interface import directlyProvides
from zope.interface import implements
import interfaces

# CMF
from Products.CMFCore.CMFBTreeFolder import manage_addCMFBTreeFolder
from Products.CMFCore.PortalFolder import PortalFolderBase as PortalFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

# Plone
from plone.memoize.interfaces import ICacheChooser
from Products.Archetypes.atapi import *
from Products.Archetypes.BaseObject import BaseObject
from Products.Archetypes.debug import deprecated
from Products.Archetypes.public import *
from Products.Archetypes.utils import make_uuid
from Products.ATContentTypes.content.folder import ATFolder
#from Products.BTreeFolder2.BTreeFolder2 import manage_addBTreeFolder
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs

# Plomino
from exceptions import PlominoCacheException
from exceptions import PlominoScriptException
from index.PlominoIndex import PlominoIndex
from PlominoAccessControl import PlominoAccessControl
from PlominoDesignManager import PlominoDesignManager
from PlominoDocument import addPlominoDocument
from PlominoReplicationManager import PlominoReplicationManager
from PlominoScheduler import PlominoScheduler
from Products.CMFPlomino.config import *
from Products.CMFPlomino.PlominoUtils import *

try:
    from plone.app.async.interfaces import IAsyncService
    import zc.async
    ASYNC = True
except:
    ASYNC = False

PLOMINO_REQUEST_CACHE_KEY = "plomino.cache"
##/code-section module-header

schema = Schema((

    TextField(
        name='AboutDescription',
        allowable_content_types=('text/html',),
        widget=RichWidget(
            label="About this database",
            description="Describe the database, its objectives, its targetted audience, etc...",
            label_msgid='CMFPlomino_label_AboutDescription',
            description_msgid='CMFPlomino_help_AboutDescription',
            i18n_domain='CMFPlomino',
        ),
        default_output_type="text/html",
    ),
    TextField(
        name='UsingDescription',
        allowable_content_types=('text/html',),
        widget=RichWidget(
            label="Using this database",
            description="Describe how to use the database",
            label_msgid='CMFPlomino_label_UsingDescription',
            description_msgid='CMFPlomino_help_UsingDescription',
            i18n_domain='CMFPlomino',
        ),
        default_output_type="text/html",
    ),
    BooleanField(
        name='IndexAttachments',
        default=False,
        widget=BooleanField._properties['widget'](
            label="Index file attachments",
            description="If enabled, files attached in File Attachments fields will be indexed. It might increase the index size.",
            label_msgid='CMFPlomino_label_IndexAttachments',
            description_msgid='CMFPlomino_help_IndexAttachments',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='FulltextIndex',
        default=True,
        widget=BooleanField._properties['widget'](
            label="Local full-text index",
            description="If enabled, documents are full-text indexed into the Plomino index.",
            label_msgid='CMFPlomino_label_FulltextIndex',
            description_msgid='CMFPlomino_help_FulltextIndex',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='IndexInPortal',
        default=False,
        widget=BooleanField._properties['widget'](
            label="Index documents in Plone portal",
            description="If enabled, documents are searchable in Plone search.",
            label_msgid='CMFPlomino_label_IndexInPortal',
            description_msgid='CMFPlomino_help_IndexInPortal',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='debugMode',
        default=False,
        widget=BooleanField._properties['widget'](
            label="Debug mode",
            description="If enabled, script and formula errors are logged.",
            label_msgid='CMFPlomino_label_debugMode',
            description_msgid='CMFPlomino_help_debugMode',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='StorageAttachments',
        default=False,
        widget=BooleanField._properties['widget'](
            label="Use File System Storage for attachments",
            description="File System Storage must be installed on the portal",
            label_msgid='CMFPlomino_label_StorageAttachments',
            description_msgid='CMFPlomino_help_StorageAttachments',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='CountDocuments',
        default=False,
        widget=BooleanField._properties['widget'](
            label="Count the number of documents",
            description="If enabled, count the number of documents for each view. Display might be slower.",
            description_msgid="CMFPlomino_help_ShowDocumentsNumbers",
            label_msgid="CMFPlomino_label_ShowDocumentsNumbers",
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='DateTimeFormat',
        default="%Y-%m-%d",
        widget=StringField._properties['widget'](
            label='Date/time format',
            description='Format example: %Y-%m-%d',
            label_msgid='CMFPlomino_label_DateTimeFormat',
            description_msgid="CMFPlomino_help_DateTimeFormat",
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='StartPage',
        widget=StringField._properties['widget'](
            label='Start page',
            description='Element to display instead of the regular database menu.',
            label_msgid='CMFPlomino_label_StartPage',
            description_msgid='CMFPlomino_help_StartPage',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='DoNotListUsers',
        default=False,
        widget=BooleanField._properties['widget'](
            label="Do not list portal users",
            description="If True, in ACL screen, users are entered using a free text field, if False, using a selection list. Use True when the amount of users is big.",
            description_msgid="CMFPlomino_help_DoNotListUsers",
            label_msgid="CMFPlomino_label_DoNotListUsers",
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='DoNotReindex',
        default=False,
        widget=BooleanField._properties['widget'](
            label="Do not re-index documents on design changes",
            description="If True, documents are not re-indexed automatically when views, columns or indexed fields are changed. Note: manual refresh db is then needed.",
            description_msgid="CMFPlomino_help_DoNotReindex",
            label_msgid="CMFPlomino_label_DoNotReindex",
            i18n_domain='CMFPlomino',
        ),
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoDatabase_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    getattr(PlominoAccessControl, 'schema', Schema(())).copy() + \
    getattr(PlominoDesignManager, 'schema', Schema(())).copy() + \
    getattr(PlominoReplicationManager, 'schema', Schema(())).copy() + \
    getattr(PlominoScheduler, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoDatabase(ATFolder, PlominoAccessControl, PlominoDesignManager, PlominoReplicationManager, PlominoScheduler):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoDatabase)

    meta_type = 'PlominoDatabase'
    _at_rename_after_creation = True

    schema = PlominoDatabase_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('__init__')
    def __init__(self,oid,**kw):
        """
        """
        ATFolder.__init__(self, oid, **kw)
        self.plomino_version = VERSION
        self.setStatus("Ready")
        PlominoAccessControl.__init__(self)
        #manage_addBTreeFolder(self, id='plomino_documents')
        manage_addCMFBTreeFolder(self, id='plomino_documents')
        directlyProvides(self.documents, IHideFromBreadcrumbs)

    @property
    def documents(self):
        # returns plomino_documents BTreeFolder
        # note: default to {} to avoid errors for db having version <1.7.5 not
        # refreshed yet
        return getattr(self, 'plomino_documents', {})

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        """DB initialization
        """
        self.initializeACL()
        index = PlominoIndex(FULLTEXT=self.FulltextIndex)
        self._setObject('plomino_index', index)
        resources = Folder('resources')
        resources.title='resources'
        self._setObject('resources', resources)
        scripts = Folder('scripts')
        scripts.title='scripts'
        self._setObject('scripts', scripts)

    def __bobo_traverse__(self, request, name):
        # TODO: replace with IPublishTraverse or/and ITraverse
        if hasattr(self, 'documents'):
            if self.documents.has_key(name):
                return aq_inner(getattr(self.documents, name)).__of__(self)
        return BaseObject.__bobo_traverse__(self, request, name)
    
    def allowedContentTypes(self):
        # Make sure PlominoDocument is hidden in Plone "Add..." menu
        # as getNotAddableTypes is not used anymore in Plone 4
        filterOut = ['PlominoDocument']
        types = PortalFolder.allowedContentTypes(self)
        return [ ctype for ctype in types if ctype.getId() not in filterOut ]

    security.declarePublic('getStatus')
    def getStatus(self):
        """return DB current status
        """
        return getattr(self, "plomino_status", "Ready")

    security.declarePublic('setStatus')
    def setStatus(self, status):
        """set DB current status
        """
        self.plomino_status = status

    security.declarePublic('checkBeforeOpenDatabase')
    def checkBeforeOpenDatabase(self):
        """check if custom start page
        """
        if self.checkUserPermission(READ_PERMISSION):
#            if hasattr(self, 'REQUEST') and not self.checkUserPermission(DESIGN_PERMISSION):
#                self.REQUEST["disable_border"]=True
            try:
                if self.StartPage:        
                    if hasattr(self, self.getStartPage()):
                        target = getattr(self, self.getStartPage())
                    return getattr(target, target.defaultView())()
                else:
                    return self.OpenDatabase()
            except:
                return self.OpenDatabase()
        else:
            raise Unauthorized, "You cannot read this content"

    security.declarePublic('getForm')
    def getForm(self, formname):
        """return a PlominoForm
        """
        obj = getattr(self, formname, None)
        if obj and obj.Type() == 'PlominoForm':
            return obj

    security.declarePublic('getForms')
    def getForms(self, sortbyid=False):
        """return the database forms list
        """
        form_list = self.objectValues(spec='PlominoForm')
        form_obj_list = [a for a in form_list]
        if sortbyid:
            form_obj_list.sort(key=lambda elt: elt.id.lower())
        else:
            form_obj_list.sort(key=lambda elt: elt.getPosition())
        return form_obj_list

    security.declarePublic('getView')
    def getView(self, viewname):
        """return a PlominoView
        """
        obj = getattr(self, viewname, None)
        if obj and obj.Type() == 'PlominoView':
            return obj

    security.declarePublic('getViews')
    def getViews(self, sortbyid=False):
        """return the database views list
        """
        view_list = self.objectValues(spec='PlominoView')
        view_obj_list = [a for a in view_list]
        if sortbyid:
            view_obj_list.sort(key=lambda elt: elt.id.lower())
        else:
            view_obj_list.sort(key=lambda elt: elt.getPosition())
        return view_obj_list

    security.declarePublic('getAgent')
    def getAgent(self, agentid):
        """ Return a PlominoAgent, or None.
        """
        obj = getattr(self, agentid, None)
        if obj and obj.Type() == 'PlominoAgent':
            return obj

    security.declarePublic('getAgents')
    def getAgents(self):
        """ Returns all the PlominoAgent objects stored in the database.
        """
        # Convert from LazyList to (sortable) plain list.
        agent_list = list(self.objectValues(spec='PlominoAgent'))
        agent_list.sort(key=lambda agent: agent.id.lower())
        return agent_list

    security.declareProtected(CREATE_PERMISSION, 'createDocument')
    def createDocument(self, docid=None):
        """ Invoke PlominoDocument factory.
        Returns a new empty document.
        """
        if not docid:
            docid = make_uuid()
        self.documents[docid] = addPlominoDocument(docid)
        doc = self.documents.get(docid)
        return doc

    security.declarePublic('getDocument')
    def getDocument(self, docid):
        """ Return a PlominoDocument, or None. 
        If ``docid`` contains a "/", assume it's a path not a docid.
        """
        if not docid:
            return None
        if "/" in docid:
            # let's assume it is a path
            docid = docid.split("/")[-1]
        return self.documents.get(docid)

    security.declareProtected(READ_PERMISSION, 'getParentDatabase')
    def getParentDatabase(self):
        """ Normally used via acquisition by Plomino formulas operating on
        documents, forms, etc.
        """
        obj = self
        while getattr(obj, 'meta_type', '') != 'PlominoDatabase':
            obj = obj.aq_parent
        return obj

    security.declareProtected(REMOVE_PERMISSION, 'deleteDocument')
    def deleteDocument(self, doc):
        """ Delete the document from database.
        """
        if not self.isCurrentUserAuthor(doc):
            raise Unauthorized, "You cannot delete this document."
        else:
            # execute the onDeleteDocument code of the form
            form = doc.getForm()
            if form:
                try:
                    self.runFormulaScript("form_"+form.id+"_ondelete", doc, form.onDeleteDocument)
                except PlominoScriptException, e:
                    e.reportError('Document has been deleted, but onDelete event failed.')

            self.getIndex().unindexDocument(doc)
            if self.getIndexInPortal():
                self.portal_catalog.uncatalog_object("/".join(self.getPhysicalPath() + (doc.id,)))
            event.notify(ObjectRemovedEvent(doc, self.documents, doc.id))
            self.documents._delOb(doc.id)

    security.declareProtected(REMOVE_PERMISSION, 'deleteDocuments')
    def deleteDocuments(self, ids=None, massive=True):
        """ Batch delete documents from database.
        If ``massive`` is True, the ``onDelete`` formula and index
        updating are not performed (use ``refreshDB`` to update).
        """
        if ids is None:
            ids=[doc.id for doc in self.getAllDocuments()]

        if massive:
            ObjectManager.manage_delObjects(self.documents, ids)
        else:
            for id in ids:
                try:
                    self.deleteDocument(self.getDocument(id))
                except:
                    # if insufficient access rights, we continue
                    pass

    security.declareProtected(REMOVE_PERMISSION, 'manage_deleteDocuments')
    def manage_deleteDocuments(self, REQUEST):
        """delete documents action
        """
        strids = REQUEST.get('deldocs', None)
        if strids is not None:
            ids = [i for i in strids.split('@') if i is not '']
            self.deleteDocuments(ids=ids, massive=False)
        REQUEST.RESPONSE.redirect('.')

    security.declarePublic('getIndex')
    def getIndex(self):
        """ Return the database index.
        """
        return getattr(self, 'plomino_index')

    security.declarePublic('getAllDocuments')
    def getAllDocuments(self, getObject=True):
        """ Return all the database documents.
        """
        if getObject == False:
            # XXX: TODO: Return brains
            pass
        return self.documents.values()

    security.declarePublic('isDocumentsCountEnabled')
    def isDocumentsCountEnabled(self):
        """
        """
        try :
            return self.CountDocuments
        except Exception :
            return False

    def getObjectPosition(self, id):
        """
        """
        if id in self.documents:
            # documents will not be ordered in site map
            return 0
        return ATFolder.getObjectPosition(self, id)

    def _cache(self):
        chooser = queryUtility(ICacheChooser)
        if chooser is None:
            return None
        return chooser(self.absolute_url_path())

    def getCache(self, key):
        """ get cached value in the cache provided by plone.memoize 
        """ 
        return self._cache().get(key)

    def setCache(self, key, value):
        """ set cached value in the cache provided by plone.memoize 
        """
        self._cache()[key] = value

    def cleanCache(self, key=None):
        """ invalidate the cache
        (if key is None, all cached values are cleaned)
        """
        cache = self._cache()
        if hasattr(cache, 'ramcache'):
            if key:
                cachekey = dict(key=cache._make_key(key))
            else:
                cachekey = None
            cache.ramcache.invalidate(self.absolute_url_path(), cachekey)
        else:
            # we are probably not using zope.ramcache
            raise PlominoCacheException, 'Cache cleaning not implemented'
        
    def getRequestCache(self, key):
        """ get cached value in an annotation on the current request
        Note: it will available within this request only, it will be destroyed
        once the request is terminated.
        """
        if not hasattr(self, 'REQUEST'):
            return None
        annotations = IAnnotations(self.REQUEST)
        cache = annotations.get(PLOMINO_REQUEST_CACHE_KEY)
        if cache:
            return cache.get(key)

    def setRequestCache(self, key, value):
        """ set cached value in an annotation on the current request 
        """
        if not hasattr(self, 'REQUEST'):
            return None
        annotations = IAnnotations(self.REQUEST)
        cache = annotations.get(PLOMINO_REQUEST_CACHE_KEY)
        if not cache:
            cache = annotations[PLOMINO_REQUEST_CACHE_KEY] = dict()
        cache[key] = value

registerType(PlominoDatabase, PROJECTNAME)
# end of class PlominoDatabase

##code-section module-footer #fill in your manual code here
##/code-section module-footer




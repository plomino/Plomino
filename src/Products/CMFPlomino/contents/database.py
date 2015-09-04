from AccessControl import ClassSecurityInfo, Unauthorized
from OFS.ObjectManager import ObjectManager
from plone.dexterity.content import Container
from plone.memoize.interfaces import ICacheChooser
from plone.supermodel import model
from Products.CMFCore.PortalFolder import PortalFolderBase as PortalFolder
import uuid
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import queryUtility
from zope.container.contained import ObjectRemovedEvent
from zope import event
from zope.interface import implements

from .. import _, config
from ..accesscontrol import AccessControl
from ..exceptions import PlominoCacheException, PlominoScriptException
from ..interfaces import IPlominoContext
from ..design import DesignManager
from ..document import addPlominoDocument

security = ClassSecurityInfo()


class IPlominoDatabase(model.Schema):
    """ Plomino database schema
    """

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
    )

    indexAttachments = schema.Bool(
        title=_('CMFPlomino_label_IndexAttachments',
            default="Index file attachments"),
        description=_('CMFPlomino_help_IndexAttachments',
            default="If enabled, files attached in File Attachment fields "
            "will be indexed. It might increase the index size."),
        default=False,
    )

    fulltextIndex = schema.Bool(
        title=_('CMFPlomino_label_FulltextIndex',
            default="Local full-text index"),
        description=_('CMFPlomino_help_FulltextIndex',
            default='If enabled, documents are full-text indexed in the '
            'Plomino index.'),
        default=True,
    )

    indexInPortal = schema.Bool(
        title=_('CMFPlomino_label_IndexInPortal',
            default="Index documents in Plone portal"),
        description=_('CMFPlomino_help_IndexInPortal',
            default="If enabled, documents are searchable in Plone search."),
        default=False,
    )

    debugMode = schema.Bool(
        title=_('CMFPlomino_label_debugMode', default="Debug mode"),
        description=_('CMFPlomino_help_debugMode', default="If enabled, script"
        " and formula errors are logged."),
        default=False,
    )

    datetime_format = schema.TextLine(
        title=_('CMFPlomino_label_DateTimeFormat', default="Date/time format"),
        description=_(
            "CMFPlomino_help_DateTimeFormat",
            default='Format example: %Y-%m-%d'),
        default=u"%Y-%m-%d",
        required=False,
    )

    start_page = schema.TextLine(
        title=_('CMFPlomino_label_StartPage', default="Start page"),
        description=_('CMFPlomino_help_StartPage',
            default="Element to display instead of the regular database "
            "menu."),
        required=False,
    )

    i18n = schema.TextLine(
        title=_('CMFPlomino_label_i18n', default="i18n domain"),
        description=_('CMFPlomino_help_i18n',
            default="i18n domain to use for Plomino internal translation"),
        required=False,
    )

    do_not_list_users = schema.Bool(
        title=_("CMFPlomino_label_DoNotListUsers",
            default="Do not list portal users"),
        description=_("CMFPlomino_help_DoNotListUsers",
            default='If True, in ACL screen, users are entered using a free '
            'text field, if False, using a selection list. Use True when the '
            'amount of users is large.'),
        default=False,
    )

    do_not_reindex = schema.Bool(
        title=_("CMFPlomino_label_DoNotReindex",
            default="Do not re-index documents on design changes"),
        description=_("CMFPlomino_help_DoNotReindex",
            default='If True, documents are not re-indexed automatically when '
            'views, columns or indexed fields are changed. Note: manual '
            'refresh db is then needed.'),
        default=False,
    )

    isDatabaseTemplate = schema.Bool(
        title=_("CMFPlomino_label_IsDatabaseTemplate",
            default="Use it as a template"),
        description=_("CMFPlomino_help_IsDatabaseTemplate",
            default="If True, the database design can be exported in a "
            "GenericSetup profile and can then be used as a template in "
            "any Plomino database."),
        default=False,
    )


class PlominoDatabase(Container, AccessControl, DesignManager):
    implements(IPlominoDatabase, IPlominoContext)

    @property
    def documents(self):
        return self.plomino_documents

    def allowedContentTypes(self):
        # Make sure PlominoDocument is hidden in Plone "Add..." menu
        filterOut = ['PlominoDocument']
        types = PortalFolder.allowedContentTypes(self)
        return [ctype for ctype in types if ctype.getId() not in filterOut]

    security.declarePublic('getStatus')

    def getStatus(self):
        """ Return DB current status
        """
        return getattr(self, "plomino_status", "Ready")

    security.declarePublic('setStatus')

    def setStatus(self, status):
        """ Set DB current status
        """
        self.plomino_status = status

    security.declarePublic('getForm')

    def getForm(self, formname):
        """ Return a PlominoForm
        """
        obj = getattr(self, formname, None)
        if obj and obj.__class__.__name__ == 'PlominoForm':
            return obj

    security.declarePublic('getForms')

    def getForms(self, sortbyid=True):
        """ Return the database forms list
        """
        form_list = [obj for obj in self.objectValues()
            if obj.__class__.__name__ == 'PlominoForm']
        if sortbyid:
            form_list.sort(key=lambda elt: elt.id.lower())
        else:
            form_list.sort(key=lambda elt: elt.getPosition())
        return form_list

    security.declarePublic('getView')

    def getView(self, viewname):
        """ Return a PlominoView
        """
        obj = getattr(self, viewname, None)
        if obj and obj.__class__.__name__ == 'PlominoView':
            return obj

    def getViews(self, sortbyid=True):
        """ Return the list of PlominoView instances in the database.
        """
        view_list = [obj for obj in self.objectValues()
            if obj.__class__.__name__ == 'PlominoView']
        if sortbyid:
            view_list.sort(key=lambda elt: elt.id.lower())
        else:
            view_list.sort(key=lambda elt: elt.getPosition())
        return view_list

    security.declarePublic('getAgent')

    def getAgent(self, agentid):
        """ Return a PlominoAgent, or None.
        """
        obj = getattr(self, agentid, None)
        if obj and obj.__class__.__name__ == 'PlominoAgent':
            return obj

    security.declarePublic('getAgents')

    def getAgents(self):
        """ Returns all the PlominoAgent objects stored in the database.
        """
        agent_list = [obj for obj in self.objectValues()
            if obj.__class__.__name__ == 'PlominoAgent']
        agent_list.sort(key=lambda agent: agent.id.lower())
        return agent_list

    security.declareProtected(config.CREATE_PERMISSION, 'createDocument')

    def createDocument(self, docid=None):
        """ Invoke PlominoDocument factory.
        Returns a new empty document.
        """
        if not docid:
            docid = str(uuid.uuid4())
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

    security.declareProtected(config.READ_PERMISSION, 'getParentDatabase')

    def getParentDatabase(self):
        """ Normally used via acquisition by Plomino formulas operating on
        documents, forms, etc.
        """
        obj = self
        while getattr(obj, 'portal_type', '') != 'PlominoDatabase':
            obj = obj.aq_parent
        return obj

    security.declareProtected(config.REMOVE_PERMISSION, 'deleteDocument')

    def deleteDocument(self, doc):
        """ Delete the document from database.
        """
        if not self.isCurrentUserAuthor(doc):
            if hasattr(self, 'REQUEST'):
                self.writeMessageOnPage("You cannot delete this document.",
                        self.REQUEST, error=False)
            raise Unauthorized("You cannot delete this document.")
        else:
            # execute the onDeleteDocument code of the form
            form = doc.getForm()
            if form:
                message = None
                try:
                    message = self.runFormulaScript(
                        config.SCRIPT_ID_DELIMITER.join(
                            ['form', form.id, 'ondelete']),
                        doc,
                        form.onDeleteDocument)
                except PlominoScriptException, e:
                    e.reportError('Document has been deleted, '
                            'but onDelete event failed.')
                if message:
                    # Abort deletion
                    if hasattr(self, 'REQUEST'):
                        doc.writeMessageOnPage(message, self.REQUEST, False)
                        self.REQUEST.RESPONSE.redirect(doc.absolute_url())
                    return None

            self.getIndex().unindexDocument(doc)
            if self.indexInPortal:
                self.portal_catalog.uncatalog_object(
                    "/".join(self.getPhysicalPath() + (doc.id,)))
            event.notify(ObjectRemovedEvent(doc, self.documents, doc.id))
            self.documents._delOb(doc.id)

    security.declareProtected(config.REMOVE_PERMISSION, 'deleteDocuments')

    def deleteDocuments(self, ids=None, massive=True):
        """ Batch delete documents from database.
        If ``massive`` is True, the ``onDelete`` formula and index
        updating are not performed (use ``refreshDB`` to update).
        """
        if ids is None:
            ids = [doc.id for doc in self.getAllDocuments()]

        if massive:
            ObjectManager.manage_delObjects(self.documents, ids)
        else:
            for id in ids:
                self.deleteDocument(self.getDocument(id))

    security.declareProtected(
        config.REMOVE_PERMISSION, 'manage_deleteDocuments')

    def manage_deleteDocuments(self, REQUEST):
        """ Delete documents action.
        """
        strids = REQUEST.get('deldocs', None)
        if strids is not None:
            ids = [i for i in strids.split('@') if i is not '']
            self.deleteDocuments(ids=ids, massive=False)  # Trigger events
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
        if getObject is False:
            # XXX: TODO: Return brains
            pass
        return self.documents.values()

    def _cache(self):
        chooser = queryUtility(ICacheChooser)
        if chooser is None:
            return None
        return chooser(self.absolute_url_path())

    def getCache(self, key):
        """ Get cached value in the cache provided by plone.memoize
        """
        return self._cache().get(key)

    def setCache(self, key, value):
        """ Set cached value in the cache provided by plone.memoize
        """
        self._cache()[key] = value

    def cleanCache(self, key=None):
        """ Invalidate the cache.

        If key is None, all cached values are cleared.
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
            raise PlominoCacheException('Cache cleaning not implemented')

    def getRequestCache(self, key):
        """ Get cached value in an annotation on the current request.

        Note: it will available within this request only,
        it will be destroyed once the request is terminated.
        """
        if not hasattr(self, 'REQUEST'):
            return None
        annotations = IAnnotations(self.REQUEST)
        cache = annotations.get(config.PLOMINO_REQUEST_CACHE_KEY)
        if cache:
            return cache.get(key)

    def setRequestCache(self, key, value):
        """ Set cached value in an annotation on the current request
        """
        if not hasattr(self, 'REQUEST'):
            return None
        annotations = IAnnotations(self.REQUEST)
        cache = annotations.get(config.PLOMINO_REQUEST_CACHE_KEY)
        if not cache:
            cache = annotations[config.PLOMINO_REQUEST_CACHE_KEY] = dict()
        cache[key] = value

    def cleanRequestCache(self, key=None):
        if not hasattr(self, 'REQUEST'):
            return None
        annotations = IAnnotations(self.REQUEST)
        if key:
            cache = annotations.get(config.PLOMINO_REQUEST_CACHE_KEY)
            del cache[key]
        else:
            del annotations[config.PLOMINO_REQUEST_CACHE_KEY]

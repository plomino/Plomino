from AccessControl import ClassSecurityInfo, Unauthorized
from OFS.ObjectManager import ObjectManager
from plone.app.z3cform.widget import SelectFieldWidget
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.memoize.interfaces import ICacheChooser
from plone.supermodel import directives as supermodel_directives
from plone.supermodel import model
from Products.CMFCore.PortalFolder import PortalFolderBase as PortalFolder
from Products.CMFCore.utils import getToolByName
import uuid
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import queryUtility
from zope.container.contained import ObjectRemovedEvent
from zope import event
from zope.interface import implements
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory
from z3c.form.browser.checkbox import SingleCheckBoxWidget
from z3c.form import widget
import zope.component

from .. import _, config
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from Products.CMFPlomino.accesscontrol_ import AccessControl
from Products.CMFPlomino.exceptions import PlominoCacheException, PlominoScriptException
from Products.CMFPlomino.interfaces import IPlominoContext
from Products.CMFPlomino.design import DesignManager
from Products.CMFPlomino.replication import ReplicationManager
from Products.CMFPlomino.document import addPlominoDocument
from zope.component import getAdapter
from Products.CMFPlone.interfaces import IUserGroupsSettingsSchema
from plone import api
from Acquisition import aq_inner
security = ClassSecurityInfo()


@provider(IContextAwareDefaultFactory)
def default_macros(obj):
    """Return all plomino databases that begins with 'macros' and '.'.

    Order in alphabetical order
    """
    db = obj
    values = ['.']
    if not db:
        return values

    current_values = get_databases(db)
    db_ids = current_values.by_token.keys()

    new_values = []
    got_macros = False
    for db_id in db_ids:
        if db_id in values:
            continue
        if db_id == 'macros':
            got_macros = True
            continue
        elif db_id.startswith('macros'):
            new_values.append(db_id)

    new_values.sort()

    if got_macros:
        new_values.append('macros')

    return values + new_values


class DoNotListUserCheckboxWidget(SingleCheckBoxWidget):

    def update(self):
        many_users = getAdapter(aq_inner(api.portal.get()), IUserGroupsSettingsSchema).many_users
        # Hide the field if Plone many_user setting is enabled
        if many_users:
            self.mode = 'hidden'
        else:
            self.mode = 'input'
        return super(SingleCheckBoxWidget,self).update()



class IPlominoDatabase(model.Schema):
    """ Plomino database schema
    """



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


    directives.widget('do_not_list_users',DoNotListUserCheckboxWidget)
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

    #TODO: proper vocabulary of all other db's in site. perhaps with UUID in
    # case they are renamed
    directives.widget('import_macros', SelectFieldWidget)
    import_macros = schema.List(
        title=_("CMFPlomino_label_include_macros_from",
            default="Import Macros"),
        description=_("CMFPlomino_help_include_macros_from",
            default="Databases to search for macros. Reorder to change search order."),
        unique=True,
        value_type=schema.Choice(vocabulary="Products.CMFPlomino.fields.vocabularies.get_databases"),
        defaultFactory=default_macros,
        required=False,
    )

    # ADVANCED - the defaults should be fine most of the time
    supermodel_directives.fieldset(
        'advanced',
        label=_(u'Advanced'),
        fields=(
            'indexAttachments',
            'fulltextIndex',
            'indexInPortal',
            'debugMode',
            'i18n',
            'do_not_list_users',
            'do_not_reindex',
            'isDatabaseTemplate',
        ),
    )




class PlominoDatabase(
        Container, AccessControl, DesignManager, ReplicationManager):
    implements(IPlominoDatabase, IPlominoContext)

    @property
    def documents(self):
        return self.plomino_documents

    @property
    def do_not_list_users(self):
        many_users = getAdapter(aq_inner(api.portal.get()), IUserGroupsSettingsSchema).many_users
        if many_users:
            return True
        else:
            if hasattr(self, '_do_not_list_users'):
                return self._do_not_list_users
            else:
                return False

    @do_not_list_users.setter
    def do_not_list_users(self, value):
        self._do_not_list_users = value

    def allowedContentTypes(self):
        # Make sure PlominoDocument is hidden in Plone "Add..." menu
        filterOut = ['PlominoDocument']
        types = PortalFolder.allowedContentTypes(self)
        return [ctype for ctype in types if ctype.getId() not in filterOut]

    def getImportMacros(self):
        if getattr(self, 'import_macros', None) is not None:
            return self.import_macros
        else:
            return default_macros(self)

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
        return view_list

    security.declarePublic('getAgent')

    def getAgent(self, agentid):
        """ Return a PlominoAgent, or None.
        """
        obj = getattr(self, agentid, None)
        if obj and obj.__class__.__name__ == 'PlominoAgent':
            return obj

    security.declarePublic('getAgents')

    def getAgents(self, sortbyid=True):
        """ Returns all the PlominoAgent objects stored in the database.
        """
        agent_list = [obj for obj in self.objectValues()
            if obj.__class__.__name__ == 'PlominoAgent']
        if sortbyid:
            agent_list.sort(key=lambda agent: agent.id.lower())
        return agent_list


    def getDesignElements(self, sortbyid=True):
        """ return agents, views and forms
        """
        element_list = [obj for obj in self.objectValues()
            if obj.__class__.__name__ in ['PlominoAgent','PlominoView','PlominoForm']]
        if sortbyid:
            element_list.sort(key=lambda x: x.id.lower())
        return element_list

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
            for id in ids:
                self.getIndex().unindexDocument(self.getDocument(id))
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
            self.deleteDocuments(ids=ids, massive=True)  # Trigger events
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
        return None

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


def get_databases(obj):
    """Return all plomino databases

    Using id as value and 'title (path)' as label,
    except current database as '.'
    """
    db = obj
    if not db:
        return []

    catalog = getToolByName(db, 'portal_catalog')
    results = catalog.searchResults({'portal_type': 'PlominoDatabase'})
    title = "{title} ({path})".format(title=db.Title(), path=".")
    vocab = [SimpleTerm(title=title, token=".", value=".")]
    path = '/'.join(db.getPhysicalPath())
    site_path = '/'.join(db.portal_url.getPortalObject().getPhysicalPath())
    ids = []

    for brain in results:
        brain_id = brain.id
        brain_path = brain.getPath()

        if brain_path == path:
            continue

        # brain_id has to be unique
        # drop any duplicate
        # user need to refer to the path to double check the db is the
        # right one
        if brain_id in ids:
            continue

        if brain_path.startswith(site_path):
            brain_path = brain_path[len(site_path):]
        title = "{title} ({path})".format(
            title=brain['Title'], path=brain_path)
        ids.append(brain_id)
        vocab.append(SimpleTerm(title=title, token=brain_id, value=brain_id))

    return SimpleVocabulary(vocab)




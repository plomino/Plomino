from AccessControl import ClassSecurityInfo
from plone.dexterity.content import Container
from plone.memoize.interfaces import ICacheChooser
from plone.supermodel import model
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import queryUtility
from zope.interface import implements

from .. import _, config
from ..accesscontrol import AccessControl
from ..exceptions import PlominoCacheException
from ..interfaces import IPlominoContext
from ..design import DesignManager

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

    datetime_format = schema.TextLine(
        title=_('CMFPlomino_label_DateTimeFormat', default="Date/time format"),
        description=_(
            "CMFPlomino_help_DateTimeFormat",
            default='Format example: %Y-%m-%d'),
        default=u"%Y-%m-%d",
        required=False,
    )

    debugMode = schema.Bool(
        title=_('CMFPlomino_label_debugMode', default="Debug mode"),
        description=_('CMFPlomino_help_debugMode', default="If enabled, script"
        " and formula errors are logged."),
        default=False,
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


class PlominoDatabase(Container, AccessControl, DesignManager):
    implements(IPlominoDatabase, IPlominoContext)

    security.declareProtected(config.READ_PERMISSION, 'getParentDatabase')

    def getParentDatabase(self):
        """ Normally used via acquisition by Plomino formulas operating on
        documents, forms, etc.
        """
        obj = self
        while getattr(obj, 'portal_type', '') != 'PlominoDatabase':
            obj = obj.aq_parent
        return obj

    def getViews(self, sortbyid=True):
        """ Return the list of PlominoView instances in the database.
        """
        view_list = [obj for obj in self.objectValues()
            if obj.__class__.__name__ == 'PlominoView']
        view_obj_list = [a for a in view_list]
        if sortbyid:
            view_obj_list.sort(key=lambda elt: elt.id.lower())
        else:
            view_obj_list.sort(key=lambda elt: elt.getPosition())
        return view_obj_list

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

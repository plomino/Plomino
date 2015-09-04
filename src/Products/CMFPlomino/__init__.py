# -*- coding: utf-8 -*-
"""Init and utils."""

from AccessControl.Permission import registerPermissions
from DateTime import DateTime
import decimal
from Globals import DevelopmentMode
from json import JSONDecoder, JSONEncoder
from jsonutil import jsonutil as json
from time import time
from plone.resource.interfaces import IResourceDirectory
from Products.CMFCore import utils as cmfutils
from Products.PythonScripts.Utility import allow_module
from zope.i18nmessageid import MessageFactory
from zope import component
from zope.interface import implements

import interfaces
from config import (
    ADD_DESIGN_PERMISSION,
    ADD_CONTENT_PERMISSION,
    READ_PERMISSION,
    EDIT_PERMISSION,
    CREATE_PERMISSION,
    REMOVE_PERMISSION,
    DESIGN_PERMISSION,
    ACL_PERMISSION,
    PLOMINO_RESOURCE_NAME,
)
from utils import StringToDate

_ = MessageFactory('Products.CMFPlomino')


# Override default JSONEncoder/JSONDecoder classes in jsonutil to handle
# dates:
def _extended_json_encoding(obj):
    if isinstance(obj, DateTime):
        return {'<datetime>': True, 'datetime': obj.ISO()}
    return json.dumps(obj)

json._default_encoder = JSONEncoder(
    skipkeys=False,
    ensure_ascii=True,
    check_circular=True,
    allow_nan=True,
    indent=None,
    separators=None,
    encoding='utf-8',
    default=_extended_json_encoding,
)


def _extended_json_decoding(dct):
    if '<datetime>' in dct:
        # 2013-10-18T20:35:18+07:00
        return StringToDate(dct['datetime'], format=None)
    return dct


json._default_decoder = JSONDecoder(
    encoding=None,
    object_hook=_extended_json_decoding,
    object_pairs_hook=None,
    parse_float=decimal.Decimal)


class PlominoCoreUtils:
    implements(interfaces.IPlominoUtils)

    module = "Products.CMFPlomino.utils"
    methods = [
        'Log',
        'DateToString',
        'StringToDate',
        'DateRange',
        'sendMail',
        'userFullname',
        'userInfo',
        'htmlencode',
        'Now',
        'normalizeString',
        'asList',
        'urlencode',
        'csv_to_array',
        'MissingValue',
        'open_url',
        'asUnicode',
        'array_to_csv',
        'isDocument',
        'cgi_escape',
        'json_dumps',
        'json_loads',
        'decimal',
        'actual_path',
        'actual_context',
        'is_email',
        'urlquote',
        'translate',
        'SCRIPT_ID_DELIMITER',
        'save_point',
    ]

component.provideUtility(PlominoCoreUtils, interfaces.IPlominoUtils)


def get_utils():
    utils = {}
    for plugin_utils in component.getUtilitiesFor(interfaces.IPlominoUtils):
        module = plugin_utils[1].module
        utils[module] = plugin_utils[1].methods
    return utils

allow_module("Products.CMFPlomino.utils")


class PlominoSafeDomains:
    implements(interfaces.IPlominoSafeDomains)

    # by default, there is no domains allowed
    # but we can provide a IPlominoSafeDomains utility to declare some
    domains = []

component.provideUtility(PlominoSafeDomains, interfaces.IPlominoSafeDomains)


def get_resource_directory():
    """Obtain the Plomino persistent resource directory, creating it if
    necessary.
    """
    persistentDirectory = component.queryUtility(
        IResourceDirectory, name="persistent")
    if not persistentDirectory:
        return None
    if PLOMINO_RESOURCE_NAME not in persistentDirectory:
        persistentDirectory.makeDirectory(PLOMINO_RESOURCE_NAME)

    return persistentDirectory[PLOMINO_RESOURCE_NAME]


component.provideUtility(PlominoSafeDomains, interfaces.IPlominoSafeDomains)


if DevelopmentMode:
    PROFILING = True

    class plomino_profiler:
        """ Decorator which helps to control what aspects to profile
        """
        def __init__(self, aspect=None):
            self.aspect = aspect

        def get_storage(self, context):
            storage = context.getCache("plomino.profiling")
            if not storage:
                storage = dict()
                context.setCache("plomino.profiling", storage)
            return storage

        def __call__(self, f):
            def newf(*args, **kwds):
                obj = args[0]
                request = getattr(obj, 'REQUEST', None)
                if request and self.aspect in request.cookies.get(
                    'plomino_profiler', ''
                ):
                    start = time()
                    f_result = f(*args, **kwds)
                    duration = 1000 * (time() - start)
                    if self.aspect == "formulas":
                        id = args[1]
                    else:
                        id = obj.id
                    profiling = self.get_storage(obj)
                    aspect_times = profiling.get(self.aspect, [])
                    aspect_times.append([id, duration])
                    profiling[self.aspect] = aspect_times
                    return f_result
                else:
                    return f(*args, **kwds)
            newf.__doc__ = f.__doc__
            return newf
else:
    PROFILING = False

    class plomino_profiler:
        """"Transparent decorator, as profiling is only available if
        Zope runs in debug mode
        """
        def __init__(self, aspect=None):
            self.aspect = aspect

        def __call__(self, f):
            def newf(*args, **kwds):
                return f(*args, **kwds)

            newf.__doc__ = f.__doc__
            return newf


def initialize(context):
    """ Initialize product (standard Zope hook)
    """
    registerPermissions([(ADD_DESIGN_PERMISSION, []),
                         (ADD_CONTENT_PERMISSION, []),
                         (READ_PERMISSION, []),
                         (EDIT_PERMISSION, []),
                         (CREATE_PERMISSION, []),
                         (REMOVE_PERMISSION, []),
                         (DESIGN_PERMISSION, []),
                         (ACL_PERMISSION, [])])
    from .document import PlominoDocument, addPlominoDocument

    all_content_types = (PlominoDocument,)
    all_constructors = (addPlominoDocument,)
    all_ftis = ({
        'meta_type': 'PlominoDocument',
        'allowed_content_types': [],
        'allow_discussion': 0,
        'global_allow': 0,
        'filter_content_types': 1,
    }, )

    cmfutils.ContentInit(
        'CMFPlomino Content',
        content_types=all_content_types,
        permission=ADD_CONTENT_PERMISSION,
        extra_constructors=all_constructors,
        fti=all_ftis,
    ).initialize(context)

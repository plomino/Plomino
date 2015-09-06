# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IPlominoLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IPlominoSafeDomains(Interface):
    """Marker interface for PlominoSafeDomains
    """


class IPlominoContext(Interface):
    """Marker interface for Plomino objects."""


class IPlominoDocument(Interface):
    """ Marker interface for .PlominoDocument.PlominoDocument
    """


class IPlominoUtils(Interface):
    """ Marker interface for PlominoUtils
    """

# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IProductsCmfplominoLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IPlominoSafeDomains(Interface):
    """Marker interface for PlominoSafeDomains
    """

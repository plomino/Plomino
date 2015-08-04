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


class IXMLImportExportSubscriber(Interface):
    """ Provides import/export to/from XML.
       Subscribers to IXMLExportEvent MUST implement this interface"""

    def __call__():
        """ Attaches an XML string representing custom exportable properties
           to the 'xml_strings' attribute of the event
        """

    def import_xml(xml_string):
        """ Applies information contained in XML string
        (as returned by __call__).
        """

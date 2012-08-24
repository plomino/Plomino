# -*- coding: utf-8 -*-

from zope.interface import Interface

class IPlominoDatabase(Interface):
    """Marker interface for .PlominoDatabase.PlominoDatabase
    """

class IPlominoAction(Interface):
    """Marker interface for .PlominoAction.PlominoAction
    """

class IPlominoForm(Interface):
    """Marker interface for .PlominoForm.PlominoForm
    """

class IPlominoField(Interface):
    """Marker interface for .PlominoField.PlominoField
    """

class IPlominoView(Interface):
    """Marker interface for .PlominoView.PlominoView
    """

class IPlominoColumn(Interface):
    """Marker interface for .PlominoColumn.PlominoColumn
    """

class IPlominoDocument(Interface):
    """Marker interface for .PlominoDocument.PlominoDocument
    """

class IPlominoHidewhen(Interface):
    """Marker interface for .PlominoHidewhen.PlominoHidewhen
    """

class IPlominoAgent(Interface):
    """Marker interface for .PlominoAgent.PlominoAgent
    """

class IPlominoUtils(Interface):
    """Marker interface for PlominoUtils
    """

class IPlominoCache(Interface):
    """Marker interface for PlominoCache
    """

class IXMLImportExport(Interface):
    "Provides import/export to/from XML"
    def export_xml():
        "Returns an XML string representing custom exportable properties"
    def import_xml(xml_string):
        "Applies information contained in xml string (as returned by export_xml)"
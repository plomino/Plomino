# -*- coding: utf-8 -*-
#
# File: PlominoAccessControl.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.CMFPlomino.config import *

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCatalog.Catalog import CatalogError

from Products.CMFPlone.UnicodeSplitter import CaseNormalizer
from Products.CMFPlone.UnicodeSplitter import Splitter
#from Products.ZCTextIndex.Lexicon import CaseNormalizer
#from Products.ZCTextIndex.Lexicon import Splitter
#from Products.ZCTextIndex.Lexicon import StopWordRemover
from Products.ZCTextIndex.ZCTextIndex import PLexicon

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject, SimpleRecord
from Products.CMFCore.utils import getToolByName

from Products.CMFPlomino.index.PlominoCatalog import PlominoCatalog
from Products.CMFPlomino.index.PlominoViewIndex import PlominoViewIndex
from Products.CMFPlomino.index.PlominoColumnIndex import PlominoColumnIndex
from Products.CMFPlomino.index.PlominoFileIndex import PlominoFileIndex

class PlominoIndex(UniqueObject, ZCatalog, ActionProviderBase):
    """Plomino index
    """
    security = ClassSecurityInfo()
   
    id = 'plomino_index'

    manage_options = ( ZCatalog.manage_options +
        ActionProviderBase.manage_options +
        ({ 'label' : 'Overview', 'action' : 'manage_overview' }
        ,
        ))

    # Methods

    security.declarePublic('__init__')
    def __init__(self, FULLTEXT = False):
        """
        """
        ZCatalog.__init__(self, self.getId())
        self._catalog = PlominoCatalog()
        # TODO: use TextindexNG3
        #lexicon = PLexicon('plaintext_lexicon', '', Splitter(), CaseNormalizer(), StopWordRemover())
        lexicon = PLexicon('plaintext_lexicon', '', Splitter(), CaseNormalizer())
        self._setObject('plaintext_lexicon', lexicon)
        self.no_refresh = False
        self.createFieldIndex('Form', 'SELECTION')
        if FULLTEXT:
            self.createFieldIndex('SearchableText', 'TEXT')

    security.declareProtected(READ_PERMISSION, 'getParentDatabase')
    def getParentDatabase(self):
        """
        """
        return self.getParentNode()

    security.declareProtected(DESIGN_PERMISSION, 'createIndex')
    def createIndex(self,fieldname):
        """
        """
        try:
            self._catalog.addIndex(fieldname,PlominoColumnIndex(fieldname))
            self.addColumn(fieldname)
        except CatalogError:
            # index already exists
            pass
        self.refresh()
        
    security.declareProtected(DESIGN_PERMISSION, 'createFieldIndex')
    def createFieldIndex(self,fieldname, fieldtype):
        """
        """
        try:
            #self.addIndex(fieldname, 'KeywordIndex')
            indextype=FIELD_TYPES[fieldtype][1]
            if indextype=='ZCTextIndex':
                plaintext_extra = SimpleRecord( lexicon_id='plaintext_lexicon', index_type='Okapi BM25 Rank')
                self.addIndex(fieldname, 'ZCTextIndex', plaintext_extra)
                if fieldtype=='ATTACHMENT' and self.getParentDatabase().getIndexAttachments():
                    self._catalog.addIndex('PlominoFiles_'+fieldname,PlominoFileIndex('PlominoFiles_'+fieldname, caller=self, extra=plaintext_extra))
                    #self.addIndex('PlominoFiles_'+fieldname, 'ZCTextIndex', plaintext_extra)
            else:
                self.addIndex(fieldname, indextype)
            self.addColumn(fieldname)
        except CatalogError:
            # index already exists
            pass
        self.refresh()
        
    security.declareProtected(DESIGN_PERMISSION, 'createSelectionIndex')
    def createSelectionIndex(self,fieldname):
        """
        """
        try:
            self._catalog.addIndex(fieldname,PlominoViewIndex(fieldname))
        except CatalogError:
            # index already exists
            pass
        self.refresh()

    security.declareProtected(DESIGN_PERMISSION, 'deleteIndex')
    def deleteIndex(self,fieldname):
        """
        """
        self.delIndex(fieldname)
        self.delColumn(fieldname)
        self.refresh()

    security.declareProtected(READ_PERMISSION, 'indexDocument')
    def indexDocument(self,doc):
        """
        """
        self.catalog_object(doc, "/".join(doc.getPhysicalPath()))

    security.declareProtected(READ_PERMISSION, 'unindexDocument')
    def unindexDocument(self,doc):
        """
        """
        self.uncatalog_object("/".join(doc.getPhysicalPath()))

    security.declarePublic('refresh')
    def refresh(self):
        """
        """
        if not self.no_refresh:
            self.refreshCatalog()

    security.declareProtected(READ_PERMISSION, 'dbsearch')
    def dbsearch(self,request,sortindex=None,reverse=0):
        """
        """
        return self.search(request, sortindex, reverse)

    security.declareProtected(READ_PERMISSION, 'getKeyUniqueValues')
    def getKeyUniqueValues(self,key):
        """
        """
        return self.uniqueValuesFor(key)

    security.declarePublic('convertFileToText')
    def convertFileToText(self, doc, field):
        """ (adapted from Plone3 ATContentTypes file class)
        """
        source   = ''
        mimetype = 'text/plain'
        encoding = 'utf-8'
        
        if hasattr(doc.getItem(field), 'keys'):
            files=doc.getItem(field)
            # stage 1: get the searchable text and convert it to utf8
            sp    = getToolByName(self, 'portal_properties').site_properties
            stEnc = getattr(sp, 'default_charset', 'utf-8')
        
            # get the file and try to convert it to utf8 text
            ptTool = getToolByName(self, 'portal_transforms')
            for filename in files.keys():
                f=doc.getfile(filename=filename)
                if f:
                    mt = files[filename]
                    try:
                        result = ptTool.convertTo('text/plain', str(f), mimetype=mt)
                        if result:
                            data = result.getData()
                        else:
                            data = ''
                    except TransformException:
                        data = ''
                    source+=data

        return source




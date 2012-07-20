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

import logging
logger = logging.getLogger('Plomino')

from AccessControl import ClassSecurityInfo
from Products.CMFPlomino.config import *
from Products.CMFPlomino.PlominoField import get_field_types

from Products.CMFCore.CatalogTool import CatalogTool
from Products.ZCatalog.Catalog import CatalogError

from Products.CMFPlone.UnicodeSplitter import CaseNormalizer
from Products.CMFPlone.UnicodeSplitter import Splitter
#from Products.ZCTextIndex.Lexicon import CaseNormalizer
#from Products.ZCTextIndex.Lexicon import Splitter
#from Products.ZCTextIndex.Lexicon import StopWordRemover
from Products.ZCTextIndex.ZCTextIndex import PLexicon

from Products.CMFCore.utils import UniqueObject, SimpleRecord
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.utils import TransformException
from Products.PortalTransforms.libtransforms.utils import MissingBinary

from Products.CMFPlomino.index.PlominoCatalog import PlominoCatalog
from Products.CMFPlomino.index.PlominoViewIndex import PlominoViewIndex
from Products.CMFPlomino.index.PlominoColumnIndex import PlominoColumnIndex
from Products.CMFPlomino.index.PlominoFileIndex import PlominoFileIndex

class PlominoIndex(UniqueObject, CatalogTool):
    """Plomino index
    """
    security = ClassSecurityInfo()

    id = 'plomino_index'

    # Methods

    security.declarePublic('__init__')
    def __init__(self, FULLTEXT = False):
        """
        """
        self.no_refresh = True
        CatalogTool.__init__(self)
        self._catalog = PlominoCatalog()
        # TODO: use TextindexNG3
        #lexicon = PLexicon('plaintext_lexicon', '', Splitter(), CaseNormalizer(), StopWordRemover())
        lexicon = PLexicon('plaintext_lexicon', '', Splitter(), CaseNormalizer())
        self._setObject('plaintext_lexicon', lexicon)
        #self.createFieldIndex('Form', 'SELECTION')
        #self.createFieldIndex('getPlominoReaders', 'SELECTION')
        self.addIndex('Form', "FieldIndex")
        self.addIndex('id', "FieldIndex")
        self.addColumn('id')
        self.addIndex('getPlominoReaders', "KeywordIndex")
        self.addIndex('path', "ExtendedPathIndex")
        
        if FULLTEXT:
            self.createFieldIndex('SearchableText', 'RICHTEXT')
        self.no_refresh = False

    security.declareProtected(DESIGN_PERMISSION, 'createIndex')
    def createIndex(self, fieldname, refresh=True):
        """
        """
        if not fieldname in self.indexes():
            self._catalog.addIndex(fieldname,PlominoColumnIndex(fieldname))
        if not self._catalog.schema.has_key(fieldname):
            self.addColumn(fieldname)
            
        if refresh:
            self.refresh()

    security.declareProtected(DESIGN_PERMISSION, 'createFieldIndex')
    def createFieldIndex(self,fieldname, fieldtype, refresh=True, indextype='DEFAULT'):
        """
        """
        if indextype == 'DEFAULT':
            indextype=get_field_types()[fieldtype][1]
        if indextype=='ZCTextIndex':
            plaintext_extra = SimpleRecord( lexicon_id='plaintext_lexicon', index_type='Okapi BM25 Rank')
            if not fieldname in self.indexes():
                self.addIndex(fieldname, 'ZCTextIndex', plaintext_extra)
            if fieldtype=='ATTACHMENT' and self.getParentDatabase().getIndexAttachments():
                if not 'PlominoFiles_'+fieldname in self.indexes():
                    self._catalog.addIndex('PlominoFiles_'+fieldname, PlominoFileIndex('PlominoFiles_'+fieldname, caller=self, extra=plaintext_extra))
        else:
            if not fieldname in self.indexes():
                self.addIndex(fieldname, indextype)

        if not self._catalog.schema.has_key(fieldname):
            self.addColumn(fieldname)

        if refresh:
            self.refresh()

    security.declareProtected(DESIGN_PERMISSION, 'createSelectionIndex')
    def createSelectionIndex(self,fieldname, refresh=True):
        """
        """
        if not fieldname in self.indexes():
            self._catalog.addIndex(fieldname, PlominoViewIndex(fieldname))

        if refresh:
            self.refresh()

    security.declareProtected(DESIGN_PERMISSION, 'deleteIndex')
    def deleteIndex(self,fieldname, refresh=True):
        """
        """
        self.delIndex(fieldname)
        self.delColumn(fieldname)
        if refresh:
            self.refresh()

    security.declareProtected(READ_PERMISSION, 'indexDocument')
    def indexDocument(self, doc, idxs=None, update_metadata=1):
        """
        """
        try:
            self.catalog_object(doc,
                "/".join(doc.getPhysicalPath()),
                idxs=idxs, update_metadata=update_metadata)
        except Exception, e:
            self.portal_skins.plone_scripts.plone_log('%s\non %s'%(`e`, doc.id))
            raise

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
            self.getParentDatabase().setStatus("Re-indexing")
            self.refreshCatalog()
            self.getParentDatabase().setStatus("Ready")

    security.declareProtected(READ_PERMISSION, 'dbsearch')
    def dbsearch(self, request, sortindex=None, reverse=0, only_allowed=True, limit=None):
        """
        """
        user_groups_roles = ['Anonymous', '*']
        user_id = self.getCurrentUser().getUserName()
        if user_id != "Anonymous User":
            user_groups_roles += (
                [user_id] + 
                self.getCurrentUserGroups() + 
                self.getCurrentUserRoles()
                )
        request['getPlominoReaders'] = user_groups_roles
        try:
            results = self.search(request, sortindex, reverse, limit)
        except AttributeError:
            # attempting to sort using a non-sortable index raise an
            # AttributeError about 'documentToKeyMap'
            if hasattr(self, 'REQUEST'):
                self.writeMessageOnPage("The %s index does not allow sorting" % sortindex,
                                        self.REQUEST, error=True)
            results = self.search(request, None, reverse, limit)                
        return results

    security.declareProtected(READ_PERMISSION, 'getKeyUniqueValues')
    def getKeyUniqueValues(self,key):
        """
        """
        return self.uniqueValuesFor(key)

    security.declarePublic('convertFileToText')
    def convertFileToText(self, doc, field):
        """ (adapted from Plone3 ATContentTypes file class)
        """
        result = ''

        if hasattr(doc.getItem(field), 'keys'):
            # `files` will always be a dictionary with a single key.
            files = doc.getItem(field)
            filename = files.keys()[0]

            f = doc.getfile(filename=filename)
            if f:
                textstream = None
                mimetype = files[filename]
                try:
                    ptTool = getToolByName(self, 'portal_transforms')
                    textstream = ptTool.convertTo('text/plain', str(f), mimetype=mimetype)
                except TransformException:
                    logger.info('convertFileToText> Transform failed', exc_info=True) 
                except MissingBinary:
                    logger.info('convertFileToText> Transform failed', exc_info=True) 
                if textstream:
                    result = textstream.getData()

        return result




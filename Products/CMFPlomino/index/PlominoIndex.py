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
from Products.PortalTransforms.utils import TransformException
from Products.PortalTransforms.libtransforms.utils import MissingBinary

from Products.CMFPlomino.index.PlominoCatalog import PlominoCatalog
from Products.CMFPlomino.index.PlominoViewIndex import PlominoViewIndex
from Products.CMFPlomino.index.PlominoColumnIndex import PlominoColumnIndex
from Products.CMFPlomino.index.PlominoFileIndex import PlominoFileIndex

class PlominoIndex(UniqueObject, ZCatalog, ActionProviderBase):
    """Plomino index
    """
    security = ClassSecurityInfo()

    #id = 'plomino_index'

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
        self.no_refresh = True
        ZCatalog.__init__(self, self.getId())
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
    def createFieldIndex(self,fieldname, fieldtype, refresh=True):
        """
        """
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
        #self.catalog_object(doc, "/".join(doc.getPhysicalPath()))
        try:
            # TODO DONE LATER (cataloging real path is better but it implies
            # to test all the side-effect and provide a migration script)
            #self.catalog_object(doc)
            db = doc.getParentDatabase()
            self.catalog_object(doc,
                "/".join(db.getPhysicalPath()) + "/" + doc.id,
                idxs=idxs, update_metadata=update_metadata)
        except Exception, e:
            self.portal_skins.plone_scripts.plone_log('%s\non %s'%(`e`, doc.id))
            raise

    security.declareProtected(READ_PERMISSION, 'unindexDocument')
    def unindexDocument(self,doc):
        """
        """
        # TODO DONE LATER (cataloging real path is better but it implies
        # to test all the side-effect and provide a migration script)
        #self.uncatalog_object("/".join(doc.getPhysicalPath()
        self.uncatalog_object("/".join(doc.getParentDatabase().getPhysicalPath()) + "/" + doc.id)

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
        #DBG logger.info('dbsearch> %s, %s, %s, %s'%(`request`, sortindex, reverse, limit)) 
        return self.search(request, sortindex, reverse, limit)

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
                    except MissingBinary:
                        data = ''
                        
                    source+=data

        return source




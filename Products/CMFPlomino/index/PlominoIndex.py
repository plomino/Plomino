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

from Products.CMFPlomino.config import *
from Products.CMFPlomino.PlominoField import get_field_types

from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.utils import TransformException
from Products.PortalTransforms.libtransforms.utils import MissingBinary
from AccessControl import ClassSecurityInfo
from souper.soup import NodeAttributeIndexer
from repoze.catalog.indexes.field import CatalogFieldIndex
from repoze.catalog.indexes.text import CatalogTextIndex
from repoze.catalog.indexes.keyword import CatalogKeywordIndex


class PlominoIndex(object):
    """Plomino index
    """

    security = ClassSecurityInfo()

    security.declarePublic('__init__')
    def __init__(self, context):
        """
        """
        self.context = context

    security.declareProtected(DESIGN_PERMISSION, 'initialize')
    def initialize(self, FULLTEXT=True):
        catalog = self.context.documents().catalog
        form_indexer = NodeAttributeIndexer('Form')
        catalog[u'Form'] = CatalogFieldIndex(form_indexer)
        readers_indexer = NodeAttributeIndexer('Plomino_Readers')
        catalog[u'Plomino_Readers'] = CatalogKeywordIndex(readers_indexer)

        if FULLTEXT:
            fulltext_indexer = SearchableTextIndexer(self.context)
            catalog[u'SearchableText'] = CatalogTextIndex(fulltext_indexer)

        self.context.no_refresh = False

    def indexDocument(self, doc):
        self.context.documents().reindex([doc.record])

    def indexes(self):
        return self.context.documents().catalog.keys()

    security.declareProtected(DESIGN_PERMISSION, 'createColumnIndex')
    def createColumnIndex(self, viewid, columnid, refresh=True):
        """
        """
        if not id in self.indexes():
            column_indexer = ColumnIndexer(viewid, columnid, self.context)
            self.context.documents().catalog['PlominoViewColumn_'+viewid+'_'+columnid] = CatalogFieldIndex(column_indexer)
            
            if refresh:
                self.refresh()

    security.declareProtected(DESIGN_PERMISSION, 'createFieldIndex')
    def createFieldIndex(self, fieldname, fieldtype, refresh=True, indextype='DEFAULT'):
        """
        """
        catalog = self.context.documents().catalog
        field_indexer = NodeAttributeIndexer(fieldname)
        if indextype == 'DEFAULT':
            indextype=get_field_types()[fieldtype][1]
        if indextype == 'field':
            catalog[fieldname] = CatalogFieldIndex(field_indexer)
        elif indextype == 'keyword':
            catalog[fieldname] = CatalogKeywordIndex(field_indexer)
        elif indextype == 'text':
            catalog[fieldname] = CatalogTextIndex(field_indexer)

        if refresh:
            self.refresh()

    security.declareProtected(DESIGN_PERMISSION, 'createSelectionIndex')
    def createSelectionIndex(self, id, refresh=True):
        """
        """
        if not id in self.indexes():
            view_indexer = ViewSelectionIndexer(id, self.context)
            self.context.documents().catalog['PlominoViewFormula_' + id] = CatalogFieldIndex(view_indexer)

            if refresh:
                self.refresh()

    security.declareProtected(DESIGN_PERMISSION, 'deleteIndex')
    def deleteIndex(self, id, refresh=True):
        """
        """
        del self.context.documents().catalog[id]
        if refresh:
            self.refresh()

    security.declarePublic('refresh')
    def refresh(self):
        """
        """
        if not self.context.no_refresh:
            self.context.setStatus("Re-indexing")
            self.context.documents().reindex()
            self.context.setStatus("Ready")

    security.declareProtected(READ_PERMISSION, 'dbsearch')
    def dbsearch(self, request, sortindex=None, reverse=0, only_allowed=True, limit=None, lazy=False):
        """
        """
        user_groups_roles = ['Anonymous', '*']
        user_id = self.context.getCurrentUser().getUserName()
        if user_id != "Anonymous User":
            user_groups_roles += (
                [user_id] + 
                self.context.getCurrentUserGroups() + 
                self.context.getCurrentUserRoles()
                )
        request = """(%s) and Plomino_Readers in any([%s])""" % (
                request,
                ', '.join(["'%s'" % u for u in user_groups_roles])
                )

        results = self.context.documents().lazy(
                                request,
                                sort_index=sortindex,
                                limit=limit,
                                sort_type=sortindex,
                                reverse=reverse,
                                with_size=True)
        if lazy:
            return results
        else:
            return [o() for o in list(results)[1:]]

    security.declareProtected(READ_PERMISSION, 'getKeyUniqueValues')
    def getIndexedValue(self, index, recordid=None, record=None):
        """
        """
        if not recordid:
            if not record:
                return None
            else:
                recordid = record.intid
        return self.context.documents().catalog[index]._rev_index.get(recordid, None)

    security.declareProtected(READ_PERMISSION, 'getKeyUniqueValues')
    def getKeyUniqueValues(self, key):
        """
        """
        return list(self.context.documents().catalog[key]._fwd_index.keys()) 

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


class ViewSelectionIndexer(object):

    def __init__(self, viewname, db):
        self.viewname = viewname
        self.db = db

    def __call__(self, context, default):
        doc = self.db.getDocument(None, context)
        return doc.isSelectedInView(self.viewname)


class ColumnIndexer(object):

    def __init__(self, viewid, columnid, db):
        self.viewid = viewid
        self.columnid = columnid
        self.db = db

    def __call__(self, context, default):
        doc = self.db.getDocument(None, context)
        return doc.computeColumnValue(self.viewid, self.columnid)


class SearchableTextIndexer(object):

    def __init__(self, db):
        self.db = db

    def __call__(self, context, default):
        doc = self.db.getDocument(None, context)
        return doc.SearchableText

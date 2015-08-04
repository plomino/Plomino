# -*- coding: utf-8 -*-

from AccessControl import ClassSecurityInfo
from Products.CMFCore.CatalogTool import CatalogTool
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import UniqueObject, SimpleRecord
from Products.CMFPlone.UnicodeSplitter import CaseNormalizer
from Products.CMFPlone.UnicodeSplitter import Splitter
from Products.PortalTransforms.libtransforms.utils import MissingBinary
from Products.PortalTransforms.utils import TransformException
from Products.ZCTextIndex.ZCTextIndex import PLexicon

from ..config import DESIGN_PERMISSION, READ_PERMISSION
from ..contents.field import get_field_types
from .catalog import PlominoCatalog
from .columnindex import PlominoColumnIndex
from .fileindex import PlominoFileIndex
from .viewindex import PlominoViewIndex

DISPLAY_INDEXED_ATTR_PREFIX = 'PlominoDisplay_'


class PlominoIndex(UniqueObject, CatalogTool):
    """ Plomino index
    """
    security = ClassSecurityInfo()

    id = 'plomino_index'

    # Methods

    security.declarePublic('__init__')

    def __init__(self, FULLTEXT=False):
        """
        """
        self.no_refresh = True
        CatalogTool.__init__(self)
        self._catalog = PlominoCatalog()
        lexicon = PLexicon(
            'plaintext_lexicon',
            '',
            Splitter(),
            CaseNormalizer())
        self._setObject('plaintext_lexicon', lexicon)
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
        if fieldname not in self.indexes():
            self._catalog.addIndex(fieldname, PlominoColumnIndex(fieldname))
        if fieldname not in self._catalog.schema:
            self.addColumn(fieldname)

        if refresh:
            self.refresh()

    security.declareProtected(DESIGN_PERMISSION, 'createFieldIndex')

    def createFieldIndex(self, fieldname, fieldtype, refresh=True,
            indextype='DEFAULT', fieldmode=None):
        """
        """
        if indextype == 'DEFAULT':
            indextype = get_field_types()[fieldtype][1]
        if indextype == 'ZCTextIndex':
            plaintext_extra = SimpleRecord(
                lexicon_id='plaintext_lexicon',
                index_type='Okapi BM25 Rank')
            if fieldname not in self.indexes():
                self.addIndex(fieldname, 'ZCTextIndex', plaintext_extra)
            if (fieldtype == 'ATTACHMENT' and
                    self.getParentDatabase().indexAttachments):
                if 'PlominoFiles_' + fieldname not in self.indexes():
                    self._catalog.addIndex(
                        'PlominoFiles_%s' % fieldname,
                        PlominoFileIndex(
                            'PlominoFiles_%s' % fieldname,
                            caller=self,
                            extra=plaintext_extra)
                    )
        else:
            if fieldname not in self.indexes():
                if fieldmode == 'DISPLAY':
                    display_extra = SimpleRecord(
                        indexed_attrs='%s%s' % (
                            DISPLAY_INDEXED_ATTR_PREFIX, fieldname))
                    self.addIndex(fieldname, indextype, extra=display_extra)
                else:
                    self.addIndex(fieldname, indextype)

        if fieldname not in self._catalog.schema:
            self.addColumn(fieldname)

        if refresh:
            self.refresh()

    security.declareProtected(DESIGN_PERMISSION, 'createSelectionIndex')

    def createSelectionIndex(self, fieldname, refresh=True):
        """
        """
        if fieldname not in self.indexes():
            self._catalog.addIndex(fieldname, PlominoViewIndex(fieldname))

        if refresh:
            self.refresh()

    security.declareProtected(DESIGN_PERMISSION, 'deleteIndex')

    def deleteIndex(self, fieldname, refresh=True):
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
        self.catalog_object(doc,
            "/".join(doc.getPhysicalPath()),
            idxs=idxs, update_metadata=update_metadata)

    security.declareProtected(READ_PERMISSION, 'unindexDocument')

    def unindexDocument(self, doc):
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

    security.declarePublic('dbsearch')

    def dbsearch(self, request, sortindex=None, reverse=0,
            only_allowed=True, limit=None):
        """
        """
        if only_allowed:
            user_groups_roles = ['Anonymous', '*']
            user_id = self.getCurrentMember().getUserName()
            if user_id != "Anonymous User":
                user_groups_roles += (
                    [user_id] +
                    self.getCurrentUserGroups() +
                    self.getCurrentUserRoles())
            request['getPlominoReaders'] = user_groups_roles
        try:
            results = self.search(request, sortindex, reverse, limit)
        except AttributeError:
            # attempting to sort using a non-sortable index raise an
            # AttributeError about 'documentToKeyMap'
            if hasattr(self, 'REQUEST'):
                self.writeMessageOnPage(
                    "The %s index does not allow sorting" % sortindex,
                    self.REQUEST,
                    error=True)
            results = self.search(request, None, reverse, limit)
        return results

    security.declareProtected(READ_PERMISSION, 'getKeyUniqueValues')

    def getKeyUniqueValues(self, key):
        """
        """
        return self.uniqueValuesFor(key)

    security.declarePublic('convertFileToText')

    def convertFileToText(self, doc, field):
        """ Adapted from Plone3 ATContentTypes file class.

        If conversion fails, returns ''.
        """
        result = ''

        if hasattr(doc.getItem(field), 'keys'):
            # `files` will always be a dictionary with a single key.
            files = doc.getItem(field)
            if not files:
                return ''
            filename = files.keys()[0]

            f = doc.getfile(filename=filename)
            if f:
                textstream = None
                mimetype = files[filename]
                try:
                    ptTool = getToolByName(self, 'portal_transforms')
                    textstream = ptTool.convertTo(
                        'text/plain', str(f), mimetype=mimetype)
                except TransformException:
                    pass
                except MissingBinary:
                    pass
                if textstream:
                    result = textstream.getData()

        return result

# -*- coding: utf-8 -*-

from Products.PluginIndexes.common.UnIndex import UnIndex
from ZODB.POSException import ConflictError


class PlominoColumnIndex(UnIndex):
    """ Index for Plomino columns.
    """

    meta_type = "PlominoColumnIndex"

    query_options = ["query", "range"]

    def index_object(self, documentId, obj, threshold=None):
        """ Index an object.

        'documentId' is the integer ID of the document.
        'obj' is the object to be indexed.
        'threshold' is the number of words to process between committing
        subtransactions.  If None, subtransactions are disabled.
        """

        returnStatus = 0
        parentdb = self.getParentDatabase()
        doc = obj.__of__(parentdb)
        if self.id.startswith("PlominoViewColumn_"):
            param = self.id.split('_')
            viewname = param[1]
            if not doc.isSelectedInView(viewname):
                return 0
            columnname = param[2]
            newValue = doc.computeColumnValue(viewname, columnname)
        else:
            return 0

        oldValue = self._unindex.get(documentId, None)
        if newValue != oldValue:
            if oldValue is not None:
                self.removeForwardIndexEntry(oldValue, documentId)
                if isinstance(oldValue, list):
                    for kw in oldValue:
                        self.removeForwardIndexEntry(kw, documentId)
                if newValue is None:
                    try:
                        del self._unindex[documentId]
                    except ConflictError:
                        raise
                    except:
                        pass
            if newValue is not None:
                self.insertForwardIndexEntry(newValue, documentId)
                if isinstance(newValue, list):
                    for kw in newValue:
                        self.insertForwardIndexEntry(kw, documentId)
                self._unindex[documentId] = newValue

            returnStatus = 1

        return returnStatus

# -*- coding: utf-8 -*-

from Products.ZCTextIndex.ZCTextIndex import ZCTextIndex


class PlominoFileIndex(ZCTextIndex):
    """ Index for Plomino file attachments.
    """

    meta_type = "PlominoFileIndex"
    query_options = ["query"]

    def index_object(self, documentId, obj, threshold=None):
        """ Wrapper for  index_doc()  handling indexing of multiple attributes.

        Enter the document with the specified documentId in the index
        under the terms extracted from the indexed text attributes,
        each of which should yield either a string or a list of
        strings (Unicode or otherwise) to be passed to index_doc().
        """
        # XXX We currently ignore subtransaction threshold

        # 'result' is ignored
        result = 0
        all_texts = []
        if self._fieldname.startswith("PlominoFiles_"):
            attr = self._fieldname[13:]
            text = str(
                obj.getRenderedItem(
                    attr,
                    form=None,
                    convertattachments=True))
            if text:
                if isinstance(text, (list, tuple, )):
                    all_texts.extend(text)
                else:
                    all_texts.append(text)

        # Check that we're sending only strings
        all_texts = filter(
            lambda text: isinstance(text, basestring),
            all_texts)

        if all_texts:
            return self.index.index_doc(documentId, all_texts)

        return result

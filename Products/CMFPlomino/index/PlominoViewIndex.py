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


from Products.PluginIndexes.common.UnIndex import UnIndex

class PlominoViewIndex(UnIndex):

	"""Index for Plomino view selection formula.
	"""

	meta_type="PlominoViewIndex"

	query_options = ["query","range"]

	def index_object(self, documentId, obj, threshold=None):
		"""Index an object.

		'documentId' is the integer ID of the document.
		'obj' is the object to be indexed.
		'threshold' is the number of words to process between committing
		subtransactions.  If None, subtransactions are disabled.
		"""

		returnStatus = 0
		parentdb = self.getParentDatabase()
		doc = obj.__of__(parentdb)
		if(self.id.startswith("PlominoViewFormula_")):
			param = self.id.split('_')
			viewname=param[1]
			newSelection = doc.isSelectedInView(viewname)
		else:
			return 0

		oldSelection = self._unindex.get( documentId, None )
		if newSelection != oldSelection:
			if oldSelection is not None:
				self.removeForwardIndexEntry(oldSelection, documentId)
				if newSelection is None:
					try:
						del self._unindex[documentId]
					except ConflictError:
						raise
					except:
						pass
			if newSelection is not None:
				self.insertForwardIndexEntry( newSelection, documentId )
				self._unindex[documentId] = newSelection

			returnStatus = 1

		return returnStatus


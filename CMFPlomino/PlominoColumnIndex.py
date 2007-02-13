# -*- coding: utf-8 -*-
#
# File: PlominoColumnIndex.py
#
# Copyright (c) 2007 by ['[Eric BREHAULT]']
#
# Zope Public License (ZPL)
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL). A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#

__author__ = """[Eric BREHAULT] <[ebrehault@gmail.com]>"""
__docformat__ = 'plaintext'

from Products.PluginIndexes.common.UnIndex import UnIndex

class PlominoColumnIndex(UnIndex):

	"""Index for Plomino columns.
	"""

	__implements__ = UnIndex.__implements__

	meta_type="PlominoColumnIndex"

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
		if(self.id.startswith("PlominoViewColumn_")):
			param = self.id.split('_')
			viewname=param[1]
			columnname=param[2]
			newValue = doc.computeColumnValue(viewname, columnname)
		else:
			return 0
			
		oldValue = self._unindex.get( documentId, None )
		if newValue != oldValue:
			if oldValue is not None:
				self.removeForwardIndexEntry(oldValue, documentId)
				if newValue is None:
					try:
						del self._unindex[documentId]
					except ConflictError:
						raise
					except:
						pass
			if newValue is not None:
				self.insertForwardIndexEntry( newValue, documentId )
				self._unindex[documentId] = newValue

			returnStatus = 1
			
		return returnStatus


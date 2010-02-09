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

from Products.ZCatalog.ZCatalog import Catalog
from Missing import MV

try:
	from DocumentTemplate.cDocumentTemplate import safe_callable
except ImportError:
	# Fallback to python implementation to avoid dependancy on DocumentTemplate
	def safe_callable(ob):
		# Works with ExtensionClasses and Acquisition.
		if hasattr(ob, '__class__'):
			return hasattr(ob, '__call__') or isinstance(ob, types.ClassType)
		else:
			return callable(ob)

class PlominoCatalog(Catalog):
	"""Plomino catalog (just overloads recordify method)
	"""

	def recordify(self, object):
		""" turns an object into a record tuple """
		record = []
		# the unique id is allways the first element
		for x in self.names:
			if(x.startswith("PlominoViewColumn_")):
				param = x.split('_')
				viewname=param[1]
				columnname=param[2]
				v = object.computeColumnValue(viewname, columnname)
				record.append(v)
			else:
				attr=getattr(object, x, MV)
				if(attr is not MV and safe_callable(attr)): attr=attr()
				record.append(attr)
		return tuple(record)
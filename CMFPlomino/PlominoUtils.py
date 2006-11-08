# -*- coding: utf-8 -*-
#
# File: PlominoUtils.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:39 2006
# Generator: ArchGenXML Version 1.5.1-svn
#			http://plone.org/products/archgenxml
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

from DateTime import DateTime
from time import strptime

from zLOG import LOG, ERROR


def DateToString(d, format='%d/%m/%Y'):
	"""return the date as string using the given format, default is '%d/%m/%Y'
	"""
	return DateTime(*d[0:6]).strftime(format)

def StringToDate(str_d, format='%d/%m/%Y'):
	"""parse the string using the given format (default is '%d/%m/%Y') and return the date 
	"""
	dt = strptime(str_d, "%d/%m/%Y")
	return DateTime(dt[0], dt[1], dt[2])

def DateRange(d1, d2):
	"""return all the days from the d1 date to the d2 date (included)
	"""
	duration = int(d2-d1)
	result=[]
	current=d1
	for d in range(duration+1):
		result.append(current)
		current = current+1
	return result

def RunFormula(obj, formula):
	"""try to run formula as single line code, then try to run it as multi line indented code, and return result
	"""
	result = None
	# plominoDocument and plominoContext are the reserved names used in formulas
	plominoContext = obj
	plominoDocument = obj
	try:
		exec "result = "+formula
	except Exception:
		formula=formula.replace('\r','')
		lines=formula.split('\n')
		indented_formula="def plominoFormula(plominoDocument, plominoContext):\n"
		for l in lines:
			indented_formula=indented_formula+'\t'+l+'\n'
		try:
			exec indented_formula
			result = plominoFormula(plominoDocument, plominoContext)
		except Exception, e:
			LOG("Plomino formula", ERROR, '\n'+indented_formula)
			LOG("Plomino formula", ERROR, e)
			raise
	return result

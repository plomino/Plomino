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
from Products.CMFCore.utils import getToolByName
from Acquisition import *
import ExtensionClass
import logging
#from zope.security.untrustedpython.interpreter import RestrictedInterpreter
#from zope.security.checker import ProxyFactory

logger = logging.getLogger('Plomino')

def DateToString(d, format='%d/%m/%Y'):
	"""return the date as string using the given format, default is '%d/%m/%Y'
	"""
	#return DateTime(*d[0:6]).strftime(format)
	return d.strftime(format)

def StringToDate(str_d, format='%d/%m/%Y'):
	"""parse the string using the given format (default is '%d/%m/%Y') and return the date 
	"""
	dt = strptime(str_d, format)
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
	if not(formula=="" or formula is None):
		# does code look dangerous ?
		dangerous=['_PlominoWrappedObj', '__dict__']
		for w in dangerous:
			if w in formula:
				raise AttributeError, w+" not authorized in Plomino formula context"

		# get the parent portal and get a safe proxy
		for o in obj.aq_chain:
			if type(aq_self(o)).__name__=='PloneSite':
				safeparentportal=SafeProxy(o)

		# we cut all acquisition up to the parent db node 
#		if type(aq_self(obj)).__name__=='PlominoDatabase':
#			obj=aq_base(obj).__of__(safeparentportal)
#		else:
#			db = None
#			for o in obj.aq_chain:
#				if type(aq_self(o)).__name__=='PlominoDatabase':
#					parentdb=o
#			db = aq_base(parentdb)
#			db = db.__of__(safeparentportal)
#			obj=aq_base(obj).__of__(db)
#		safeobj=obj
		
		chain=obj.aq_chain
		chain.reverse()
		safeobj=None
		for o in chain:
			if type(aq_self(o)).__name__.startswith('Plomino'):
				currentobj=aq_base(o)
			else:
				currentobj=SafeProxy(aq_base(o))
			if safeobj==None:
				safeobj=currentobj
			else:
				safeobj=currentobj.__of__(safeobj)
		
		# plominoDocument and plominoContext are the reserved names used in formulas
		plominoContext = safeobj
		plominoDocument = safeobj
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
				msg="Plomino formula error: "+str(e)
				msg=msg+"\nin code:\n"+indented_formula
				msg=msg+"\nwith context:"+str(obj)
				logger.error(msg)
				raise
	return result

def sendMail(db, recipients, title, html_message):
	"""Send an email
	"""
	host = getToolByName(db, 'MailHost')
	plone_tools = getToolByName(db, 'plone_utils')
	message = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'
	message = message + "<html>"
	message = message + html_message
	message = message + "</html>"
	sender = db.getCurrentUser().getProperty("email")
	mail = "From: "+sender+'\n'
	mail = mail + "To: "+recipients+'\n'
	mail = mail + "Subject: "+ title + '\n'
	mail = mail + 'Content-type: text/html"\n\n'
	mail = mail + message
	#host.send(mail)
	#host.send(message, mto=recipients, mfrom=sender, subject=title, encode="ISO-8859-1")
	encoding = plone_tools.getSiteEncoding()
	host.secureSend(message, recipients,
		sender, subject=title,
		subtype='html', charset=encoding,
		debug=False, From=sender)
	
def userFullname(db, userid):
	""" return user fullname if exist, else return userid, and return Unknown if user not found
	"""
	user=getToolByName(db, 'portal_membership').getMemberById(userid)
	if not(user is None):
		fullname=user.getProperty('fullname')
		if fullname=='':
			return userid
		else:
			return fullname
	else:
		return "Unknown"
		
def userInfo(db, userid):
	""" return user object
	"""
	user=getToolByName(db, 'portal_membership').getMemberById(userid)
	return user

def importPlominoScript(obj, scriptname):
	sc=obj.resources._getOb(scriptname)
	return str(sc)
	
class SafeProxy(ExtensionClass.Base):
	def __init__(self, obj):
		self.__dict__['_PlominoWrappedObj'] = obj
		
	def __getattr__(self, attr):
		attributes_whitelist=['portal_membership', 'MailHost', 'plone_utils']
		methods_whitelist=['getMemberById',
						   'getProperty',
						   'getPhysicalPath',
						   'getAuthenticatedMember',
						   'getMemberId',
						   'getUserName',
						   'getSiteEncoding',
						   'secureSend',
						   '__of__']
		if attr in attributes_whitelist:
			return SafeProxy(getattr(aq_self(self._PlominoWrappedObj), attr))
		elif attr in methods_whitelist:
			return lambda *args, **kwargs : self.methodWrapper(getattr(aq_self(self._PlominoWrappedObj), attr), args, kwargs)
		else:
			raise AttributeError, attr+" not allowed in Plomino formula context"
		
	def __setattr__(self, attr, val):
		raise AttributeError, attr+" not allowed in Plomino formula context"
		
	def methodWrapper(self, func, args, kwargs):
		return func(*args, **kwargs)
		
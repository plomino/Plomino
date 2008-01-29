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


		
# -*- coding: utf-8 -*-
#
# File: PlominoDocument.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:39 2006
# Generator: ArchGenXML Version 1.5.1-svn
#            http://plone.org/products/archgenxml
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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import Unauthorized
from time import strptime
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

from Acquisition import *
from zLOG import LOG, ERROR

import PlominoDatabase
import PlominoView
##/code-section module-header

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoDocument_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoDocument(ATFolder):
    """Plomino Document
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATFolder,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'PlominoDocument'

    meta_type = 'PlominoDocument'
    portal_type = 'PlominoDocument'
    allowed_content_types = [] + list(getattr(ATFolder, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 0
    content_icon = 'PlominoDocument.gif'
    immediate_view = 'base_view'
    default_view = 'checkBeforeOpenDocument'
    suppl_views = ()
    typeDescription = "PlominoDocument"
    typeDescMsgId = 'description_edit_plominodocument'


    actions =  (


       {'action': "string:${object_url}/checkBeforeOpenDocument",
        'category': "object",
        'id': 'view',
        'name': 'View',
        'permissions': ("View",),
        'condition': 'python:1'
       },


       {'action': "python:here.navigationParent(here)+'/'+here.id+'/EditDocument' ",
        'category': "object",
        'id': 'edit',
        'name': 'Edit',
        'permissions': (DESIGN_PERMISSION,),
        'condition': 'python:1'
       },


    )

    _at_rename_after_creation = True

    schema = PlominoDocument_schema

    ##code-section class-header #fill in your manual code here
    security.declareProtected(READ_PERMISSION, 'OpenDocument')
    ##/code-section class-header

    # Methods

    security.declarePublic('checkBeforeOpenDocument')
    def checkBeforeOpenDocument(self):
        """check read permission and open view  NOTE: if READ_PERMISSION
        set on the 'view' actionb itself, it causes error 'maximum
        recursion depth exceeded' if user hasn't permission
        """
	if self.checkUserPermission(READ_PERMISSION):
		return self.OpenDocument()
	else:
		raise Unauthorized, "You cannot read this content"

    security.declarePublic('__init__')
    def __init__(self,oid,**kw):
        """initialization
        """
	# changed from BaseFolder to ATFolder because now inherits fron ATFolder
	ATFolder.__init__(self, oid, **kw)
	self.items={}
	self._parentdatabase=None

    security.declarePublic('setItem')
    def setItem(self,name,value):
        """
        """
	items = self.items
	items[name] = value
	self.items = items

    security.declarePublic('getItem')
    def getItem(self,name):
        """
        """
	if(self.items.has_key(name)):
		return self.items[name]
	else:
		return ''

    security.declarePublic('hasItem')
    def hasItem(self,name):
        """
        """
	return self.items.has_key(name)

    security.declarePublic('removeItem')
    def removeItem(self,name):
        """
        """
	if(self.items.has_key(name)):
		items = self.items
		del items[name]
		self.items = items

    security.declarePublic('getItems')
    def getItems(self):
        """
        """
	return self.items.keys()

    security.declarePublic('getParentDatabase')
    def getParentDatabase(self):
        """
        """
	if aq_parent(self) is not None:
		return self.getParentNode()
	else:
		return self._parentdatabase

    security.declarePublic('setParentDatabase')
    def setParentDatabase(self,db):
        """
        """
	self._parentdatabase = db

    security.declarePublic('isAuthor')
    def isAuthor(self):
        """
        """
	return self.getParentDatabase().isCurrentUserAuthor(self)

    security.declareProtected(EDIT_PERMISSION, 'delete')
    def delete(self,REQUEST):
        """delete the current doc
        """
	return_url = REQUEST.get('returnurl')
	db = self.getParentDatabase()
	db.deleteDocument(self)
	REQUEST.RESPONSE.redirect(return_url)

    security.declareProtected(EDIT_PERMISSION, 'saveDocument')
    def saveDocument(self,REQUEST):
        """save a document using the form submitted content
        """
	db = self.getParentDatabase()
	form = db.getForm(REQUEST.get('Form'))
	self.setItem('Form', form.getFormName())

	# we first process editable fields (we read the submitted value in the request)
	for field in form.getFields():
		f = field.getObject()
		mode = f.getFieldMode()
		fieldName = f.Title()
		if mode=="EDITABLE":
			submittedValue = REQUEST.get(fieldName)
			if submittedValue is not None:
				if submittedValue=='':
					self.removeItem(fieldName)
				else:
					# if non-text field, convert the value
					if f.getFieldType()=="NUMBER":
						v = long(submittedValue)
					elif f.getFieldType()=="DATETIME":
						# TO BE MODIFIED: support different date/time format
						v = strptime(submittedValue, "%d/%m/%Y")
					else:
						v = submittedValue
					self.setItem(fieldName, v)

	# then we process computed fields (refresh the value)
	# TODO: manage computed fields dependencies
	for field in form.getFields():
		f = field.getObject()
		mode = f.getFieldMode()
		fieldName = f.Title()
		if mode=="COMPUTED":
			# plominoDocument is the reserved name used in field formulae
			plominoDocument = self
			try:
				exec "result = " + f.getFormula()
			except Exception:
				result = "Error"
			self.setItem(fieldName, result)
		else:
			# computed for display field are not stored
			pass

	# update the Plomino_Authors field with the current user name
	authors = self.getItem('Plomino_Authors')
	name = db.getCurrentUser().getUserName()
	if authors == '':
		authors = []
	elif name in authors:
		pass
	else:
		authors.append(name)
	self.setItem('Plomino_Authors', authors)

	# execute the onSaveDocument code of the form
	# plominoDocument is the reserved name used in events code
	plominoDocument = self
	try:
		exec form.getOnSaveDocument()
	except Exception:
		pass

	db.getIndex().indexDocument(self)
	REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(READ_PERMISSION, 'openWithForm')
    def openWithForm(self,form,editmode=False):
        """display the document using the given form's layout - first,
        check if the user has proper access rights
        """
	if editmode:
		db = self.getParentDatabase()
		if not db.isCurrentUserAuthor(self):
			raise Unauthorized, "You cannot edit this document."

	# execute the onOpenDocument code of the form
	# plominoDocument is the reserved name used in events code
	plominoDocument = self
	try:
		exec form.getOnOpenDocument()
	except Exception:
		pass

	# we use the specified form's layout
	html_content = form.displayDocument(self, editmode)
	return html_content

    security.declareProtected(EDIT_PERMISSION, 'editWithForm')
    def editWithForm(self,form):
        """
        """
	return self.openWithForm(form, True)

    security.declarePublic('send')
    def send(self,recipients,title,formname=''):
        """
        """
	host = getToolByName(self, 'MailHost')
	db = self.getParentDatabase()
	if formname=='':
		formname = self.getItem('Form')
	form = db.getForm(formname)
	message = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">'
	message = message + "<html>"
	message = message + self.openWithForm(form)
	message = message + "</html>"
	sender = db.getCurrentUser().getProperty("email")
	mail = "From: "+sender+'\n'
	mail = mail + "To: "+recipients+'\n'
	mail = mail + "Subject: "+ title + '\n'
	mail = mail + "Content-type: text/html\n\n"
	mail = mail + message
	#host.send(message, recipients, sender, title)
	host.send(mail)

    security.declarePublic('getForm')
    def getForm(self):
        """try to acquire the formname using the parent view form formula,
        if nothing, use the Form item
        """
	if hasattr(self, 'evaluateViewForm'):
		formname = self.evaluateViewForm(self)
		if formname == "":
			formname = self.getItem('Form')
	else:
		formname = self.getItem('Form')
	return self.getParentDatabase().getForm(formname)

    security.declarePrivate('manage_afterClone')
    def manage_afterClone(self,item):
        """after cloning
        """
	# changed from BaseFolder to ATFolder because now inherits fron ATFolder
	ATFolder.manage_afterClone(self, item)

    security.declarePrivate('manage_beforeDelete')
    def manage_beforeDelete(self,item,container):
        """
        """
	db = self.getParentDatabase()
	db.getIndex().unindexDocument(self)
	# changed from BaseFolder to ATFolder because now inherits fron ATFolder
	ATFolder.manage_beforeDelete(self, item, container)

    security.declarePublic('__getattr__')
    def __getattr__(self,name):
        """Overloads getattr to return item values, view selection formula
        evaluation and views columns values as attibutes (so ZCatalog
        can read them)
        """
	if(name.startswith("PlominoViewFormula_")):
		param = name.split('_')
		viewname=param[1]
		return self.isSelectedInView(viewname)
	elif(name.startswith("PlominoViewColumn_")):
		param = name.split('_')
		viewname=param[1]
		columnname=param[2]
		return self.computeColumnValue(viewname, columnname)
	else:
		if(self.items.has_key(name)):
			return self.items[name]
		else:
			return BaseFolder.__getattr__(self, name)

    security.declareProtected("READ_PERMISSION", 'isSelectedInView')
    def isSelectedInView(self,viewname):
        """
        """
	db = self.getParentDatabase()
	v = db.getView(viewname)
	# plominoDocument is the reserved name used in selection formulae
	plominoDocument = self
	try:
		exec "result = " + v.SelectionFormula()
	except Exception:
		result = False
	return result

    security.declareProtected("READ_PERMISSION", 'computeColumnValue')
    def computeColumnValue(self,viewname,columnname):
        """
        """
	db = self.getParentDatabase()
	v = db.getView(viewname)
	# plominoDocument is the reserved name used in column formulae
	plominoDocument = self
	try:
		exec "result = " + v.getColumn(columnname).Formula()
	except Exception:
		result = False
	return result


registerType(PlominoDocument, PROJECTNAME)
# end of class PlominoDocument

##code-section module-footer #fill in your manual code here
##/code-section module-footer




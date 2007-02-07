# -*- coding: utf-8 -*-
#
# File: PlominoDesignManager.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Thu Dec 7 14:08:02 2006
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

from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from Products.CMFCore import CMFCorePermissions
from cStringIO import StringIO
from zLOG import LOG, ERROR
from Acquisition import *
##/code-section module-header
from OFS.XMLExportImport import *
import urllib
from PlominoIndex import PlominoIndex

class PlominoDesignManager:
	"""Plomino design import/export features
	"""
	security = ClassSecurityInfo()

	# Methods

	security.declareProtected(DESIGN_PERMISSION, 'refreshDB')
	def refreshDB(self):
		"""all actions to take when reseting a DB (after import for instance)
		"""
		# reset reference on portal and app
		for o in self.aq_chain:
			if type(aq_self(o)).__name__=='Application':
				self._parentapp=o
			if type(aq_self(o)).__name__=='PloneSite':
				self._parentportalid=o.id
		
		# destroy the index
		self.manage_delObjects(self.getIndex().getId())
		
		#creat e new blank index
		index = PlominoIndex()
		self._setObject(index.getId(), index)
		
		#declare all the view formulas and columns index entries
		for v in self.getViews():
			v_obj=v.getObject()
			self.getIndex().createSelectionIndex('PlominoViewFormula_'+v_obj.getViewName())
			for c in v_obj.getColumns():
				v_obj.declareColumn(c.getColumnName(), c)
		#declare all the forms fields index entries 
		for f in self.getForms():
			f_obj=f.getObject()
			for fi in f_obj.getFields():
				self.getIndex().createIndex(fi.Title)
		#reindex all the documents
		for d in self.getAllDocuments():
			self.getIndex().indexDocument(d)
			
	security.declareProtected(DESIGN_PERMISSION, 'exportDesign')
	def exportDesign(self, RESPONSE=None,REQUEST=None):
		"""return object as a .zexp stream 
		"""
		try:
			path=REQUEST.get('objpath')
			if path.startswith('resources/'):
				ob=self.resources._getOb(path.split('/')[1])
			else:
				ob=self._getOb(path)
		except Exception:
			ob=self
		id=ob.id
		f=StringIO()
		ob._p_jar.exportFile(ob._p_oid, f)
		#XMLExportImport.exportXML(ob._p_jar, ob._p_oid, f)
		if RESPONSE is not None:
			RESPONSE.setHeader('Content-type','application/data')
			RESPONSE.setHeader('Content-Disposition',
					'inline;filename=%s.%s' % (id, 'zexp'))
			return f.getvalue()

	security.declareProtected(DESIGN_PERMISSION, 'importDesign')
	def importDesign(self, REQUEST=None):
		"""import design elements in current database
		"""
		submit_import=REQUEST.get('submit_import')
		sourceURL=REQUEST.get('sourceURL')
		username=REQUEST.get('username')
		password=REQUEST.get('password')
		if submit_import:
			designelements=REQUEST.get('designelements')
			overwrite=REQUEST.get('overwrite')
			if designelements:
				if type(designelements)==str:
					designelements=[designelements]
				for e in designelements:
					if 'resources/' in e:
						container=self.resources
					else:
						container=self
					if container.hasObject(e):
						if overwrite=="yes":
							container.manage_delObjects(e)
							self.importElement(container, sourceURL, e, username, password)
					else:
						self.importElement(container, sourceURL, e, username, password)
				self.refreshDB()
		else:
			REQUEST.RESPONSE.redirect(self.absolute_url()+"/DesignImport?username="+username+"&password="+password+"&sourceURL="+sourceURL)
		
	security.declarePrivate('importElement')
	def importElement(self, container, sourceURL, path, username, password):
		"""import an element targeted by sourceURL into container
		"""
		f=self.loadPlominoURL(sourceURL+"/exportDesign?objpath="+path, username, password)
		container._importObjectFromFile(f)
		
	security.declareProtected(DESIGN_PERMISSION, 'getViewsList')
	def getViewsList(self):
		"""return the database views ids in a string
		"""
		views = self.getViews()
		ids = ""
		for v in views:
			ids=ids+v.getObject().id+"/"
		return ids
	
	security.declareProtected(DESIGN_PERMISSION, 'getFormsList')
	def getFormsList(self):
		"""return the database forms ids in a string
		"""
		forms = self.getForms()
		ids = ""
		for f in forms:
			ids=ids+f.getObject().id+"/"
		return ids
		
	security.declareProtected(DESIGN_PERMISSION, 'getResourcesList')
	def getResourcesList(self):
		"""return the database resources objects ids in a string
		"""
		res = self.resources.objectIds()
		ids = ""
		for i in res:
			ids=ids+i+"/"
		return ids

	security.declareProtected(DESIGN_PERMISSION, 'getRemoteViews')
	def getRemoteViews(self, sourceURL, username, password):
		"""get views ids list from remote database
		"""
		views = self.loadPlominoURL(sourceURL+"/getViewsList", username, password).read()
		ids = views.split('/')
		ids.pop()
		return ids

	security.declareProtected(DESIGN_PERMISSION, 'getRemoteForms')
	def getRemoteForms(self, sourceURL, username, password):
		"""get forms ids list from remote database
		"""
		forms = self.loadPlominoURL(sourceURL+"/getFormsList", username, password).read()
		ids = forms.split('/')
		ids.pop()
		return ids
		
	security.declareProtected(DESIGN_PERMISSION, 'getRemoteResources')
	def getRemoteResources(self, sourceURL, username, password):
		"""get resources ids list from remote database
		"""
		res = self.loadPlominoURL(sourceURL+"/getResourcesList", username, password).read()
		ids = res.split('/')
		ids.pop()
		return ['resources/'+i for i in ids]
		
	security.declarePrivate('loadPlominoURL')
	def loadPlominoURL(self, sourceURL, username, password):
		"""return URL page content
		"""
		sourceURL=sourceURL.replace("http://", "http://"+username+":"+password+"@")
		f=urllib.urlopen(sourceURL)
		return f
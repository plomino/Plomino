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
from Acquisition import *
##/code-section module-header
from OFS.XMLExportImport import *
import logging
from PlominoIndex import PlominoIndex
from HttpUtils import authenticateAndLoadURL, authenticateAndPostToURL

logger = logging.getLogger('Plomino')

class PlominoDesignManager:
	"""Plomino design import/export features
	"""
	security = ClassSecurityInfo()

	# Methods

	security.declareProtected(DESIGN_PERMISSION, 'refreshDB')
	def refreshDB(self):
		"""all actions to take when reseting a DB (after import for instance)
		"""
		logger.info('Refreshing database '+self.id)
		# 0.6.1 migration: remove references on portal and app
		try:
			del self._parentapp
			del self._parentportalid
		except:
			pass
		
		# destroy the index
		self.manage_delObjects(self.getIndex().getId())
		logger.info('Old index removed')
		
		#create new blank index
		index = PlominoIndex()
		self._setObject(index.getId(), index)
		logger.info('New index created')
		
		#declare all the view formulas and columns index entries
		for v_obj in self.getViews():
			self.getIndex().createSelectionIndex('PlominoViewFormula_'+v_obj.getViewName())
			for c in v_obj.getColumns():
				v_obj.declareColumn(c.getColumnName(), c)
		for f_obj in self.getForms() :
			for f in f_obj.getFields() :
				if f.deliverable :
					self.getIndex().createFieldIndex(f.id)
		logger.info('Index structure initialized')
		
		#reindex all the documents
		for d in self.getAllDocuments():
			# 0.6.1 migration: remove references on parent db
			try:
				del self._parentdatabase
			except:
				pass
				
			self.getIndex().indexDocument(d)
		logger.info('Documents indexed')
		
	security.declareProtected(DESIGN_PERMISSION, 'exportDesign')
	def exportDesign(self, REQUEST=None):
		"""export design elements from current database to remote database
		"""
		targetURL=REQUEST.get('targetURL')
		username=REQUEST.get('username')
		password=REQUEST.get('password')

		designelements=REQUEST.get('designelements')
		overwrite=REQUEST.get('overwrite')
		if designelements:
			if type(designelements)==str:
				designelements=[designelements]
			for e in designelements:
				self.exportElementPush(targetURL, e, username, password)
		REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign")

	security.declareProtected(DESIGN_PERMISSION, 'exportElementPush')
	def exportElementPush(self, targetURL, path, username, password,):
		"""send object as a .zexp stream via HTTP multipart POST
		"""
		if path.startswith('resources/'):
			ob=self.resources._getOb(path.split('/')[1])
			id="resources_"+ob.id
		else:
			ob=self._getOb(path)
			id=ob.id
		f=StringIO()
		ob._p_jar.exportFile(ob._p_oid, f)
		result=authenticateAndPostToURL(targetURL+"/importElementPush", username, password, '%s.%s' % (id, 'zexp'), f.getvalue())
			
	security.declareProtected(DESIGN_PERMISSION, 'exportElement')
	def exportElement(self, RESPONSE=None,REQUEST=None):
		"""retrieve object as a .zexp stream 
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
			if designelements:
				if type(designelements)==str:
					designelements=[designelements]
				for e in designelements:
					if 'resources/' in e:
						container=self.resources
					else:
						container=self
					if container.hasObject(e):
						container.manage_delObjects(e)
						self.importElement(container, sourceURL, e, username, password)
					else:
						self.importElement(container, sourceURL, e, username, password)
				self.refreshDB()
			REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign")
		else:
			REQUEST.RESPONSE.redirect(self.absolute_url()+"/DatabaseDesign?username="+username+"&password="+password+"&sourceURL="+sourceURL)
		
	security.declarePrivate('importElement')
	def importElement(self, container, sourceURL, path, username, password):
		"""import an element targeted by sourceURL into container
		"""
		f=authenticateAndLoadURL(sourceURL+"/exportElement?objpath="+path, username, password)
		container._importObjectFromFile(f)
	
	security.declarePrivate('importElementPush')
	def importElementPush(self,REQUEST=None):
		"""import an element received as a multipart HTTP POST
		"""
		f=REQUEST.get("file")
		filename=f.filename
		if filename.startswith('resources_'):
			container=self.resources
			filename=filename.replace('resources_','')
		else:
			container=self
		id=filename.replace('.zexp','')
		if container.hasObject(id):
			container.manage_delObjects(id)
		container._importObjectFromFile(f)
		self.refreshDB()
		
	security.declareProtected(DESIGN_PERMISSION, 'getViewsList')
	def getViewsList(self):
		"""return the database views ids in a string
		"""
		views = self.getViews()
		ids = ""
		for v in views:
			ids=ids+v.id+"/"
		return ids
	
	security.declareProtected(DESIGN_PERMISSION, 'getFormsList')
	def getFormsList(self):
		"""return the database forms ids in a string
		"""
		forms = self.getForms()
		ids = ""
		for f in forms:
			ids=ids+f.id+"/"
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
		views = authenticateAndLoadURL(sourceURL+"/getViewsList", username, password).read()
		ids = views.split('/')
		ids.pop()
		return ids

	security.declareProtected(DESIGN_PERMISSION, 'getRemoteForms')
	def getRemoteForms(self, sourceURL, username, password):
		"""get forms ids list from remote database
		"""
		forms = authenticateAndLoadURL(sourceURL+"/getFormsList", username, password).read()
		ids = forms.split('/')
		ids.pop()
		return ids
		
	security.declareProtected(DESIGN_PERMISSION, 'getRemoteResources')
	def getRemoteResources(self, sourceURL, username, password):
		"""get resources ids list from remote database
		"""
		res = authenticateAndLoadURL(sourceURL+"/getResourcesList", username, password).read()
		ids = res.split('/')
		ids.pop()
		return ['resources/'+i for i in ids]


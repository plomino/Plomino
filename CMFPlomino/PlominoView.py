# -*- coding: utf-8 -*-
#
# File: PlominoView.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:38 2006
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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes.public import *
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent
from Products.CMFPlomino.config import PROJECTNAME, READ_PERMISSION

import PlominoDocument
##/code-section module-header

schema = Schema((
	StringField(
		name='id',
		widget=StringWidget(
			label="Id",
			description="If changed after creation, refresh database is needed.",
			label_msgid='CMFPlomino_label_ViewId',
			description_msgid='CMFPlomino_help_ViewId',
			i18n_domain='CMFPlomino',
		)
	),
	
	TextField(
		name='SelectionFormula',
		widget=TextAreaWidget(
			label="Selection formula",
			description="The view selection formula is a line of Python code which should return True or False. The formula will be evaluated for each document in the database to decide if the document must be displayed in the view or not. plominoDocument is a reserved name in formulae, it returns the current Plomino document. Each document field value can be accessed directly as an attribute of the document: plominoDocument.<fieldname>",
			label_msgid='CMFPlomino_label_SelectionFormula',
			description_msgid='CMFPlomino_help_SelectionFormula',
			i18n_domain='CMFPlomino',
		)
	),

	StringField(
		name='SortColumn',
		widget=StringWidget(
			label="Sort column",
			description="Column used to sort the view",
			label_msgid='CMFPlomino_label_SortColumn',
			description_msgid='CMFPlomino_help_SortColumn',
			i18n_domain='CMFPlomino',
		)
	),

	TextField(
		name='FormFormula',
		widget=TextAreaWidget(
			label="Form formula",
			description="Documents open from the view will use the form defined by the following formula (they use their own form if empty)",
			label_msgid='CMFPlomino_label_FormFormula',
			description_msgid='CMFPlomino_help_FormFormula',
			i18n_domain='CMFPlomino',
		)
	),
	
	BooleanField(
		name='Categorized',
		default="0",
		widget=BooleanWidget(
			label="Categorized",
			description="Categorised on first column",
			label_msgid='CMFPlomino_label_Categorized',
			description_msgid='CMFPlomino_help_Categorized',
			i18n_domain='CMFPlomino',
		)
	),

	BooleanField(
		name='ReverseSorting',
		default="0",
		widget=BooleanWidget(
			label="Reverse sorting",
			description="Reverse sorting",
			label_msgid='CMFPlomino_label_ReverseSorting',
			description_msgid='CMFPlomino_help_ReverseSorting',
			i18n_domain='CMFPlomino',
		)
	),
	
	StringField(
		name='ViewTemplate',
		widget=StringWidget(
			label="View template",
			description="Leave blank to use default",
			label_msgid='CMFPlomino_label_ViewTemplate',
			description_msgid='CMFPlomino_help_ViewTemplate',
			i18n_domain='CMFPlomino',
		)
	),
	StringField(
		name='ActionBarPosition',
		default="TOP",
		widget=SelectionWidget(
			label="Position of the action bar",
			description="Select the position of the action bar",
			label_msgid='CMFPlomino_label_ActionBarPosition',
			description_msgid='CMFPlomino_help_ActionBarPosition',
			i18n_domain='CMFPlomino',
		),
		vocabulary=  [["TOP", "At the top of the page"], ["BOTTOM", "At the bottom of the page"], ["BOTH", "At the top and at the bottom of the page "]]
	),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoView_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
	schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoView(ATFolder):
	"""
	"""
	security = ClassSecurityInfo()
	__implements__ = (getattr(ATFolder,'__implements__',()),)

	# This name appears in the 'add' box
	archetype_name = 'PlominoView'

	meta_type = 'PlominoView'
	portal_type = 'PlominoView'
	allowed_content_types = ['PlominoAction', 'PlominoColumn'] + list(getattr(ATFolder, 'allowed_content_types', []))
	filter_content_types = 1
	global_allow = 0
	content_icon = 'PlominoView.gif'
	immediate_view = 'base_view'
	default_view = 'checkBeforeOpenView'
	suppl_views = ()
	typeDescription = "PlominoView"
	typeDescMsgId = 'description_edit_plominoview'


	actions =  (


	   {'action': "string:${object_url}/checkBeforeOpenView",
		'category': "object",
		'id': 'view',
		'name': 'View',
		'permissions': ("View",),
		'condition': 'python:1'
	   },


	)

	_at_rename_after_creation = True

	schema = PlominoView_schema

	##code-section class-header #fill in your manual code here
	##/code-section class-header

	# Methods

	security.declarePublic('checkBeforeOpenView')
	def checkBeforeOpenView(self):
		"""check read permission and open view NOTE: if READ_PERMISSION set
		on the 'view' actionb itself, it causes error 'maximum recursion
		depth exceeded' if user hasn't permission
		"""
		if self.checkUserPermission(READ_PERMISSION):
			if not self.getViewTemplate()=="":
				pt=self.resources._getOb(self.getViewTemplate())
				return pt.__of__(self)()
			else:
				return self.OpenView()
		else:
			raise Unauthorized, "You cannot read this content"

	security.declarePublic('__init__')
	def __init__(self,oid,**kw):
		"""Initialization
		"""
		#modified
		ATFolder.__init__(self, oid, **kw)

	security.declarePublic('getViewName')
	def getViewName(self):
		"""Get view name
		"""
		return self.id

	security.declarePublic('getParentDatabase')
	def getParentDatabase(self):
		"""Get parent database
		"""
		return self.getParentNode()

	security.declarePublic('getAllDocuments')
	def getAllDocuments(self):
		"""Get all documents (as CatalogBrains, you have to use getObject()
		to get the real PlominoDocument)
		"""
		index = self.getParentDatabase().getIndex()
		sortindex = self.getSortColumn()
		if sortindex=='':
			sortindex=None
		else:
			sortindex='PlominoViewColumn_'+self.getViewName()+'_'+sortindex
		return index.dbsearch({'PlominoViewFormula_'+self.getViewName() : True}, sortindex, self.getReverseSorting())

	security.declarePublic('getColumns')
	def getColumns(self):
		"""Get colums
		"""
		columnslist = self.getFolderContents(contentFilter = {'portal_type' : ['PlominoColumn']})
		orderedcolumns = []
		for c in columnslist:
			c_obj = c.getObject()
			if not(c_obj is None):
				orderedcolumns.append([c_obj.Position, c_obj])
		orderedcolumns.sort()
		return [i[1] for i in orderedcolumns]

	security.declarePublic('getActions')
	def getActions(self, target, hide=True):
		"""Get actions
		"""
		all = self.getFolderContents(contentFilter = {'portal_type' : ['PlominoAction']})
		
		filtered = []
		for a in all:
			obj_a=a.getObject()
			if hide:
				try:
					#result = RunFormula(target, obj_a.getHidewhen())
					result = self.runFormulaScript("action_"+obj_a.getParentNode().id+"_"+obj_a.id+"_hidewhen", target, obj_a.getHidewhen)
				except Exception:
					#if error, we hide anyway
					result = True
				if not result:
					filtered.append(obj_a)
			else:
				filtered.append(obj_a)
		return filtered
		
	security.declarePublic('getColumn')
	def getColumn(self,column_name):
		"""Get a single column
		"""
		return self._getOb( column_name )

	security.declarePublic('evaluateViewForm')
	def evaluateViewForm(self,doc):
		"""compute the form to be used to open documents
		"""
		try:
			#result = RunFormula(doc, self.getFormFormula())
			result = self.runFormulaScript("view_"+self.id+"_formformula", doc, self.getFormFormula)
		except Exception:
			result = ""
		return result

	security.declarePublic('at_post_create_script')
	def at_post_create_script(self):
		"""post create
		"""
		db = self.getParentDatabase()
		db.getIndex().createSelectionIndex('PlominoViewFormula_'+self.getViewName())
		
	security.declarePrivate('at_post_edit_script')
	def at_post_edit_script(self):
		self.cleanFormulaScripts("view_"+self.id)


	security.declarePublic('declareColumn')
	def declareColumn(self,column_name,column_obj):
		"""declare column
		"""
		db = self.getParentDatabase()
		db.getIndex().createIndex('PlominoViewColumn_'+self.getViewName()+'_'+column_name)

	security.declarePublic('getCategorizedColumnValues')
	def getCategorizedColumnValues(self,column_name):
		"""return existing values for the given key and add the empty value
		"""
		alldocs = self.getAllDocuments()
		allvalues = [getattr(doc, 'PlominoViewColumn_'+self.getViewName()+'_'+column_name) for doc in alldocs]
		categories={}
		for itemvalue in allvalues:
			if type(itemvalue)==list:
				for v in itemvalue:
					if not(v in categories):
						categories[v]=1
			else:
				if not(itemvalue in categories):
					categories[itemvalue]=1
		uniquevalues = categories.keys()
		uniquevalues.sort()
		return uniquevalues
		
	security.declarePublic('getCategoryViewEntries')
	def getCategoryViewEntries(self,category_column_name,category_value):
		"""get category view entry
		"""
		index = self.getParentDatabase().getIndex()
		sortindex = self.getSortColumn()
		if sortindex=='':
			sortindex=None
		else:
			sortindex='PlominoViewColumn_'+self.getViewName()+'_'+sortindex
		return index.dbsearch(
			{
				'PlominoViewFormula_'+self.getViewName() : True,
				'PlominoViewColumn_'+self.getViewName()+'_'+category_column_name : category_value
			},
			sortindex,
			self.getReverseSorting())

		
	security.declareProtected(DESIGN_PERMISSION, 'exportCSV')
	def exportCSV(self, REQUEST=None):
		"""export columns values as CSV
		"""
		docs=self.getAllDocuments()
		result=""
		columns=[c.id for c in self.getColumns()]
		vname=self.getViewName()
		for doc in docs:
			values=[]
			for cname in columns:
				v=getattr(doc, 'PlominoViewColumn_%s_%s' % (vname, cname))
				if v is None:
					v=''
				else:
					v=str(v)
				values.append(v)
			result=result+"\t".join(values)+"\n"
		
		if REQUEST:
			REQUEST.RESPONSE.setHeader('content-type', 'text/csv')
			REQUEST.RESPONSE.setHeader("Content-Disposition", "attachment; filename="+self.id+".csv")
		return result
				
			
			
registerType(PlominoView, PROJECTNAME)
# end of class PlominoView

##code-section module-footer #fill in your manual code here
##/code-section module-footer




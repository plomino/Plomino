#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent

from Products.CMFPlomino.config import PROJECTNAME, READ_PERMISSION

import PlominoDocument

class PlominoView(BaseFolder):
	""" Plomino view """
	schema = BaseFolderSchema + Schema(
				(StringField('Description',widget=TextAreaWidget(label='Description')),
				StringField('SelectionFormula',widget=TextAreaWidget(label='Selection formula')),
				StringField('SortColumn',widget=TextAreaWidget(label='Column used to sort the view')),
				BooleanField('Categorized',widget=BooleanWidget(label='Categorised on first column'), default=0),
				BooleanField('ReverseSorting',widget=BooleanWidget(label='Reverse sorting'), default=0),
				StringField('FormFormula',widget=TextAreaWidget(label='Form formula'))
				))
	
	content_icon = "PlominoView.gif"
	
	actions = (
		{
		'id': 'view',
		'name': 'View',
		'action': 'string:${object_url}/OpenView',
		'permissions': (READ_PERMISSION)
		},
		)
		
	security = ClassSecurityInfo()
	
	def __init__(self, oid, **kw):
		BaseFolder.__init__(self, oid, **kw)
		columns = {}
		self._columns = columns
		
	def getViewName(self):
		return self.Title()
		
	def getParentDatabase(self):
		return self.getParentNode()
	
	def getAllDocuments(self):
		#cat = getToolByName(self, 'portal_catalog', None)
		#return cat.ZopeFindAndApply(
		#	obj = self.getParentDatabase(),
		#	obj_metatypes=['PlominoDocument'],
		#	obj_expr=self.getSelectionFormula()
		#	)
		index = self.getParentDatabase().getIndex()
		sortindex = self.getSortColumn()
		if sortindex=='':
			sortindex=None
		else:
			sortindex='PlominoViewColumn_'+self.getViewName()+'_'+sortindex
		return index.dbsearch({'PlominoViewFormula_'+self.getViewName() : True}, sortindex, self.getReverseSorting())
		
	def getColumns(self):
		#return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoColumn']})
		columns = [[c.Position, c] for c in self._columns.values()]
		columns.sort()
		return [i[1] for i in columns]

	def getActions(self):
		return self.getFolderContents(contentFilter = {'portal_type' : ['PlominoAction']})
	
	def getColumn(self, column_name):
		columns = self._columns
		if columns.has_key(column_name):
			c = columns[column_name]
			if hasattr(c, '__of__'):
				c = c.__of__(self)
			return c
		else:
			return None
			
	def evaluateViewForm(self, doc):
		# plominoDocument is the reserved name used in form formulae
		plominoDocument = doc
		try:
			exec "result = " + self.getFormFormula()
		except Exception:
			result = ""
		return result
		
	def at_post_edit_script(self):
		db = self.getParentDatabase()
		db.declareDesign('views', self.getViewName(), self)
	
	def at_post_create_script(self):
		db = self.getParentDatabase()
		db.declareDesign('views', self.getViewName(), self)
		db.getIndex().createSelectionIndex('PlominoViewFormula_'+self.getViewName())
		
	security.declarePrivate('manage_beforeDelete')
	def manage_beforeDelete(self, item, container):
		db = self.getParentDatabase()
		db.undeclareDesign('views', self.getViewName())
		BaseFolder.manage_beforeDelete(self, item, container)
	
	def declareColumn(self, column_name, column_obj):
		columns = self._columns
		if not columns.has_key(column_name):
			columns[column_name] = column_obj
			self._columns = columns
			db = self.getParentDatabase()
			db.getIndex().createIndex('PlominoViewColumn_'+self.getViewName()+'_'+column_name)
	
	def undeclareColumn(self, column_name):
		columns = self._columns
		del columns[column_name]
		self._columns = columns
	
	def getCategorizedColumnValues(self, column_name):
		# return ALL existing values for the given key
		# (selection formula is not applied)
		# and add the empty value
		index = self.getParentDatabase().getIndex()
		allvalues = [v for v in index.getKeyUniqueValues('PlominoViewColumn_'+self.getViewName()+'_'+column_name)]
		allvalues.sort()
		return allvalues
		
	def getCategoryViewEntries(self, category_column_name, category_value):
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
		
registerType(PlominoView, PROJECTNAME)
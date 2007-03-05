# -*- coding: utf-8 -*-
#
# File: PlominoAgent.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:37 2006
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

from AccessControl import ClassSecurityInfo, Permissions
from Products.Archetypes.atapi import *
from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from Products.CMFPlomino.PlominoUtils import *
from AccessControl.SecurityManagement import getSecurityManager, setSecurityManager
from Products.TimerService import *
from zLOG import LOG, ERROR
from ZODB.PersistentMapping import PersistentMapping
from types import IntType, ListType, NoneType, TupleType, StringType
##/code-section module-header

INTERVAL = 1
TIME_TYPE_DEFS = {
    'minute':   {'name': 'Minute',          'min': 0, 'max': 60,
                 'fraction': INTERVAL, 'unit': 'min'},
    'hour':     {'name': 'Hour',            'min': 0, 'max': 23, 'unit': 'hour'},
    'dom':      {'name': 'Day of Month',    'min': 1, 'max': 31, 'unit': 'day'},
    'dow':      {'name': 'Day of Week',     'min': 1, 'max': 7,  'unit': 'day'},
    'month':    {'name': 'Month',           'min': 1, 'max': 12, 'unit': 'month'}
}

list_min=[["*","*"],]
list_hrs=[["*","*"],]
list_dom=[["*","*"],]
list_dow=[["*","*"],]
list_month=[["*","*"],]

c=0
while c < 32:
	if c < 13:
		i = c*5
		list_min.append([str(i),str(i)])
	if c < 24:
		list_hrs.append([str(c),str(c)])
	if c > 0:
		if c < 32:
			list_dom.append([str(c),str(c)])
		if c < 13:
			list_month.append([str(c),str(c)])
		if c < 8:
			list_dow.append([str(c),str(c)])
	c+=1
	


schema = Schema((
	StringField(
		name='id',
		widget=StringWidget(
			label="Id",
			description="The agent id",
			label_msgid='CMFPlomino_label_AgentId',
			description_msgid='CMFPlomino_help_AgentId',
			i18n_domain='CMFPlomino',
		)
	),
	TextField(
		name='Content',
		widget=TextAreaWidget(
			label="Parameter or code",
			description="Code or parameter depending on the action type",
			label_msgid='CMFPlomino_label_Content',
			description_msgid='CMFPlomino_help_Content',
			i18n_domain='CMFPlomino',
		)
	),
	StringField(
		name='user',
		widget=StringWidget(
			label="User",
			description="The run agent user",
			label_msgid='CMFPlomino_label_AgentUser',
			description_msgid='CMFPlomino_help_AgentUser',
			i18n_domain='CMFPlomino',
		)
	),
	StringField(
		name='minute',
		default="*",
		widget=SelectionWidget(
			label="Minutes",
			description="Require TimerService product",
			label_msgid='CMFPlomino_label_Minutes',
			description_msgid='CMFPlomino_help_Minutes',
			i18n_domain='CMFPlomino',
		),
		vocabulary= list_min
	),
	StringField(
		name='hour',
		default="*",
		widget=SelectionWidget(
			label="Hours",
			description="Require TimerService product",
			label_msgid='CMFPlomino_label_Hours',
			description_msgid='CMFPlomino_help_Hours',
			i18n_domain='CMFPlomino',
		),
		vocabulary= list_hrs
	),
	StringField(
		name='dow',
		default="*",
		widget=SelectionWidget(
			label="DayOfWeek",
			description="Require TimerService product",
			label_msgid='CMFPlomino_label_DayOfWeek',
			description_msgid='CMFPlomino_help_DayOfWeek',
			i18n_domain='CMFPlomino',
		),
		vocabulary= list_dow
	),
	StringField(
		name='dom',
		default="*",
		widget=SelectionWidget(
			label="DayOfMonth",
			description="Require TimerService product",
			label_msgid='CMFPlomino_label_DayOfMonth',
			description_msgid='CMFPlomino_help_DayOfMonth',
			i18n_domain='CMFPlomino',
		),
		vocabulary= list_dom
	),
	StringField(
		name='month',
		default="*",
		widget=SelectionWidget(
			label="Month",
			description="Require TimerService product",
			label_msgid='CMFPlomino_label_Month',
			description_msgid='CMFPlomino_help_Month',
			i18n_domain='CMFPlomino',
		),
		vocabulary= list_month
	),
),
)

##code-section after-local-schema #fill in your manual code here
ACTION_TYPES = [["OPENFORM", "Open form"], ["OPENVIEW", "Open view"], ["CLOSE", "Close"], ["SAVE", "Save"], ["PYTHON", "Python script"]]
ACTION_DISPLAY = [["LINK", "Link"], ["SUBMIT", "Submit button"], ["BUTTON", "Button"]]
##/code-section after-local-schema

PlominoAgent_schema = BaseSchema.copy() + \
	schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoAgent(BaseContent):
	"""
	"""
	security = ClassSecurityInfo()
	__implements__ = (getattr(BaseContent,'__implements__',()),)

	# This name appears in the 'add' box
	archetype_name = 'PlominoAgent'

	meta_type = 'PlominoAgent'
	portal_type = 'PlominoAgent'
	allowed_content_types = []
	filter_content_types = 0
	global_allow = 0
	content_icon = 'PlominoAction.gif'
	immediate_view = 'base_view'
	default_view = 'base_view'
	suppl_views = ()
	typeDescription = "PlominoAgent"
	typeDescMsgId = 'description_edit_plominoagent'

	_at_rename_after_creation = True

	schema = PlominoAgent_schema

	##code-section class-header #fill in your manual code here
	##/code-section class-header

	# Methods
	
	security.declarePublic('at_post_create_script')
	def at_post_create_script(self):
		self.activate()

	security.declarePrivate('manage_beforeDelete')
	def manage_beforeDelete(self, item, container):
		self.deactivate()
		BaseContent.manage_beforeDelete(self, item, container)

	security.declarePrivate('at_post_edit_script')
	def at_post_edit_script(self):
		self.deactivate()
		self.activate()

	security.declareProtected(CMFCorePermissions.View, 'runAgent')
	def runAgent(self,REQUEST=None):
		"""execute the python code
		"""
		#self._proxy_roles = ('PlominoManager',)
		#acl = self.acl_users
		#setSecurityManager(acl.getUserById('caro1', None))
		#user = self.getUser()
		#LOG("TESTAGENT", ERROR, user)

		plominoContext = self
		plominoReturnURL = self.getParentDatabase().absolute_url()
		try:
			RunFormula(plominoContext, self.Content())
			if REQUEST != None:
				REQUEST.RESPONSE.redirect(plominoReturnURL)
		except Exception, e:
			return "Error: %s \nCode->\n%s" % (e, self.Content())


	security.declarePublic('getParentDatabase')
	def getParentDatabase(self):
		"""Get the database containing this form
		"""
		return self.getParentNode()


	security.declareProtected( Permissions.manage_properties, 'activate' )
	def activate( self ):
		""" """
		try:
			service = getTimerService(self)
			if not service:
				raise ValueError, "Can't find event service!"
			service.subscribe( self )
		except Exception, e:
			LOG('PlominoScheduler', ERROR, 'Require TimerService product')



	security.declarePrivate('_isInsideTimeSlot')
	def _isInsideTimeSlot(self, date):
		""" check whether a date is inside a given time tuple """

		domc = date.day()
		dowc = date.dow()
		monthc = date.month()
		hourc = date.hour()
		minutec = date.minute()

		#_minute, _hour, _dom, _dow, _month = time_tuple
		if (self.month == "*") or (str(monthc) == self.month):
			if (self.dom == "*") or (str(domc) == self.dom):
				if (self.dow == "*") or (str(dowc) == self.dow):
					if (self.hour == "*") or (str(hourc) == self.hour):
						if (self.minute == "*") or (str(minutec) == self.minute):
							return 1
		return 0

	security.declareProtected( Permissions.manage_properties, 'deactivate' )
	def deactivate( self ):
		""" """
		try:
			service = getTimerService(self)
			if not service:
				raise ValueError, "Can't find event service!"
			service.unsubscribe( self )
		except Exception, e:
			LOG('PlominoScheduler', ERROR, 'Require TimerService product')



	def process_timer(self, interval, tick, prev_tick, next_tick):
		""" process one message """
		year = tick.year()
		month = tick.month()
		day = tick.day()
		hour = tick.hour()
		minute = tick.minute()
		LOG('PlominoScheduler', ERROR,'Process timer tick at %s\n'%tick)

		# decide process task or not
		date = DateTime('%s/%s/%s %s:%s:00'%(year, month, day, hour, ('%0.2ds'%minute)[0]+'0'))
		prev_delta = date - prev_tick
		#LOG('PlominoScheduler', ERROR,'prev_delta = %s\n'%prev_delta)
		#LOG('PlominoScheduler', ERROR,'prev_tick = %s\n'%prev_tick)
		if prev_delta > 0:
			if (tick - date) > prev_delta:
				return
		else:
			#LOG('PlominoScheduler', ERROR,'interval = %s\n'%INTERVAL)
			date = DateTime('%s/%s/%s %s:%s:00'%(year, month, day, hour, ('%0.2ds'%(minute+INTERVAL))[0]+'0'))
			#LOG('PlominoScheduler', ERROR,'Process timer date2 at %s\n'%date)
			next_delta = next_tick - date
			if next_delta > 0:
				if (date - tick) > next_delta:
					return
			else:
				return

		# run tasks
		#LOG('PlominoScheduler', ERROR,'Process timer tick at %s\n'%tick)

		#for ob in self.findObjects(date):
		LOG("Process task", ERROR, "calling at %s" % str(date))
		if self._isInsideTimeSlot(date):
			try:
				self.runAgent()
			except Exception, e:
				LOG('PlominoScheduler', ERROR, 'Process task error', error = sys.exc_info())

registerType(PlominoAgent, PROJECTNAME)
# end of class PlominoAgent

##code-section module-footer #fill in your manual code here
##/code-section module-footer




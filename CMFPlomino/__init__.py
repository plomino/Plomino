# -*- coding: utf-8 -*-
#
# File: CMFPlomino.py
#
# Copyright (c) 2006 by ['[Eric BREHAULT]']
# Generated: Fri Sep 29 17:50:40 2006
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


# There are three ways to inject custom code here:
#
#   - To set global configuration variables, create a file AppConfig.py.
#	   This will be imported in config.py, which in turn is imported in
#	   each generated class and in this file.
#   - To perform custom initialisation after types have been registered,
#	   use the protected code section at the bottom of initialize().
#   - To register a customisation policy, create a file CustomizationPolicy.py
#	   with a method register(context) to register the policy.

import logging
logger = logging.getLogger('Plomino')
logger.info('Installing Product')

try:
	import CustomizationPolicy
except ImportError:
	CustomizationPolicy = None

from Globals import package_home
from Products.CMFCore import utils as cmfutils
from Products.CMFCore import permissions
from Products.CMFCore import DirectoryView
from Products.CMFPlone.utils import ToolInit
from Products.Archetypes.atapi import *
from Products.Archetypes import listTypes
from Products.Archetypes.utils import capitalize

import os, os.path

from Products.CMFPlomino.config import *

DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/CMFPlomino',
									product_globals)

##code-section custom-init-head #fill in your manual code here
from Products.Archetypes.public import process_types, listTypes
from Products.CMFCore import utils
from Products.CMFCore.DirectoryView import registerDirectory
from AccessControl.Permission import registerPermissions
from Products.PythonScripts.Utility import allow_module
allow_module("Products.CMFPlomino.PlominoUtils")
##/code-section custom-init-head


def initialize(context):
	##code-section custom-init-top #fill in your manual code here
	registerPermissions([(ADD_DESIGN_PERMISSION, []), (ADD_CONTENT_PERMISSION, []), (READ_PERMISSION, []), (EDIT_PERMISSION, []), (CREATE_PERMISSION, []), (REMOVE_PERMISSION, []), (DESIGN_PERMISSION, []), (ACL_PERMISSION, [])])
	##/code-section custom-init-top

	# imports packages and types for registration

	import PlominoDatabase
	import PlominoAction
	import PlominoAgent
	import PlominoForm
	import PlominoField
	import PlominoView
	import PlominoColumn
	import PlominoDocument
	import PlominoHidewhen
	import PlominoAccessControl
	import PlominoIndex
	import PlominoFile
	
	# Initialize portal content
	content_types, constructors, ftis = process_types(
		listTypes(PROJECTNAME),
		PROJECTNAME)

	cmfutils.ContentInit(
		PROJECTNAME + ' Content',
		content_types	  = content_types,
		permission		 = DEFAULT_ADD_CONTENT_PERMISSION,
		extra_constructors = constructors,
		fti				= ftis,
		).initialize(context)

	# Apply customization-policy, if theres any
	if CustomizationPolicy and hasattr(CustomizationPolicy, 'register'):
		CustomizationPolicy.register(context)
		print 'Customization policy for CMFPlomino installed'

	##code-section custom-init-bottom #fill in your manual code here
	allTypes = zip(content_types, constructors)
	for atype, constructor in allTypes:
		kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
		if atype.archetype_name.find("PlominoDocument")>=0 or atype.archetype_name.find("PlominoFile")>=0:
			utils.ContentInit(
				kind,
				content_types	  = (atype,),
				permission		 = ADD_CONTENT_PERMISSION,
				extra_constructors = (constructor,),
				fti				= ftis,
				).initialize(context)
		else:
			utils.ContentInit(
				kind,
				content_types	  = (atype,),
				permission		 = ADD_DESIGN_PERMISSION,
				extra_constructors = (constructor,),
				fti				= ftis,
				).initialize(context)

	##/code-section custom-init-bottom

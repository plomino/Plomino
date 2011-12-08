# -*- coding: utf-8 -*-
#
# File: CMFPlomino.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
# Generator: ArchGenXML Version 2.0
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

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'


# There are three ways to inject custom code here:
#
#   - To set global configuration variables, create a file AppConfig.py.
#       This will be imported in config.py, which in turn is imported in
#       each generated class and in this file.
#   - To perform custom initialisation after types have been registered,
#       use the protected code section at the bottom of initialize().

import logging
logger = logging.getLogger('CMFPlomino')
logger.debug('Installing Product')

import os
import os.path
from Products.Archetypes import listTypes
from Products.Archetypes.atapi import *
from Products.Archetypes.utils import capitalize
from Products.CMFCore import DirectoryView
from Products.CMFCore import permissions as cmfpermissions
from Products.CMFCore import utils as cmfutils
from Products.CMFPlone.utils import ToolInit
from config import *

DirectoryView.registerDirectory('skins', product_globals)


##code-section custom-init-head #fill in your manual code here
from AccessControl.Permission import registerPermissions
from Products.PythonScripts.Utility import allow_module
from zope import component
import interfaces
from zope.interface import implements

class PlominoCoreUtils:
    implements(interfaces.IPlominoUtils)
    
    module = "Products.CMFPlomino.PlominoUtils"
    methods = ['DateToString',
               'StringToDate',
               'DateRange',
               'sendMail',
               'userFullname',
               'userInfo',
               'htmlencode',
               'Now',
               'asList',
               'urlencode',
               'csv_to_array',
               'MissingValue',
               'open_url',
               'asUnicode',
               'array_to_csv',
               'isDocument',
               'cgi_escape']

component.provideUtility(PlominoCoreUtils, interfaces.IPlominoUtils)

def get_utils():
    utils = {}
    for plugin_utils in component.getUtilitiesFor(interfaces.IPlominoUtils):
        module = plugin_utils[1].module
        utils[module] = plugin_utils[1].methods
    return utils

allow_module("Products.CMFPlomino.PlominoUtils")

def initialize(context):
    """initialize product (called by zope)"""
    ##code-section custom-init-top #fill in your manual code here
    registerPermissions([(ADD_DESIGN_PERMISSION, []),
                         (ADD_CONTENT_PERMISSION, []),
                         (READ_PERMISSION, []),
                         (EDIT_PERMISSION, []),
                         (CREATE_PERMISSION, []),
                         (REMOVE_PERMISSION, []),
                         (DESIGN_PERMISSION, []),
                         (ACL_PERMISSION, [])])
    ##/code-section custom-init-top

    # imports packages and types for registration

    import PlominoDatabase
    import PlominoAction
    import PlominoForm
    import PlominoField
    import PlominoView
    import PlominoColumn
    import PlominoDocument
    import PlominoHidewhen
    import PlominoAgent
    import PlominoCache

    # Initialize portal content
    all_content_types, all_constructors, all_ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = all_content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = all_constructors,
        fti                = all_ftis,
        ).initialize(context)

    # Give it some extra permissions to control them on a per class limit
    for i in range(0,len(all_content_types)):
        klassname=all_content_types[i].__name__
        if not klassname in ADD_CONTENT_PERMISSIONS:
            continue

        context.registerClass(meta_type   = all_ftis[i]['meta_type'],
                              constructors= (all_constructors[i],),
                              permission  = ADD_CONTENT_PERMISSIONS[klassname])


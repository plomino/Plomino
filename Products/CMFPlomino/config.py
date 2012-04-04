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

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'


# Product configuration.
#
# The contents of this module will be imported into __init__.py, the
# workflow configuration and every content type module.
#
# If you wish to perform custom configuration, you may put a file
# AppConfig.py in your product's root directory. The items in there
# will be included (by importing) in this file if found.

from Products.CMFCore.permissions import setDefaultRoles
##code-section config-head #fill in your manual code here
from Products.CMFPlomino.AppConfig import ADD_DESIGN_PERMISSION, ADD_CONTENT_PERMISSION
##/code-section config-head


PROJECTNAME = "CMFPlomino"

# Permissions
DEFAULT_ADD_CONTENT_PERMISSION = ADD_CONTENT_PERMISSION
setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))
ADD_CONTENT_PERMISSIONS = {
    'PlominoAction': ADD_DESIGN_PERMISSION,
    'PlominoForm': ADD_DESIGN_PERMISSION,
    'PlominoField': ADD_DESIGN_PERMISSION,
    'PlominoView': ADD_DESIGN_PERMISSION,
    'PlominoColumn': ADD_DESIGN_PERMISSION,
    'PlominoDocument': ADD_CONTENT_PERMISSION,
    'PlominoHidewhen': ADD_DESIGN_PERMISSION,
    'PlominoAgent': ADD_DESIGN_PERMISSION,
    'PlominoCache': ADD_DESIGN_PERMISSION,
}

setDefaultRoles(ADD_DESIGN_PERMISSION, ('Manager','Owner'))
setDefaultRoles(ADD_CONTENT_PERMISSION, ('Manager','Owner'))

product_globals = globals()

# Dependencies of Products to be installed by quick-installer
# override in custom configuration
DEPENDENCIES = []

# Dependend products - not quick-installed - used in testcase
# override in custom configuration
PRODUCT_DEPENDENCIES = []

##code-section config-bottom #fill in your manual code here
##/code-section config-bottom


# Load custom configuration not managed by archgenxml
try:
    from Products.CMFPlomino.AppConfig import *
except ImportError:
    pass

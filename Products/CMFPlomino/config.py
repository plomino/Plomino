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
from Products.CMFPlomino.AppConfig import ADD_DESIGN_PERMISSION
from Products.CMFPlomino.AppConfig import ADD_CONTENT_PERMISSION
##/code-section config-head


PROJECTNAME = "CMFPlomino"
PLOMINO_RESOURCE_NAME = "plomino"

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

setDefaultRoles(ADD_DESIGN_PERMISSION, ('Manager', 'Owner'))
setDefaultRoles(ADD_CONTENT_PERMISSION, ('Manager', 'Owner'))

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

schemaMigration = dict(
    PlominoDatabase = dict(
        AboutDescription = None,
        CountDocuments = None,
        DateTimeFormat = "datetime_format",
        DoNotListUsers = "do_not_list_users",
        DoNotReindex = "do_not_reindex",
        FulltextIndex = "fulltextIndex",
        IndexAttachments = "indexAttachments",
        IndexInPortal = "indexInPortal",
        IsDatabaseTemplate = "isDatabaseTemplate",
        StartPage = "start_page",
        UsingDescription = None,
        debugMode = "debugMode",
        i18n = "i18n"
    ),
    PlominoField = dict(
        FieldEditTemplate = "edit_template", 
        FieldMode = "field_mode",
        FieldType = "field_type",
        Formula = "formula",
        HTMLAttributesFormula = "html_attributes_formula",
        IndexType = "index_type", 
        Mandatory = "mandatory",
        FieldReadTemplate = "read_template",
        ToBeIndexed = "to_be_indexed",
        ValidationFormula ="validation_formula",
    ),
    PlominoForm = dict(
        onCreateDocument = "onCreateDocument",
        onOpenDocument = "onOpenDocument", 
        beforeSaveDocument = "beforeSaveDocument", 
        onSaveDocument = "onSaveDocument", 
        onDeleteDocument = "onDeleteDocument", 
        onSearch = "onSearch", 
        beforeCreateDocument = "beforeCreateDocument", 
        FormLayout = "form_layout", 
        FormMethod = "form_method", 
        DocumentTitle = "document_title", 
        DynamicDocumentTitle= "dynamic_document_title", 
        StoreDynamicDocumentTitle = "store_dynamic_document_title", 
        DocumentId = "document_id", 
        ActionBarPosition = None, 
        HideDefaultActions = "hide_default_actions", 
        HideInMenu = None, 
        isSearchForm = "isSearchForm", 
        isPage = "isPage", 
        SearchView = "search_view", 
        SearchFormula = "search_formula", 
        Position = None, 
        ResourcesJS = "resources_js", 
        ResourcesCSS = "resources_css"
    ),
    PlominoView = dict(
        SelectionFormula = "selection_formula",
        SortColumn = "sort_column",
        KeyColumn = "key_column",
        Categorized = "categorized",
        FormFormula = "form_formula",
        ReverseSorting = "reverse_sorting",
        ActionBarPosition = None,
        HideDefaultActions = "hide_default_actions",
        HideCheckboxes = None,
        HideInMenu = None,
        Widget = None,
        DynamicTableParameters = None,
        ViewTemplate = None,
        onOpenView = "onOpenView",
        Position = None
    ),
    PlominoColumn = dict(
        SelectedField = "displayed_field",
        Formula = "formula",
        HiddenColumn = "hidden_column"
    ),
    PlominoAgent = dict(
        Content = "content",
        RunAs = "run_as",
        
    ),
    PlominoAction = dict(
        ActionType = "action_type",
        ActionDisplay = "action_display",
        Content = "content",
        Hidewhen = "hidewhen",
        InActionBar = "in_action_bar"
    ),
    PlominoHideWhen = dict(
        Formula = "formula",
        isDynamicHidewhen = "is_dynamic_hide_when"
    )
)

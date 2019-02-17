# -*- coding: utf-8 -*-

from . import _
import os
import logging
logger = logging.getLogger('Plomino')

VERSION = "2.0"

TIMEZONE = os.environ.get('TZ', None)
if TIMEZONE:
    from DateTime import Timezones
    if TIMEZONE not in Timezones():
        logger.info('Specified timezone not recognized: %s, '
                'defaulting to local timezone.' % TIMEZONE)
        TIMEZONE = None
if not TIMEZONE:
    from DateTime import DateTime
    TIMEZONE = DateTime().timezone()

ADD_DESIGN_PERMISSION = 'CMFPlomino: Add Plomino design elements'
ADD_CONTENT_PERMISSION = 'CMFPlomino: Add Plomino content'
READ_PERMISSION = 'CMFPlomino: Read documents'
EDIT_PERMISSION = 'CMFPlomino: Edit documents'
CREATE_PERMISSION = 'CMFPlomino: Create documents'
REMOVE_PERMISSION = 'CMFPlomino: Remove documents'
DESIGN_PERMISSION = 'CMFPlomino: Modify Database design'
ACL_PERMISSION = 'CMFPlomino: Control Database ACL'

SCRIPT_ID_DELIMITER = '_-_'

PLOMINO_REQUEST_CACHE_KEY = "plomino.cache"

MSG_SEPARATOR = '\n'

PLOMINO_RESOURCE_NAME = "plomino"

FIELD_TYPES = {
    "TEXT": [_("Text"), "FieldIndex"],
    "NUMBER": [_("Number"), "FieldIndex"],
    "RICHTEXT": [_("Rich text"), "ZCTextIndex"],
    "DATETIME": [_("Date/Time"), "DateIndex"],
    "DATAGRID": [_("Datagrid"), "ZCTextIndex"],
    "NAME": [_("Name"), "FieldIndex"],
    "SELECTION": [_("Selection list"), "KeywordIndex"],
    "ATTACHMENT": [_("File attachment"), "ZCTextIndex"],
    "DOCLINK": [_("Doclink"), "KeywordIndex"],
    "GOOGLECHART": [_("Google chart"), "FieldIndex"],
    "GOOGLEVISUALIZATION": [_("Google visualization"), "FieldIndex"],
    "BOOLEAN": [_("Boolean"), "FieldIndex"],
}

FIELD_MODES = [
    ["EDITABLE", _("Editable")],
    ["COMPUTED", _("Computed")],
    ["CREATION", _("Computed on creation")],
    ["DISPLAY", _("Computed for display")],
    ["COMPUTEDONSAVE", _("Computed on save")],
]

ACTION_TYPES = [
    ["OPENFORM", _("Open form")],
    ["OPENVIEW", _("Open view")],
    ["CLOSE", _("Close")],
    ["SAVE", _("Save")],
    ["PYTHON", _("Python script")],
    ["REDIRECT", _("Redirect formula")]
]
ACTION_DISPLAY = [
    ["LINK", _("Link")],
    ["SUBMIT", _("Submit button")],
    ["BUTTON", _("Button")]
]

RENAME_AFTER_CREATION_ATTEMPTS = 100

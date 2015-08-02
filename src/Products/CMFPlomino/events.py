# -*- coding: utf-8 -*-

from collective.instancebehavior import enable_behaviors

from .config import SCRIPT_ID_DELIMITER
import fields


def afterFieldModified(obj, event):
    """
    """
    field_type = obj.field_type
    fieldinterface = getattr(
        getattr(fields, field_type.lower()),
        "I%sField" % field_type.capitalize())
    behavior = 'Products.CMFPlomino.fields.text.I%sField' % field_type.capitalize()
    enable_behaviors(obj, [behavior, ], [fieldinterface, ])

    obj.cleanFormulaScripts(
        SCRIPT_ID_DELIMITER.join(["field", obj.getPhysicalPath()[-2], obj.id]))

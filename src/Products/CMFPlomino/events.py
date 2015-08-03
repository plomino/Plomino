# -*- coding: utf-8 -*-

from collective.instancebehavior import (
    enable_behaviors,
    instance_behaviors_of,
    disable_behaviors,
)

from .config import SCRIPT_ID_DELIMITER


def afterFieldModified(obj, event):
    """
    """
    field_type = obj.field_type
    behavior = 'Products.CMFPlomino.fields.%s.I%sField' % (
        field_type.lower(),
        field_type.capitalize(),
    )

    # reset behavior if changed
    existing_behaviors = instance_behaviors_of(obj)
    if not(len(existing_behaviors) == 1 and existing_behaviors[0] == behavior):
        # clean up current behavior
        disable_behaviors(obj, existing_behaviors, [])

        # also clean up attributes declared in different field schema
        for attr in ['widget', 'format', 'type', ]:
            if hasattr(obj, attr):
                setattr(obj, attr, None)

        enable_behaviors(obj, [behavior, ], [])

    obj.cleanFormulaScripts(
        SCRIPT_ID_DELIMITER.join(["field", obj.getPhysicalPath()[-2], obj.id]))

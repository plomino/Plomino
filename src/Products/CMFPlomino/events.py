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

    # cleanup compiled formulas
    obj.cleanFormulaScripts(
        SCRIPT_ID_DELIMITER.join(["field", obj.getPhysicalPath()[-2], obj.id]))

    # re-index
    db = obj.getParentDatabase()
    if obj.to_be_indexed and not db.do_not_reindex:
        db.getIndex().createFieldIndex(
            obj.id,
            obj.field_type,
            indextype=obj.index_type,
            fieldmode=obj.field_mode,
        )


def afterFormModified(obj, event):
    """
    """
    obj.cleanFormulaScripts(SCRIPT_ID_DELIMITER.join(["form", obj.id]))

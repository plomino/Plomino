# -*- coding: utf-8 -*-

from collective.instancebehavior import (
    enable_behaviors,
    instance_behaviors_of,
    disable_behaviors,
)
from Products.CMFCore.CMFBTreeFolder import manage_addCMFBTreeFolder
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs
from zope.interface import directlyProvides

from .config import SCRIPT_ID_DELIMITER, VERSION
from .index.index import PlominoIndex


def afterDatabaseCreated(obj, event):
    obj.plomino_version = VERSION
    obj.setStatus("Ready")
    manage_addCMFBTreeFolder(obj, id='plomino_documents')
    directlyProvides(obj.documents, IHideFromBreadcrumbs)
    obj.ACL_initialized = 0
    obj.UserRoles = {}
    obj.initializeACL()
    index = PlominoIndex(FULLTEXT=obj.fulltextIndex)
    obj._setObject('plomino_index', index)
    for i in ['resources', 'scripts']:
        manage_addCMFBTreeFolder(obj, id=i)


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


def afterActionModified(obj, event):
    """
    """
    obj.cleanFormulaScripts(SCRIPT_ID_DELIMITER.join(
        ['action', obj.getParentNode().id, obj.id]))


def afterViewCreated(obj, event):
    """
    """
    db = obj.getParentDatabase()
    refresh = not db.do_not_reindex
    db.getIndex().createSelectionIndex(
        'PlominoViewFormula_' + obj.id,
        refresh=refresh)
    if refresh:
        obj.getParentDatabase().getIndex().refresh()


def afterViewModified(obj, event):
    """
    """
    db = obj.getParentDatabase()
    obj.cleanFormulaScripts(SCRIPT_ID_DELIMITER.join(["view", obj.id]))
    if not db.do_not_reindex:
        obj.getParentDatabase().getIndex().refresh()


def afterColumnModified(obj, event):
    """
    """
    view = obj.getParentView()
    view.declareColumn(obj.id, obj)
    obj.cleanFormulaScripts('column_%s_%s' % (view.id, obj.id))
    db = obj.getParentDatabase()
    if not db.do_not_reindex:
        db.getIndex().refresh()


def afterAgentModified(obj, event):
    """
    """
    obj.cleanFormulaScripts(SCRIPT_ID_DELIMITER.join(["agent", obj.id]))


def afterHidewhenModified(obj, event):
    """
    """
    obj.cleanFormulaScripts(SCRIPT_ID_DELIMITER.join(
        ['hidewhen', obj.getParentNode().id, obj.id]))

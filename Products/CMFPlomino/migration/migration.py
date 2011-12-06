from zope.interface import directlyProvides
from Products.BTreeFolder2.BTreeFolder2 import manage_addBTreeFolder
from Products.CMFPlone.interfaces import IHideFromBreadcrumbs

from Products.CMFPlomino.fields.text import ITextField
from Products.CMFPlomino.fields.selection import ISelectionField
from Products.CMFPlomino.fields.number import INumberField
from Products.CMFPlomino.fields.datetime import IDatetimeField
from Products.CMFPlomino.fields.name import INameField
from Products.CMFPlomino.fields.doclink import IDoclinkField

from Products.CMFPlomino.PlominoUtils import asUnicode

from Products.PythonScripts.PythonScript import PythonScript
from Products.PythonScripts.PythonScript import manage_addPythonScript
from OFS.Image import manage_addImage
import parser
import re

import logging
logger = logging.getLogger('Plomino migration')

def migrate(db):
    """
    """
    messages = []
    if not(hasattr(db, "plomino_version")):
        msg = migrate_to_130(db)
        messages.append(msg)
    if db.plomino_version=="1.3.0":
        # no migration needed here
        db.plomino_version = "1.4.0"
    if db.plomino_version=="1.4.0":
        msg = migrate_to_15(db)
        messages.append(msg)
    if db.plomino_version=="1.5":
        msg = migrate_to_16(db)
        messages.append(msg)
    if db.plomino_version=="1.6":
        msg = migrate_to_161(db)
        messages.append(msg)
    if db.plomino_version=="1.6.1":
        # no migration needed here
        db.plomino_version = "1.6.2"
    if db.plomino_version=="1.6.2":
        # no migration needed here
        db.plomino_version = "1.6.3"
    if db.plomino_version=="1.6.3":
        msg = migrate_to_164(db)
        messages.append(msg)
    if db.plomino_version=="1.6.4":
        msg = migrate_to_17(db)
        messages.append(msg)
    if db.plomino_version=="1.7":
        msg = migrate_to_173(db)
        messages.append(msg)
    if db.plomino_version=="1.7.3":
        # no migration needed here
        db.plomino_version = "1.7.4"
    if db.plomino_version=="1.7.4":
        msg = migrate_to_175(db)
        messages.append(msg)
    if db.plomino_version=="1.7.5":
        # no migration needed here
        db.plomino_version = "1.8"
    if db.plomino_version=="1.8":
        # no migration needed here
        db.plomino_version = "1.9"
    if db.plomino_version=="1.9":
        msg = migrate_to_1_10(db)
        messages.append(msg)
    if db.plomino_version=="1.10":
        # no migration needed here
        db.plomino_version = "1.10.3"
    if db.plomino_version=="1.10.3":
        msg = migrate_to_1_11(db)
        messages.append(msg)
    if db.plomino_version=="1.11":
        msg = migrate_to_1_12(db)
        messages.append(msg)
    if db.plomino_version=="1.12":
        # no migration needed here
        db.plomino_version = "1.13"
    return messages

def migrate_to_130(db):
    """ PlominoField schema has been changed, all type-specific parameters
    have been removed and are now handled through specific adapters.
    """
    db.setDebugMode(False)
    msg = "Migration to 1.3: DebugMode attribute added"

    for form in db.getForms():
        for field in form.getFormFields():
            type = field.getFieldType()
            if type == "TEXT":
                adapt = ITextField(field)
                adapt.widget = "TEXT"
            elif type == "NUMBER":
                adapt = INumberField(field)
                adapt.type = "INTEGER"
            elif type == "FLOAT":
                field.setFieldType("NUMBER")
                adapt = INumberField(field)
                adapt.type = "FLOAT"
            elif type == "NAME":
                adapt = INameField(field)
                adapt.type = "SINGLE"
            elif type == "NAMES":
                field.setFieldType("NAME")
                adapt = INameField(field)
                adapt.type = "MULTI"
            elif type in ("SELECTION", "MULTISELECTION", "CHECKBOX", "RADIO"):
                field.setFieldType("SELECTION")
                adapt = ISelectionField(field)
                l = getattr(field, "SelectionList", None)
                if l is not None:
                    adapt.selectionlist = list(l)
                v = getattr(field, "SelectionListFormula", None)
                if v is not None:
                    adapt.selectionlistformula = v.raw
                adapt.separator = getattr(field, "DisplayModList", getattr(field, "OtherDisplayMod", None))
                if type == "SELECTION":
                    adapt.widget = "SELECT"
                elif type == "MULTISELECTION":
                    adapt.widget = "MULTISELECT"
                elif type == "CHECKBOX":
                    adapt.widget = "CHECKBOX"
                elif type == "RADIO":
                    adapt.widget = "RADIO"
            elif type == "DOCLINK":
                adapt = IDoclinkField(field)
                v = getattr(field, "SelectionListFormula", None)
                if v is not None:
                    adapt.documentslistformula = v.raw
    msg = msg + ", FieldType remapped" 
    db.plomino_version = "1.3.0"
    return msg

def migrate_to_15(db):
    """ new attribute in Column: DisplaySum
    """
    for v_obj in db.getViews():
        for c in v_obj.getColumns():
            c.setDisplaySum(False)
    msg = "Migration to 1.5: DisplaySum attribute added"
    db.plomino_version = "1.5"
    return msg

def migrate_to_16(db):
    """ attribute Position in column is replaced by AtFolder sorting
    """
    for v_obj in db.getViews():
        # sort columns by their Position
        orderedcolumns = []
        for c in v_obj.getColumns():
            if not(c is None):
                orderedcolumns.append([c.Position, c])
        orderedcolumns.sort()

        # set the position using the previous sorting
        for i, c in enumerate(orderedcolumns):
            v_obj.moveObject(c[1].id, i)
            v_obj.plone_utils.reindexOnReorder(v_obj)

    msg = "Migration to 1.6: Position column attribute deleted"
    db.plomino_version = "1.6"
    return msg

def migrate_to_161(db):
    """ Fulltext index db attribute.
    """
    db.setFulltextIndex(False)
    msg = "Migration to 1.6.1: Fulltext index db attribute set to False"
    db.plomino_version = "1.6.1"
    return msg

def migrate_to_164(db):
    """ Fulltext index db attribute.
    """
    db.setDoNotReindex(False)
    msg = "Migration to 1.6.4: DoNotReindex db attribute set to False"
    db.plomino_version = "1.6.4"
    return msg

def migrate_to_17(db):
    """ dynamic hidewhen attribute
    """
    #for form in db.getForms():
    #    form.setIsDynamicHidewhen(False)
    msg = "Migration to 1.7: Dynamic hide-when initialized"
    db.plomino_version = "1.7"
    return msg

def migrate_to_173(db):
    """ dynamic hidewhen attribute moved
    """
    for form in db.getForms():
        for hidewhen in form.getHidewhenFormulas():
            hidewhen.setIsDynamicHidewhen(False)
    msg = "Migration to 1.7.3: Dynamic hide-when initialized"
    db.plomino_version = "1.7.3"
    return msg

def migrate_to_175(db):
    """ documents stores in BTreeFolder
    """
    manage_addBTreeFolder(db, id='plomino_documents')
    directlyProvides(db.plomino_documents, IHideFromBreadcrumbs)
    docids = [id for id in db.objectIds() if getattr(db, id).portal_type == "PlominoDocument"]
    cookie = db.manage_cutObjects(ids=docids)
    db.plomino_documents.manage_pasteObjects(cookie)
    msg = "Migration to 1.7.5: Documents moved in BTreeFolder"
    db.plomino_version = "1.7.5"
    return msg

def migrate_to_1_10(db):
    """ rename Plomino_Portlet_Availability fields
    """
    for form in db.getForms():
        for field in form.getFormFields():
            if field.id == "Plomino_Portlet_Availabilty":
                form.manage_renameObject("Plomino_Portlet_Availabilty", "Plomino_Portlet_Availability")
                field.setTitle("Plomino_Portlet_Availability")
    msg = "Migration to 1.10: Rename Plomino_Portlet_Availability fields"
    db.plomino_version = "1.10"
    return msg

def migrate_to_1_11(db):
    """ getAllDocuments now returns documents, unless requested.
    """
    # # Field formulas
    # # Selection formulas
    # # Hidewhen formulas
    # getHidewhenFormulas
    # # Column formulas
    # # Agents
    # agent.Content
    # # Script libraries
    # File: use str() to get the content and manage_edit to set it.
    # Page Template: read() and write()
    from zope.interface import providedBy
    from Products.CMFPlomino.fields.selection import ISelectionField
    
    forms = db.getForms()
    for form in forms:
        fields = form.getFormFields()
        for field in fields:
            # NB: Don't use getFormula, this strips markup from strings.
            f = field.Formula()
            if f:
                logger.info("Migrated formula: %s\n"
                            "Old version: %s"%(field, f))
                field.setFormula(
                    f.replace('getAllDocuments()', 'getAllDocuments(getObject=False)'))
            f = field.ValidationFormula()
            if f:
                logger.info("Migrated validation formula: %s\n"
                            "Old version: %s"%(field, f))
                field.setValidationFormula(
                    f.replace('getAllDocuments()', 'getAllDocuments(getObject=False)'))
            settings = field.getSettings()
            if ISelectionField in providedBy(settings).interfaces():
                selectionlistformula = settings.selectionlistformula
                if selectionlistformula:
                    settings.selectionlistformula = selectionlistformula.replace(
                        'getAllDocuments()', 'getAllDocuments(getObject=False)')
        hidewhens = form.getHidewhenFormulas()
        for hidewhen in hidewhens:
            f = hidewhen.Formula()
            if f:
                logger.info("Migrated hidewhen formula: %s\n"
                            "Old version: %s"%(hidewhen, f))
                hidewhen.setFormula(
                    f.replace('getAllDocuments()', 'getAllDocuments(getObject=False)'))
        actions = form.objectValues(spec='PlominoAction')
        for action in actions:
            f = action.Content()
            if f:
                logger.info("Migrated action formula: %s\n"
                            "Old version: %s"%(action, f))
                action.setContent(
                    f.replace('getAllDocuments()', 'getAllDocuments(getObject=False)'))
            f = action.Hidewhen()
            if f:
                logger.info("Migrated action hidewhen: %s\n"
                            "Old version: %s"%(action, f))
                action.setHidewhen(
                    f.replace('getAllDocuments()', 'getAllDocuments(getObject=False)'))
    views = db.getViews()
    for view in views:
        columns = view.getColumns()
        for column in columns:
            f = column.Formula()
            if f:
                logger.info("Migrated column formula: %s\n"
                            "Old version: %s"%(column, f))
                column.setFormula(
                    f.replace('getAllDocuments()', 'getAllDocuments(getObject=False)'))
        actions = view.objectValues(spec='PlominoAction')
        for action in actions:
            f = action.Content()
            if f:
                logger.info("Migrated action formula: %s\n"
                            "Old version: %s"%(action, f))
                action.setContent(
                    f.replace('getAllDocuments()', 'getAllDocuments(getObject=False)'))
            f = action.Hidewhen()
            if f:
                logger.info("Migrated action hidewhen: %s\n"
                            "Old version: %s"%(action, f))
                action.setHidewhen(
                    f.replace('getAllDocuments()', 'getAllDocuments(getObject=False)'))
    agents = db.getAgents()
    for agent in agents:
        f = agent.Content()
        if f:
            logger.info("Migrated agent formula: %s\n"
                        "Old version: %s"%(agent, f))
            agent.setContent(
                f.replace('getAllDocuments()', 'getAllDocuments(getObject=False)'))
    files = db.resources.objectValues('File')
    for f in files:
        if f.content_type.startswith('text'):
            formula = asUnicode(f).encode('utf-8')
            logger.info("Migrated script library formula: %s"%f.id())
            f.manage_edit(f.title, f.content_type, filedata=formula.replace(
                'getAllDocuments()', 'getAllDocuments(getObject=False)'))
    templates = db.resources.objectValues('Page Template')
    for template in templates:
        f = template.read()
        logger.info("Migrated template formula: %s"%template.id)
        template.write(
          f.replace('getAllDocuments()', 'getAllDocuments(getObject=False)'))

    msg = "Migration to 1.11: getAllDocuments API change."
    db.plomino_version = "1.11"
    return msg

def migrate_to_1_12(db):
    """ Convert resources script lib File into PythonScript and Image
    """
    libs = db.resources.objectValues('File')
    for lib in libs:
        lib_id = lib.id()
        lib_data = lib.data
        content_type = lib.getContentType() 
        if 'image' in content_type:
            db.resources.manage_delObjects(lib_id)
            lib_id = manage_addImage(db.resources, lib_id, lib_data)
        else:
            error_re = re.compile('^## Errors:$', re.MULTILINE)
            ps = PythonScript('testing')
            try:
                lib_data = asUnicode(lib_data)
            except UnicodeDecodeError, e:
                logger.info("Unknown encoding, skipping: %s" % lib_id)
                continue
            
            ps.write(lib_data)
            if not error_re.search(ps.read()):
                db.resources.manage_delObjects(lib_id)
                blank = manage_addPythonScript(db.resources, lib_id)
                sc = db.resources._getOb(lib_id)
                sc.write(lib_data)
                logger.info("Converted to Script: %s" % lib_id)
                continue
    
    msg = "Migration to 1.12: Convert resources script lib File into PythonScripts."
    db.plomino_version = "1.12"
    return msg

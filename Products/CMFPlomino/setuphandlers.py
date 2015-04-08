# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('CMFPlomino: setuphandlers')
import os
from StringIO import StringIO

from Products.CMFPlomino.config import DEPENDENCIES
from Products.CMFPlomino.config import FCK_STYLES
from Products.CMFPlomino.config import PLOMINO_RESOURCE_NAME
from Products.CMFPlomino.config import PROJECTNAME
from Products.CMFPlomino import get_resource_directory


def isNotCMFPlominoProfile(context):
    return context.readDataFile("CMFPlomino_marker.txt") is None


def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotCMFPlominoProfile(context):
        return
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'CMFPlomino':  # avoid infinite recursions
        return
    # THIS STEP MUST BE REMOVED
    # (but as it is permanent we need to unregister it properly)
    # wft = getToolByName(context.getSite(), 'portal_workflow')
    # wft.updateRoleMappings()


def postInstall(context):
    """ Called as at the end of the setup process.
    """
    if isNotCMFPlominoProfile(context):
        return
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'CMFPlomino':  # avoid infinite recursions
        return
    site = context.getSite()
    # THIS STEP MUST BE REMOVED
    # (but as it is permanent we need to unregister it properly)


def export_database_templates(context):
    """ Handler for 'Export Plomino templates' exportStep

    Write databases marked as templates to folders in a resource directory.
    """
    portal = context.getSite()
    dbs = portal.portal_catalog.searchResults({'Type': 'PlominoDatabase'})
    for brain in dbs:
        db = brain.getObject()
        if db.getIsDatabaseTemplate()==True:
            designelements = (
                [o.id for o in db.getForms()] +
                [o.id for o in db.getViews()] +
                [o.id for o in db.getAgents()] +
                ["resources/"+id for id in db.resources.objectIds()]
            )
            for id in designelements:
                xmlstring = db.exportDesignAsXML(
                        elementids=[id],
                        dbsettings=False)
                subdir = os.path.join(PLOMINO_RESOURCE_NAME, db.id)
                filename = id + '.xml'
                if id.startswith('resources/'):
                    subdir += "/resources"
                    filename = filename.split('/')[1]
                context.writeDataFile(filename,
                    text=xmlstring,
                    content_type='text/xml',
                    subdir=subdir,
                )

            xmlstring = db.exportDesignAsXML(
                    elementids=[],
                    dbsettings=True)
            context.writeDataFile("dbsettings.xml",
                text=xmlstring,
                content_type='text/xml',
                subdir= os.path.join(PLOMINO_RESOURCE_NAME, db.id),
            )
            
    logger.info('Plomino database templates exported')


def import_database_templates(context):
    """ Handler for 'Import Plomino templates' importStep
    """
    portal = context.getSite()
    resource = get_resource_directory()
    if not resource:
        logger.warning('Plomino database templates cannot be imported without plone.resource.')
    _copy_db_folder(context, PLOMINO_RESOURCE_NAME, resource)
    logger.info('Plomino database templates imported')


def _copy_db_folder(context, source_path, target):
    """ Utility: recursively copy export from source to target
    """
    filenames = context.listDirectory(source_path)
    if not filenames:
        return
    for fn in filenames:
        if context.isDirectory(source_path + '/' + fn):
            target.makeDirectory(fn)
            _copy_db_folder(context, source_path + '/' + fn, target[fn])
        else:
            f = context.readDataFile(fn, subdir=source_path)
            target.writeFile(fn, StringIO(f))

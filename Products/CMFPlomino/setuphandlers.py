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
from Products.CMFPlomino.config import PROJECTNAME
from Products.CMFPlomino.config import DEPENDENCIES
import os

from Products.CMFPlomino.config import FCK_STYLES


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

def export_databases(context):
    """
    """
    portal = context.getSite()
    dbs = portal.portal_catalog.searchResults({'Type': 'PlominoDatabase'})
    for brain in dbs:
        db = brain.getObject()
        if db.getIsDatabaseTemplate()==True:
            context.writeDataFile(db.id + '.xml',
                text=db.exportDesign(),
                content_type='text/xml',
                subdir="plomino",
            )
    logger.info('Plomino databases exported')
    
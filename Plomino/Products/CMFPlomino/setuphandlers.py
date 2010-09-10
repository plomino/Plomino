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
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
from Products.CMFPlomino.config import FCK_STYLES
##/code-section HEAD

def isNotCMFPlominoProfile(context):
    return context.readDataFile("CMFPlomino_marker.txt") is None



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotCMFPlominoProfile(context): return 
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'CMFPlomino': # avoid infinite recursions
        return
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    if isNotCMFPlominoProfile(context): return
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'CMFPlomino': # avoid infinite recursions
        return
    site = context.getSite()

    #run kupu customisation script
    if hasattr(site.portal_properties, 'kupu_library_tool'):
        logger.info('run Kupu Customisation Script')
        skin=site.portal_skins.cmfplomino_styles
        script = getattr(skin,'kupu-customisation-policy', None)
        if script:
            script()
            logger.info('runKupuCustomisationScript done')
        else:
            logger.info('runKupuCustomisationScript : kupu-customisation-policy not found')

    #customise FCKedior configuration
    if hasattr(site.portal_properties, 'fckeditor_properties'):
        properties = site.portal_properties.fckeditor_properties
        styles = getattr(properties, 'fck_menu_styles') + FCK_STYLES
        properties.manage_changeProperties(fck_menu_styles = styles)

    # tidy up old jquery reference
    jsregistry = getToolByName(site, 'portal_javascripts')
    jsregistry.unregisterResource('++resource++plomino.javascript/jquery-v1.4.2.js')

##code-section FOOT
##/code-section FOOT

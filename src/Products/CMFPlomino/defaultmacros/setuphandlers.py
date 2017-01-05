# -*- coding: utf-8 -*-
from plone import api

import logging

logger = logging.getLogger('Plomino')
macros_profile_id = 'profile-Products.CMFPlomino.defaultmacros:macros'


def macros_install(context):
    """Macros install script"""
    # Do something during the installation of this package
    logger.debug('Macros install script')
    portal = api.portal.get()

    if portal.hasObject('macros'):
        logger.debug('The site already have "macros" database')
        # return
    else:
        portal.invokeFactory('PlominoDatabase', id='macros', title='Macros')

    context_profile = context._getImportContext(macros_profile_id)
    profile_path = context_profile._profile_path
    db_path = profile_path + '/../../defaultmacros/macros.json'

    with open(db_path, 'r') as macros_file:
        db_data = macros_file.read()
        macros_db = portal.macros
        macros_db.importDesignFromJSON(jsonstring=db_data)

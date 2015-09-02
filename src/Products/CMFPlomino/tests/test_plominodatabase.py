# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from zope.component import queryUtility
from zope.component import createObject
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone import api

from Products.CMFPlomino.testing import PRODUCTS_CMFPLOMINO_INTEGRATION_TESTING  # noqa

import unittest2 as unittest


class PlominoDatabaseIntegrationTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLOMINO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='PlominoDatabase')
        self.assertTrue(fti)

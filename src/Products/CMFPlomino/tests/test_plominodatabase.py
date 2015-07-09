# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_ID
from zope.component import queryUtility
from zope.component import createObject
from plone.app.testing import setRoles
from plone.dexterity.interfaces import IDexterityFTI
from plone import api

from Products.CMFPlomino.testing import PRODUCTS_CMFPLOMINO_INTEGRATION_TESTING  # noqa
from Products.CMFPlomino.interfaces import IPlominoDatabase

import unittest2 as unittest


class PlominoDatabaseIntegrationTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLOMINO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_schema(self):
        fti = queryUtility(IDexterityFTI, name='PlominoDatabase')
        schema = fti.lookupSchema()
        self.assertEqual(IPlominoDatabase, schema)

    def test_fti(self):
        fti = queryUtility(IDexterityFTI, name='PlominoDatabase')
        self.assertTrue(fti)

    def test_factory(self):
        fti = queryUtility(IDexterityFTI, name='PlominoDatabase')
        factory = fti.factory
        obj = createObject(factory)
        self.assertTrue(IPlominoDatabase.providedBy(obj))

    def test_adding(self):
        self.portal.invokeFactory('PlominoDatabase', 'PlominoDatabase')
        self.assertTrue(
            IPlominoDatabase.providedBy(self.portal['PlominoDatabase'])
        )

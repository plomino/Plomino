# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from Products.CMFPlomino.testing import PRODUCTS_CMFPLOMINO_INTEGRATION_TESTING  # noqa
from plone import api

import unittest2 as unittest


class TestSetup(unittest.TestCase):
    """Test that Products.CMFPlomino is properly installed."""

    layer = PRODUCTS_CMFPLOMINO_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if Products.CMFPlomino is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('Products.CMFPlomino'))

    def test_uninstall(self):
        """Test if Products.CMFPlomino is cleanly uninstalled."""
        self.installer.uninstallProducts(['Products.CMFPlomino'])
        self.assertFalse(self.installer.isProductInstalled('Products.CMFPlomino'))

    def test_browserlayer(self):
        """Test that IPlominoLayer is registered."""
        from Products.CMFPlomino.interfaces import IPlominoLayer
        from plone.browserlayer import utils
        self.assertIn(IPlominoLayer, utils.registered_layers())

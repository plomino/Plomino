import unittest2 as unittest

from Products.CMFPlomino.testing import PLOMINO_FUNCTIONAL_TESTING

class IntegrationTest(unittest.TestCase):

    layer = PLOMINO_FUNCTIONAL_TESTING

    def test_some_functionality(self):
        "Dummy test"
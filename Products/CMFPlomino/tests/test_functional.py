from os.path import dirname, join
import unittest2 as unittest

from Products.CMFPlomino.testing import PLOMINO_FUNCTIONAL_TESTING

DIRPATH = join(dirname(__file__), 'filestoimport')

class IntegrationTest(unittest.TestCase):

    layer = PLOMINO_FUNCTIONAL_TESTING

    def test_hide_when(self):
        "Dummy test"
        # Import our sample database
        mydb = self.layer['portal'].mydb
        import_file('hideWhenTest.xml', mydb)


def import_file(filename, plominodb):
    filepath = join(DIRPATH, filename)
    plominodb.importDesignFromXML(open(filepath).read())

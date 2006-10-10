#
# Skeleton PloneTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase

PloneTestCase.installProduct('CMFPlomino')
PloneTestCase.setupPloneSite()


class TestPlominoDatabase(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.folder.invokeFactory('PlominoDatabase', 'db')

    def testDefaultAuthenticatedAccessRight(self):
        # Test something
        self.assertEqual(db.AuthenticatedAccessRight, 'NoAccess')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPlominoDatabase))
    return suite

if __name__ == '__main__':
    framework()


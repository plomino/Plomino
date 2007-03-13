#
# Skeleton PloneTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite()
PloneTestCase.installProduct('CMFPlomino')

class TestPlominoInstall(PloneTestCase.PloneTestCase):

    def afterSetUp(self):
        self.setRoles(['Manager'])
        self.portal.portal_quickinstaller.installProduct('CMFPlomino')
        self.types = ("PlominoDatabase",
            "PlominoAction",
            "PlominoAgent",
            "PlominoForm",
            "PlominoField",
            "PlominoView",
            "PlominoColumn",
            "PlominoDocument",
            "PlominoHidewhen",
            "PlominoAccessControl",
            )

    def testTypesInstalled(self):
        for t in self.types:
            self.failUnless(t in self.portal.portal_types.objectIds(),
                            '%s content type not installed' % t)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPlominoInstall))
    return suite

if __name__ == '__main__':
    framework()


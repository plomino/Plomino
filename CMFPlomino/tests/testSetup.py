#
# Skeleton PloneTestCase
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.PloneTestCase import PloneTestCase

PloneTestCase.setupPloneSite()
PloneTestCase.installProduct('CMFPlomino')

class TestPlominoGeneral(PloneTestCase.PloneTestCase):

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
            
    def testCreateDB(self):
        self.portal.invokeFactory('PlominoDatabase', 'testdb')
        self.assertEqual(self.portal.testdb.id, 'testdb')
        db=self.portal.testdb
        db.invokeFactory('PlominoView', 'view1')
        self.failUnless(db.view1)
        view=db.view1
        view.setSelectionFormula='True'
        db.invokeFactory('PlominoForm', 'form1')
        self.failUnless(db.form1)
        form=db.form1
        form.setFormLayout="""<h1>test</h1>
<table><tr><td>Foo:</td><td><span class="plominoFieldClass">foo</span></td></tr></table>"""
        


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPlominoGeneral))
    return suite

if __name__ == '__main__':
    framework()


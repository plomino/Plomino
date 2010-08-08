from Products.PloneTestCase import ptc
from Testing import ZopeTestCase as ztc
from Products.CMFDefault.factory import addConfiguredSite
from collective.testcaselayer import ptc as tcl_ptc
from collective.testcaselayer import common

ztc.installProduct('SiteAccess')

class Layer(tcl_ptc.BasePTCLayer):
    """Install collective.foo"""

    def afterSetUp(self):
        ztc.installPackage('Products.CMFPlomino')

        import Products.CMFPlone
        import Products.CMFPlomino
        self.loadZCML('configure.zcml', package=Products.CMFPlone)
        self.loadZCML('configure.zcml', package=Products.CMFPlomino)
        
        app = ztc.app()
        addConfiguredSite(app, 'site', 'Products.CMFPlone:plone',
                          snapshot=False,
                          extension_ids=('Products.CMFPlomino:default',
                                        ))
        self.addProfile('Products.CMFPlomino:default')
        self.loginAsPortalOwner()
        
base_layer = Layer([common.common_layer])

ptc.setupPloneSite()

class PlominoTestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here. This applies to unit 
    test cases.
    """

    layer = base_layer

class PlominoFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use doctest
    syntax. Again, we can put basic common utility or setup code in here.
    """

    layer = base_layer
    
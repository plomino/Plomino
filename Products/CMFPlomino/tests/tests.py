import unittest
import doctest


from Testing import ZopeTestCase as ztc
from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

def test_suite():
    """This sets up a test suite that actually runs the tests in the class
    above
    """
    return unittest.TestSuite([

        # Here, we create a test suite passing the name of a file relative 
        # to the package home, the name of the package, and the test base 
        # class to use. Here, the base class is a full PloneTestCase, which
        # means that we get a full Plone site set up.

        # The actual test is in functional.txt
#        ztc.ZopeDocFileSuite(
#            'tests/debug.txt', package='Products.CMFPlomino',
#            test_class=ExampleFunctionalTestCase,
#            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
#            #optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ztc.ZopeDocFileSuite(
            'tests/plomino.txt', package='Products.CMFPlomino',
            test_class=ExampleFunctionalTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
            #optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ztc.ZopeDocFileSuite(
            'tests/plomino_accesControl.txt', package='Products.CMFPlomino',
            test_class=ExampleFunctionalTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
            #optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        ztc.ZopeDocFileSuite(
            'tests/samples.txt', package='Products.CMFPlomino',
            test_class=ExampleFunctionalTestCase,
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
            #optionflags=doctest.REPORT_ONLY_FIRST_FAILURE | doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),

        # We could add more doctest files here as well, by copying the file
        # block above.

        ])

@onsetup
def setup_product():
    """Set up the package and its dependencies.

    The @onsetup decorator causes the execution of this body to be deferred
    until the setup of the Plone site testing layer. We could have created our
    own layer, but this is the easiest way for Plone integration tests.
    """
    fiveconfigure.debug_mode = True
    import Products.CMFPlomino
    zcml.load_config('configure.zcml', Products.CMFPlomino)
    fiveconfigure.debug_mode = False


# The order here is important: We first call the (deferred) function which
# installs the products we need for this product. Then, we let PloneTestCase 
# set up this product on installation.

ztc.installProduct('CMFPlomino')
setup_product()
ptc.setupPloneSite(products=['CMFPlomino'], extension_profiles=['Products.CMFPlomino:default'])

class ExampleFunctionalTestCase(ptc.FunctionalTestCase):
    """We use this class for functional integration tests that use doctest
    syntax. Again, we can put basic common utility or setup code in here.
    """

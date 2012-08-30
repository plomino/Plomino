from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.app.testing import login, setRoles
from plone.app.testing import FunctionalTesting
from plone.app.testing import selenium_layers

from plone.testing import z2

class Plomino(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE, )
    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import Products.CMFPlomino
        self.loadZCML(package=Products.CMFPlomino)

        # Install product and call its initialize() function
        z2.installProduct(app, 'Products.CMFPlomino')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'Products.CMFPlomino:default')

        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)

        portal.invokeFactory('PlominoDatabase', id='mydb')
        portal.mydb.at_post_create_script()
        setRoles(portal, TEST_USER_ID, ['Member'])

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'Products.CMFPlomino')

PLOMINO_FIXTURE = Plomino()
PLOMINO_FUNCTIONAL_TESTING = FunctionalTesting(bases=(PLOMINO_FIXTURE,), name="Plomino:Functional")

class PlominoSelenium(PloneSandboxLayer):

    defaultBases = (selenium_layers.SELENIUM_FIXTURE, PLOMINO_FIXTURE)


PLOMINO_SELENIUM_FIXTURE = PlominoSelenium()
PLOMINO_SELENIUM_TESTING = FunctionalTesting(bases=(PLOMINO_SELENIUM_FIXTURE,), name="Plomino:Selenium")

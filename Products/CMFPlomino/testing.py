from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting, FunctionalTesting

from plone.testing import z2

class Plomino(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import Products.CMFPlomino
        self.loadZCML(package=Products.CMFPlomino)

        # Install product and call its initialize() function
        z2.installProduct(app, 'Products.CMFPlomino')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'Products.CMFPlomino:default')

    def tearDownZope(self, app):
        # Uninstall product
        z2.uninstallProduct(app, 'Products.CMFPlomino')

PLOMINO_FIXTURE = Plomino()
PLOMINO_INTEGRATION_TESTING = IntegrationTesting(bases=(PLOMINO_FIXTURE,), name="Plomino:Integration")
PLOMINO_FUNCTIONAL_TESTING = FunctionalTesting(bases=(PLOMINO_FIXTURE,), name="Plomino:Functional")

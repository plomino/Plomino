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
        import plomino.tinymce
        import Products.CMFPlomino
        self.loadZCML(package=plomino.tinymce)
        self.loadZCML(package=Products.CMFPlomino)

        # Install product and call its initialize() function
        z2.installProduct(app, 'plomino.tinymce')
        z2.installProduct(app, 'Products.CMFPlomino')

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'Products.CMFPlomino:default')

        setRoles(portal, TEST_USER_ID, ['Manager', 'Member'])
        login(portal, TEST_USER_NAME)

        portal.invokeFactory('PlominoDatabase', id='mydb')
        portal.mydb.at_post_create_script()
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")
        db = portal.mydb
        db.invokeFactory('PlominoForm', id='frm_test', title='Form 1')
        db.frm_test.invokeFactory('PlominoField', id='field_1',
            title='field_1', FieldType="TEXT", FieldMode="EDITABLE")
        db.frm_test.field_1.at_post_create_script()
        db.frm_test.setFormLayout("""<p>please enter a value for field_1: <span class="plominoFieldClass">field_1</span></p>""")

    def tearDownZope(self, app):
        # app.manage_delObjects(ids=['PloneRemote'])
        # Uninstall product
        z2.uninstallProduct(app, 'Products.CMFPlomino')
        z2.uninstallProduct(app, 'plomino.tinymce')

PLOMINO_FIXTURE = Plomino()
PLOMINO_FUNCTIONAL_TESTING = FunctionalTesting(bases=(PLOMINO_FIXTURE,), name="Plomino:Functional")

class PlominoSelenium(PloneSandboxLayer):
    defaultBases = (selenium_layers.SELENIUM_FIXTURE, PLOMINO_FIXTURE)


PLOMINO_SELENIUM_FIXTURE = PlominoSelenium()
PLOMINO_SELENIUM_TESTING = FunctionalTesting(bases=(PLOMINO_SELENIUM_FIXTURE,), name="Plomino:Selenium")

from plone.app.testing import FunctionalTesting
from plone.app.robotframework.testing import AUTOLOGIN_LIBRARY_FIXTURE

PLOMINO_ROBOT_TESTING = FunctionalTesting(
    bases=(AUTOLOGIN_LIBRARY_FIXTURE, PLOMINO_FIXTURE, z2.ZSERVER),
    name="Plomino:Robot")

# -*- coding: utf-8 -*-
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, setRoles
from plone.testing import z2

import Products.CMFPlomino


class ProductsCmfplominoLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=Products.CMFPlomino)
        z2.installProduct(app, 'Products.CMFPlomino')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'Products.CMFPlomino:default')

        setRoles(portal, TEST_USER_ID, ['Manager', 'Member'])
        login(portal, TEST_USER_NAME)

        db = api.content.create(
            type='PlominoDatabase',
            id='mydb',
            title='mydb',
            container=portal)
        frm_test = api.content.create(
            type='PlominoForm',
            id='frm_test',
            title='Form 1',
            container=db)
        frm_test.form_layout = """<p>please enter a value for field_1: <span class="plominoFieldClass">field_1</span></p>"""
        field_1 = api.content.create(
            type='PlominoField',
            id='field_1',
            title='field_1',
            container=frm_test)
        field_1.field_type = "TEXT"
        field_1.field_mode = "EDITABLE"

        db.createDocument("doc1")


PRODUCTS_CMFPLOMINO_FIXTURE = ProductsCmfplominoLayer()


PRODUCTS_CMFPLOMINO_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PRODUCTS_CMFPLOMINO_FIXTURE,),
    name='ProductsCmfplominoLayer:IntegrationTesting'
)


PRODUCTS_CMFPLOMINO_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PRODUCTS_CMFPLOMINO_FIXTURE,),
    name='ProductsCmfplominoLayer:FunctionalTesting'
)


PRODUCTS_CMFPLOMINO_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        PRODUCTS_CMFPLOMINO_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='ProductsCmfplominoLayer:AcceptanceTesting'
)

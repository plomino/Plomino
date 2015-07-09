# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import Products.CMFPlomino


class ProductsCmfplominoLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=Products.CMFPlomino)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'Products.CMFPlomino:default')


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

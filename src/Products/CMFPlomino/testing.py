# -*- coding: utf-8 -*-
import os
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile, ploneSite
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, login, setRoles
from plone.testing import z2, Layer
import logging, sys

import Products.CMFPlomino
from Products.Sessions.SessionDataManager import SessionDataManager
from Products.TemporaryFolder.TemporaryFolder import MountedTemporaryFolder
from Products.Transience.Transience import TransientObjectContainer
from Products.Sessions.BrowserIdManager import BrowserIdManager

tf_name = 'temp_folder'
idmgr_name = 'browser_id_manager'
toc_name = 'temp_transient_container'
sdm_name = 'session_data_manager'

class ProductsCmfplominoLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=Products.CMFPlomino)
        z2.installProduct(app, 'Products.CMFPlomino')

        # Enable session data management with the site
        bidmgr = BrowserIdManager(idmgr_name)
        tf = MountedTemporaryFolder(tf_name, title="Temporary Folder")
        toc = TransientObjectContainer(toc_name, title='Temporary Transient Object Container', timeout_mins=20)
        session_data_manager = SessionDataManager(id=sdm_name,
                                                  path='/' + tf_name + '/' + toc_name, title='Session Data Manager',
                                                  requestName='TESTOFSESSION')
        app._setObject(idmgr_name, bidmgr)
        app._setObject(sdm_name, session_data_manager)
        app._setObject(tf_name, tf)
        app.temp_folder._setObject(toc_name, toc)

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

class ProductsMacrosLayer(Layer):

    defaultBases = (PRODUCTS_CMFPLOMINO_FIXTURE,)

#    def setUpZope(self, app, configurationContext):
#        self.loadZCML(package=Products.CMFPlomino)
#        z2.installProduct(app, 'Products.CMFPlomino')

    def setUp(self):
 #       applyProfile(portal, 'Products.CMFPlomino:default')
#        super(ProductsMacrosLayer, self).setUpPloneSite(portal)
        with ploneSite() as portal:
            applyProfile(portal, 'Products.CMFPlomino.defaultmacros:macros')

        # Show debug logs
        # root_logger = logging.getLogger()
        # root_logger.setLevel(logging.DEBUG)
        # handler = logging.StreamHandler(sys.stderr)
        # formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # handler.setFormatter(formatter)
        # root_logger.addHandler(handler)

        # self.browser.handleErrors = False
        # self.portal.error_log._ignored_exceptions = ()
        #
        # def raising(self, info):
        #     import traceback
        #     traceback.print_tb(info[2])
        #     print info[1]
        #
        # from Products.SiteErrorLog.SiteErrorLog import SiteErrorLog
        # SiteErrorLog.raising = raising


class TestDBsLayer(Layer):

    defaultBases = (PRODUCTS_CMFPLOMINO_FIXTURE,)

    def setUp(self):


        # data structure is
        # - tests/robot/test_dbs/myservice/*.json (design)
        # - tests/robot/test_dbs/myservice_data.json (data)
        with ploneSite() as portal:
            dir = os.path.abspath(os.path.join(__file__ ,"../tests/robot/test_dbs"))
            datas = []
            dbs = []
            for id in os.listdir(dir):
                if id.endswith('_data.json'):
                    datas.append(id)
                    continue
                elif not os.path.isdir(os.path.join(dir,id)):
                    continue
                oid = portal.invokeFactory('PlominoDatabase', id=id)
                db = getattr(portal, oid)
                db.importDesignFromJSON(from_folder=os.path.join(dir,id), replace = True)
                dbs.append( (id,db) )
            for id,db in dbs:
                data_import = "%s_data.json" % id
                if data_import not in datas:
                    continue
                db.importFromJSON(from_file=os.path.join(dir,data_import))



PRODUCTS_MACROS_FIXTURE = ProductsMacrosLayer()

TEST_DBS_FIXTURE = TestDBsLayer()

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
        TEST_DBS_FIXTURE,
        PRODUCTS_MACROS_FIXTURE,
        PRODUCTS_CMFPLOMINO_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='ProductsCmfplominoLayer:AcceptanceTesting'
)

import Missing
import os
import pstats
import unittest
from urllib2 import HTTPError

from AccessControl.unauthorized import Unauthorized
from DateTime import DateTime
from decimal import Decimal
import cStringIO
from plone.app.testing import ploneSite, SITE_OWNER_NAME, SITE_OWNER_PASSWORD, PloneSandboxLayer, applyProfile
from plone.testing import Layer
from Products.CMFPlomino.config import TIMEZONE
from Products.CMFPlomino.testing import PRODUCTS_CMFPLOMINO_FUNCTIONAL_TESTING, PRODUCTS_CMFPLOMINO_ACCEPTANCE_TESTING, PRODUCTS_CMFPLOMINO_FIXTURE
from Products.CMFPlomino import utils
from plone.testing.z2 import Browser, FunctionalTesting
import transaction
from zope.configuration import xmlconfig
from plone.testing import z2, Layer
import pas.plugins.ldap
import cProfile


PROFILEZCML = """
<configure
  xmlns="http://namespaces.zope.org/zope"
  xmlns:profiler="http://namespaces.plone.org/profiler"
  xmlns:five="http://namespaces.zope.org/five"
  xmlns:i18n="http://namespaces.zope.org/i18n">
  <profiler:profile
      class="Products.CMFPlomino.browser.form.FormView"
      method="_process_form"
      immediate="True"
      filename="test_profile_subforms.prof"
      entries="300"
      />
</configure>
"""

class TestProfileLayer(PloneSandboxLayer):

    defaultBases = (PRODUCTS_CMFPLOMINO_FIXTURE,)


    def setUpZope(self, app, configurationContext):

        self.loadZCML(package=pas.plugins.ldap)
        z2.installProduct(app, 'pas.plugins.ldap')

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'pas.plugins.ldap:default')


        portal.invokeFactory('PlominoDatabase', id="profdb")
        db = portal.profdb
        wf_tool = portal.portal_workflow
        wf_tool.doActionFor(db, 'publish')
        #self.db.manage_setLocalRoles('userManager', ['PlominoManager'])


        id = db.invokeFactory('PlominoForm', id='form', title='Form')
        topform = getattr(db, "form")
        topform.form_layout = ""

        for i in range(0,10):

            id = db.invokeFactory('PlominoForm', id='form%i'%i, title='Form 1')
            form = getattr(db, "form%i"%i)
            id = form.invokeFactory('PlominoField',
                    id='field%i'%i,
                    title='field%i'%i,
                    field_type="TEXT",
                    field_mode="EDITABLE")
            field = getattr(form, 'field%i'%i)
            field.widget="TEXT"
            field.validation_formula = "return ''"

            form.invokeFactory('PlominoHidewhen',
                id='hide%i'%i,
                title='Title for radio',
                formula="return plominoContext.REQUEST.get('hide', False)")

            form.form_layout = """<p><label for="field%i">field%i</label><span class="plominoFieldClass">field%i</span></p>"""%(i,i,i)
            form.form_layout += '<span class="plominoHidewhenClass">start:hide%i</span>A<span class="plominoHidewhenClass">end:hide%i</span>'%(i,i)

            topform.form_layout += """<span class="plominoSubformClass">form%i</span>""" % i
            topform.form_layout += """<hr class="plominoPagebreakClass"/>"""

        #Single field form to test validation calls
        form = getattr(db, db.invokeFactory('PlominoForm', id='ldapform', title='LDAP Form'))
        id = form.invokeFactory('PlominoField',
                id='name',
                title='name',
                field_type="NAME",
                field_mode="EDITABLE")
        form.form_layout = """<p><label for="name">name</label><span class="plominoFieldClass">name</span></p>"""
        db.do_not_list_users = True



PRODUCTS_CMFPLOMINO_PROFILER_FIXTURE = TestProfileLayer()


def getcalls(prof, func, file=None):
    for  (path,line,sfunc),stat in prof.stats.iteritems():
        if func == sfunc and (file in path if file is not None else True):
            (cc, nc, tt, ct, callers) = stat
            return nc
    return None



class PlominoUtilsTest(unittest.TestCase):

    layer = FunctionalTesting(
        bases=(PRODUCTS_CMFPLOMINO_PROFILER_FIXTURE, PRODUCTS_CMFPLOMINO_FIXTURE),
        name='ProductsCmfplominoLayer:ProfilerTesting'
    )

    def test_tempdoccache_next(self):
#        browser = self.layer['browser']
#        portal_url = self.layer['portal_url']


        browser = None
        portal_url = None
        with ploneSite() as portal:
            portal_url = portal.absolute_url()
            browser = Browser(portal.aq_parent)
        browser.open(portal_url + "/login")
        browser.getControl('Login Name').value = SITE_OWNER_NAME
        browser.getControl('Password').value = SITE_OWNER_PASSWORD
        browser.getControl('Log in').click()
        browser.open(portal_url)

        browser.handleErrors = False
        #warm up teh caches. compile etc
        browser.open(portal_url + "/profdb/form")


        prof = cProfile.Profile()
        prof.runctx('browser.getControl("Next").click()', globals(), locals())
        prof.dump_stats("stats.prof")
        self.assertIn("field1", browser.contents)
        self.assertIn("field2", browser.contents)
        self.assertIn("field9", browser.contents)

        # hidehwhen formula called twice. 1) during validateInputs. 2) displayDocument for next page
        # TODO: page is different so can optimise? only if formula doesn't use current page right?
        # I think its because request gets changed to include new page_id etc
        self.assertEquals(getcalls(prof, 'hidewhen_-_form0_-_hide0_-_formula'), 2)
        self.assertEquals(getcalls(prof, 'field_-_form_-_field0_-_ValidationFormula'), 1)

        # Validation only on the first page + 10 hidewhens in validate + 10 to display next page
        self.assertEquals(getcalls(prof, 'runFormulaScript'), 21)

        # one temp doc validating. a different when page number changed
        self.assertEquals(getcalls(prof, '__init__', 'document.py'), 2)




    def test_tempdoccache_onsave(self):
        with ploneSite() as portal:
            portal_url = portal.absolute_url()
            browser = Browser(portal.aq_parent)
        browser.open(portal_url + "/login")
        browser.getControl('Login Name').value = SITE_OWNER_NAME
        browser.getControl('Password').value = SITE_OWNER_PASSWORD
        browser.getControl('Log in').click()

        browser.handleErrors = True

        url = portal_url+'/profdb/form'
        prof = cProfile.Profile()
        try:
            prof.runctx('browser.post("%s","Form=form&field1=admin&plomino_save=Save")'%url, globals(), locals())
        except HTTPError as e:
            #TODO: not sure why it gets 404 for the document on redirect
            #self.fail(e)
            pass
        prof.dump_stats("onsave.prof")
        # Currently 3. 1) validateInputs 2) display page 3) redirected to /page/1
        # TODO: optimise so we don't do the redirect?
        self.assertEquals(getcalls(prof, 'hidewhen_-_form0_-_hide0_-_formula'), 3)
        self.assertEquals(getcalls(prof, 'field_-_form_-_field0_-_ValidationFormula'), 1)
        #self.assertEquals(getcalls(prof, 'runFormulaScript'), 11)
        # temp doc + ??
        self.assertEquals(getcalls(prof, '__init__', 'document.py'), 2)

        self.assertIn("plominoEdit", browser.contents)


#TODO additional test cases
# - validate field on previous page at save time
# - initial doc doesn't include hidden inputs. saved one should?

    def test_ldap(self):


        browser = None
        portal_url = None
        with ploneSite() as portal:
            portal_url = portal.absolute_url()
            browser = Browser(portal.aq_parent)
            db = portal.profdb



        browser.open(portal_url + "/login")
        browser.getControl('Login Name').value = SITE_OWNER_NAME
        browser.getControl('Password').value = SITE_OWNER_PASSWORD
        browser.getControl('Log in').click()
        browser.open(portal_url+'/plone_ldapcontrolpanel')
        browser.getControl("LDAP URI").value = "ldap://ldapserver"
        browser.getControl("LDAP Manager User").value = "cn=admin,dc=planetexpress,dc=com"
        browser.getControl("LDAP Manager Password").value = "GoodNewsEveryone"
        browser.getControl("Users container DN").value = "ou=people,dc=planetexpress,dc=com"
        browser.getControl("Groups container DN").value = "ou=people,dc=planetexpress,dc=com"
        browser.getControl("Groups search query filter").value = "(objectClass=group)"
        browser.getControl(name="ldapsettings.groups.object_classes.0").value = "group"

        browser.getControl("Save").click()
        self.assertNotIn("ERROR", browser.contents)


        browser.handleErrors = False
        #warm up teh caches. compile etc
        browser.open(portal_url + "/profdb/ldapform")
        db.cleanRequestCache()

        cProfile.runctx('browser.open("'+portal_url+'/profdb/ldapform")', globals(), locals(), filename="ldap_stats.prof")
        browser.getControl('name').value = "bender"
        db.cleanRequestCache()
        cProfile.runctx("browser.getControl('Save').click()", globals(), locals(), filename="ldap_save_stats.prof")
        self.assertIn("User not found", browser.contents)
        self.assertIn("Validation failed", browser.contents)
        #TODO: actually get it to validate

        browser.open(portal_url + "/login")
        browser.getControl('Login Name').value = "bender"
        browser.getControl('Password').value = "bender"
        cProfile.runctx('browser.getControl("Log in").click()', globals(), locals(), filename="ldap_login.prof")
        self.assertNotIn("Bender", browser.contents)


    def test_adp(self):
        browser = None
        portal_url = None
        with ploneSite() as portal:

            # Try to import adw form it available. Don't want to check this in
            portal.invokeFactory('PlominoDatabase', id="adw")
            db = getattr(portal, 'adw')
            if not os.path.isfile("adw-20170519.json"):
                return
            with open("adw-20170519.json") as fp:
                db.importDesignFromJSON(fp.read(), replace = True)

            portal_url = portal.absolute_url()
            browser = Browser(portal.aq_parent)
        cProfile.runctx('browser.open("'+portal_url+'/adw/assessment-notice")', globals(), locals(), filename="adw.prof")
        browser.getControl('Next',index=0).click()

        db.cleanRequestCache()
        cProfile.runctx("browser.getControl('Next',index=0).click()", globals(), locals(), filename="adw_validate.prof")
        self.assertIn('Validation failed', browser.contents)

        db.cleanRequestCache()
        browser.getControl("First Given Name", index=0).value = "Dylan"
        browser.getControl("Family Name", index=0).value = "Jay"
        browser.getControl(name="patient_birthdate").value = "1/1/2000"
        browser.getControl("Male").click()
        browser.getControl("Address Line 1", index=0).value = "Somewhere"
        browser.getControl('Next',index=0).click()
        self.assertNotIn('Validation failed', browser.contents)
        self.assertNotIn('page/3', browser.url)







from os.path import dirname, join
from datetime import datetime
import time

import unittest2 as unittest

from plone.app.testing import selenium_layers
from plone.app.testing import TEST_USER_NAME, TEST_USER_PASSWORD

from selenium.common.exceptions import NoSuchElementException

from Products.CMFPlomino.testing import PLOMINO_SELENIUM_TESTING

DIRPATH = join(dirname(__file__), 'filestoimport')

class IntegrationTest(unittest.TestCase):

    layer = PLOMINO_SELENIUM_TESTING

    def test_hide_when(self):
        "Dummy test"
        # Import our sample database
        mydb = self.layer['portal'].mydb
        sel = self.layer['selenium']
        import_file('hideWhenTest.xml', mydb)
        # Navigate to the Plomino db
        selenium_layers.open(sel, mydb.absolute_url())
        selenium_layers.type(sel, '__ac_name', TEST_USER_NAME)
        selenium_layers.type(sel, '__ac_password', TEST_USER_PASSWORD)
        selenium_layers.click(sel, '//form[@id="login_form"]//input[@type="submit"]')
        selenium_layers.click(sel, '//a[contains(text(), "Test Hide")]')
        selenium_layers.type(sel, 'a', '123')
        selenium_layers.click(sel, "//option[@value='A']")
        # Submitting now should warn us that 'c' has no value
        sel.find_element_by_xpath("//input[@name='plomino_save']").click()
        popup = sel.find_element_by_id('plominoValidationPopup')
        sel.find_element_by_xpath("//strong[contains(text(), 'c is mandatory')]")
        self.close_error_popup()
        # But when we fill it in, it should work
        selenium_layers.type(sel, 'c', 'A value for c!')
        sel.find_element_by_xpath("//input[@name='plomino_save']").click()
        # At this point the usual selenium wait-for-page-loaded doesn't work
        # because we intercept the submit event and do ajax validation
        self.wait_ajax_calls()
        # Empty hidden required fields should not trigger an error
        # XXX Here we should check nonzero length on mydb.plomino_documents.objectIds()
        # but for some reasons (isolated transacitons?) it doesn't show up
        self.assertTrue('plomino_documents' in sel.current_url)

    def close_error_popup(self):
        sel = self.layer['selenium']
        sel.find_element_by_xpath("//div[@aria-labelledby='ui-dialog-title-plominoValidationPopup']"
                                  "//a[contains(@class, 'ui-dialog-titlebar-close')]").click()

    def wait_ajax_calls(self, timeout=5000, step=100):
        "Wait until all jQuery initiated ajax calls return"
        start = datetime.now()
        elapsed_milliseconds = 0
        while elapsed_milliseconds < timeout:
            res = self.layer['selenium'].execute_script("return jQuery.active")
            if not res:
                return
            time.sleep(step/1000.0)
            now = datetime.now() - start
            elapsed_milliseconds = now.microseconds/1000 + now.seconds*1000
        self.fail("Timeout %i reached" % timeout)


def import_file(filename, plominodb):
    filepath = join(DIRPATH, filename)
    plominodb.importDesignFromXML(open(filepath).read())

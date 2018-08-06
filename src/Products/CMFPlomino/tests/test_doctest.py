import doctest

import transaction

from plone.app.testing import TEST_USER_ID, TEST_USER_NAME, TEST_USER_PASSWORD
from plone.testing import layered
from plone.testing.z2 import Browser

from Products.CMFPlomino.testing import PRODUCTS_CMFPLOMINO_FUNCTIONAL_TESTING

OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

doctest.set_unittest_reportflags(
    doctest.REPORT_NDIFF | doctest.REPORT_ONLY_FIRST_FAILURE)


def test_suite():
    suite = doctest.DocFileSuite(
        'plomino.txt',
        'plomino_accesscontrol.txt',
        'plomino_advanced.txt',
        'plomino_import_export.txt',
        'plomino_browser.txt',
        'plomino_file_attachment.txt',
        'plomino_view.txt',
        'plomino_linkto.txt',
        'plomino_action.txt',
        'plomino_index.txt',
        'plomino_formula.txt',
        'plomino_computed.txt',
        'plomino_search.txt',
        'plomino_field.txt',
        'plomino_selection.txt',
        'plomino_multi_page.txt',
        'plomino_field_validation.txt',
        'plomino_doclink.txt',
        # 'samples.txt',
        # 'plomino_usage.txt',
        # 'form-resources.txt',
        # 'searchableview.txt',
        globs={
            'TEST_USER_ID': TEST_USER_ID,
            'TEST_USER_NAME': TEST_USER_NAME,
            'TEST_USER_PASSWORD': TEST_USER_PASSWORD,
            'Browser': Browser,
            'transaction': transaction
        }, optionflags=OPTIONFLAGS
    )
    return layered(suite, layer=PRODUCTS_CMFPLOMINO_FUNCTIONAL_TESTING)

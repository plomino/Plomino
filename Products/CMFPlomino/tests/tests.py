import doctest

import transaction

from plone.app.testing import TEST_USER_ID
from plone.testing import layered
from plone.testing.z2 import Browser

from Products.CMFPlomino.testing import PLOMINO_FUNCTIONAL_TESTING

OPTIONFLAGS = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE

doctest.set_unittest_reportflags(
    doctest.REPORT_NDIFF | doctest.REPORT_ONLY_FIRST_FAILURE)


def test_suite():
    suite = doctest.DocFileSuite(
        'plomino.txt', 'plomino_accessControl.txt', 'samples.txt',
        'plomino_usage.txt',
        globs={
            'TEST_USER_ID': TEST_USER_ID,
            'Browser': Browser,
            'transaction': transaction
        }, optionflags=OPTIONFLAGS
    )
    return layered(suite, layer=PLOMINO_FUNCTIONAL_TESTING)

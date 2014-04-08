import unittest
from AccessControl.unauthorized import Unauthorized
from DateTime import DateTime
import Missing
from decimal import Decimal
from Products.CMFPlomino.testing import PLOMINO_FUNCTIONAL_TESTING
from  Products.CMFPlomino.config import TIMEZONE
import Products.CMFPlomino.PlominoUtils as utils


class DisplayFieldIndexTest(unittest.TestCase):

    layer = PLOMINO_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.db = self.portal.mydb
        self.db.invokeFactory('PlominoForm', id='frm1', title='Form 1')
        self.frm1 = self.db.frm1
        self.frm1.invokeFactory('PlominoField', id='a_field',
                                Title='Display Field',
                                FieldType="TEXT",
                                FieldMode="DISPLAY",
                                ToBeIndexed="True",
                                Formula="return 'spam'")
        self.field_obj = self.frm1.a_field
        self.field_obj.at_post_create_script()

    def test_indexed_attrs(self):
        doc1 = self.db.createDocument()
        doc1.setItem('Form', 'frm1')
        doc1.save()
        doc_id = doc1.id
        res = self.db.getIndex().dbsearch({'a_field': 'notspam'})
        self.assertEquals(len(res), 0)
        res = self.db.getIndex().dbsearch({'a_field': 'spam'})
        self.assertEquals(len(res), 1)
        #import pdb; pdb.set_trace()

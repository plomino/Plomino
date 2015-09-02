import unittest
from AccessControl.unauthorized import Unauthorized
from DateTime import DateTime
import Missing
from decimal import Decimal
from Products.CMFPlomino.testing import PRODUCTS_CMFPLOMINO_FUNCTIONAL_TESTING
from Products.CMFPlomino.config import TIMEZONE
from Products.CMFPlomino import utils


class PlominoUtilsTest(unittest.TestCase):

    layer = PRODUCTS_CMFPLOMINO_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.db = self.portal.mydb
        self.portal.portal_membership.addMember(
            "user1",
            'secret',
            ('Member',),
            '',
            {'fullname': "User 1", 'email': 'user1@dummy.fr', }
        )

    def test_DateToString(self):
        date = DateTime(2013, 10, 7)
        self.assertEqual(utils.DateToString(date), '2013-10-07')
        self.assertEqual(utils.DateToString(date, "%d/%m/%Y"), '07/10/2013')
        self.assertEqual(
            utils.DateToString(date, db=self.db),
            '2013-10-07'
        )

    def test_StringToDate(self):
        date = DateTime(2013, 10, 7)
        self.assertEqual(utils.StringToDate('2013-10-07') - date, 0)
        self.assertEqual(utils.StringToDate('07/10/2013', "%d/%m/%Y") - date, 0)
        self.assertEqual(
            utils.StringToDate('2013-10-07', db=self.db) - date,
            0
        )

    def test_DateRange(self):
        date1 = DateTime(2013, 9, 30)
        date2 = DateTime(2013, 10, 3)
        self.assertEqual(len(utils.DateRange(date1, date2)), 4)

    def test_Now(self):
        now = DateTime()
        self.assertAlmostEqual(utils.Now() - now, 0)

    def test_userFullname(self):
        self.assertEqual(utils.userFullname(self.db, "user1"), "User 1")
        self.assertEqual(utils.userFullname(self.db, "johncleese"), "Unknown")

    def test_userInfo(self):
        self.assertEqual(
            utils.userInfo(self.db, "user1").getProperty("email"),
            'user1@dummy.fr'
        )

    def test_PlominoTranslate(self):
        self.assertEqual(
            utils.PlominoTranslate("Access control", self.db),
            'Access control'
        )

    def test_htmlencode(self):
        self.assertEqual(
            utils.htmlencode(u"c'est \xe9vident"),
            u"c'est &eacute;vident"
        )

    def test_urlencode(self):
        self.assertEqual(
            utils.urlencode({'something': 10, 'nothing': 'zero'}),
            'nothing=zero&something=10'
        )

    def test_urlquote(self):
        self.assertEqual(
            utils.urlquote("this is an url"),
            'this%20is%20an%20url'
        )

    def test_cgi_escape(self):
        self.assertEqual(
            utils.cgi_escape("<&"),
            '&lt;&amp;'
        )

    def test_normalizeString(self):
        self.assertEqual(
            utils.normalizeString(u"C'est \xe9vident"),
            'cest-evident'
        )

    def test_asList(self):
        self.assertEqual(
                utils.asList("cheese"),
                ["cheese"])
        self.assertEqual(
                utils.asList(["cheese", "bacon", 10]),
                ["cheese", "bacon", 10])
        self.assertEqual(
                utils.asList([]),
                [])
        self.assertEqual(
                utils.asList(""),
                [""])
        self.assertEqual(
                utils.asList(None),
                [None])

    def test_asUnicode(self):
        self.assertEqual(
            utils.asUnicode(u"C'est \xe9vident"),
            u"C'est \xe9vident"
        )
        self.assertEqual(
            utils.asUnicode("C'est \xc3\xa9vident"),
            u"C'est \xe9vident"
        )
        self.assertEqual(
            utils.asUnicode(10),
            u"10"
        )

    def test_csv_to_array(self):
        # important: only strings in the result
        self.assertEqual(
            utils.csv_to_array('"abc"\t12\r\n"def"\t23\r\n'),
            [['abc', '12'], ['def', '23']]
        )
        self.assertEqual(
            utils.csv_to_array('"abc";12\r\n"def";23\r\n', delimiter=';'),
            [['abc', '12'], ['def', '23']]
        )

    def test_array_to_csv(self):
        self.assertEqual(
            utils.array_to_csv([['abc', 12], ['def', 23]]),
            '"abc"\t12\r\n"def"\t23\r\n'
        )
        self.assertEqual(
            utils.array_to_csv([['abc', 12], ['def', 23]], delimiter=';'),
            '"abc";12\r\n"def";23\r\n'
        )

    def test_open_url(self):
        self.assertRaises(
            Unauthorized,
            utils.open_url,
            "http://www.google.com",   
        )

    def test_MissingValue(self):
        self.assertEqual(
            utils.MissingValue(),
            Missing.Value
        )

    def test_isDocument(self):
        self.assertEqual(
            utils.isDocument(self.db.getForm('frm_test')),
            False
        )
        self.assertEqual(
            utils.isDocument(self.db.getDocument('doc1')),
            True
        )

    def test_json_dumps(self):
        self.assertEqual(
            utils.json_dumps({"a": [20, 3]}),
            '{"a": [20, 3]}'
        )
        dt = DateTime('2013/10/21 19:26:48 GMT+7')
        self.assertEqual(
            utils.json_dumps(dt),
            '{"<datetime>": true, "datetime": "2013-10-21T19:26:48+07:00"}'
        )

    def test_json_loads(self):
        self.assertEqual(
            utils.json_loads('{"a": [20, 3]}'),
            {"a": [20, 3]}
        )
        self.assertEqual(
            utils.json_loads('{"<datetime>": true, "datetime": "2013-10-21T19:26:48+07:00"}'),
            DateTime('2013-10-21T19:26:48+07:00').toZone(TIMEZONE)
        )

    def test_escape_xml_illegal_chars(self):
        self.assertEqual(
            utils.escape_xml_illegal_chars(u'this is \x00'),
            u'this is ?'
        )

    def test_decimal(self):
        self.assertEqual(
            utils.decimal(100.0),
            Decimal('100.0')
        )

    def test_is_email(self):
        self.assertEqual(
            utils.is_email("ebrehault@gmail.com"),
            True
        )
        self.assertEqual(
            utils.is_email("one@two"),
            False
        )

    def test_translate(self):
        self.assertEqual(
            utils.translate(
                self.db,
                "__my name__ will be translated"
            ),
            "my name will be translated"
        )

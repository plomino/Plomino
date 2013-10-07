import unittest

from DateTime import DateTime

from Products.CMFPlomino.testing import PLOMINO_FUNCTIONAL_TESTING
import Products.CMFPlomino.PlominoUtils as utils


class PlominoUtilsTest(unittest.TestCase):

    layer = PLOMINO_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.db = self.portal.mydb
        self.portal.portal_membership.addMember(
            "user1",
            'secret',
            ('Member',),
            '',
            {'fullname': "User 1", 'email': 'user1@dummy.fr',}
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
        self.assertTrue(utils.Now() - now < 1.0e-6)

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
            ["cheese"]
        )
        self.assertEqual(
            utils.asList(["cheese", "bacon"]),
            ["cheese", "bacon"]
        )
        self.assertEqual(
            utils.asList([]),
            []
        )
        self.assertEqual(
            utils.asList(""),
            [""]
        )
        self.assertEqual(
            utils.asList(None),
            [None]
        )
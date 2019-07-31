import transaction

import Missing
import unittest

import zc
from AccessControl.unauthorized import Unauthorized
from DateTime import DateTime
from decimal import Decimal

from plone import api
from zc.async.testing import wait_for_result
from zope.publisher.browser import TestRequest, BrowserResponse

from Products.CMFPlomino.config import TIMEZONE
from Products.CMFPlomino.testing import PRODUCTS_CMFPLOMINO_INTEGRATION_ASYNC_TESTING
from Products.CMFPlomino import utils
from plone.app.async.tests.base import AsyncTestCase
from zope.component import getUtility
from plone.app.async.interfaces import IAsyncService


def return42(context):
    return 42

class PlominoAsyncTest(AsyncTestCase):

    layer = PRODUCTS_CMFPLOMINO_INTEGRATION_ASYNC_TESTING

    def setUp(self):
        self.async = getUtility(IAsyncService)
        #self.login()
        #self.setRoles(['Manager'])
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.db = self.portal.mydb

    def tearDown(self):
        pass

    def test_p_a_async(self):
        job = self.async.queueJob(return42, self.app)
        transaction.commit()
        wait_for_result(job)
        self.assertEqual(job.result, 42)

    def test_queue_form(self):

        form = self.db.frm_test
        form.onDisplay = """return 42"""

        job_id = self.db.getParentDatabase().queue_run(form)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertEqual(result, 42)

    def test_queue_document(self):

        form = self.db.frm_test
        form.onDisplay = """return 42"""
        doc1 = self.db.createDocument()
        doc1.save(form)

        job_id = self.db.getParentDatabase().queue_run(doc1)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertEqual(result, 42)

    def test_queue_form_with_doc(self):

        form = self.db.frm_test
        form.onDisplay = """return plominoContext.field_1"""
        doc1 = self.db.createDocument()
        doc1.field_1 = 42

        job_id = self.db.getParentDatabase().queue_run(form, doc1)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertEqual(result, 42)

    def test_queue_form_with_exception(self):

        form = self.db.frm_test
        form.onDisplay = """raise Exception()"""

        job_id = self.db.getParentDatabase().queue_run(form)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertIsInstance(result, zc.twist.Failure)


    def test_queue_script(self):

        formula = """return 42"""

        job_id = self.db.getParentDatabase().queue_run(formula)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertEqual(result, 42)

    def test_queue_script_with_args(self):

        formula = """##parameters=x,y\nreturn x*y"""
        doc1 = self.db.createDocument()
        doc1.field_1 = 42

        job_id = self.db.getParentDatabase().queue_run(formula, x=6, y=7)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertEqual(result, 42)

    def test_queue_script_with_doc(self):

        formula = """return context.field_1"""
        doc1 = self.db.createDocument()
        doc1.field_1 = 42

        job_id = self.db.getParentDatabase().queue_run(formula, doc1)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertEqual(result, 42)

    def test_queue_script_with_exception(self):

        formula = """raise Exception()"""

        job_id = self.db.getParentDatabase().queue_run(formula)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertIsInstance(result, zc.twist.Failure)



    def test_queue_agent(self):

        agent = api.content.create(
            type='PlominoAgent',
            id='myagent',
            title='myagent',
            content="""return 42""",
            container=self.db)

        job_id = self.db.getParentDatabase().queue_run(agent)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertEqual(result, 42)


    def test_queue_agent_with_args(self):

        agent = api.content.create(
            type='PlominoAgent',
            id='myagent2',
            title='myagent',
            content="""return args[0]""",
            container=self.db)

        job_id = self.db.getParentDatabase().queue_run(agent, None, 42)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertEqual(result, 42)

    def test_queue_agent_with_exception(self):

        agent = api.content.create(
            type='PlominoAgent',
            id='myagent3',
            title='myagent',
            content="""raise Exception()""",
            container=self.db)

        job_id = self.db.getParentDatabase().queue_run(agent, None, 42)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job, 10)

        status, result = self.db.queue_status(job_id)
        self.assertIsInstance(result, zc.twist.Failure)
        #self.assertRegexpMatches(repr(result), "<zc.twist.Failure exceptions.Exception: RuntimeError: Script (Python) agent.*")


    def test_queue_from_formula(self):
        """Tests adding a computational job in a formula and getting the result.
        """

        # create a form that will submit a job on save
        form = self.db.frm_test
        form.preventSaveOnError = True
        form.onSaveDocument = \
            "formula='return 42'\n" +\
            "with plominoContext.getParentDatabase().runAsOwner():\n"+\
            "    job_id = plominoContext.getParentDatabase().queue_run(formula)\n" +\
            "plominoDocument.setItem('job_id', job_id)\n" +\
            "return job_id"
        doc1 = self.db.createDocument()
        doc1.save(form)
        job_id = doc1.getItem('job_id', {})
        self.assertTrue(job_id)

        # now we can retrieve the job id and see the status
        status, result = self.db.queue_status(job_id)
        self.assertEqual(status, u'pending-status')

        transaction.commit()
        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertEqual(status, u'completed-status')
        self.assertEqual(result, 42)
        transaction.commit()

    def test_queue_field(self):

        form = self.db.frm_test
        form.field_1.formula = """return 42"""

        job_id = self.db.getParentDatabase().queue_run(form.field_1)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertEqual(result, 42)

    def test_queue_field_with_exception(self):

        form = self.db.frm_test
        form.field_1.formula = """raise Exception()"""

        job_id = self.db.getParentDatabase().queue_run(form.field_1)
        transaction.commit()

        _, job = self.db._find_job(job_id)
        wait_for_result(job)

        status, result = self.db.queue_status(job_id)
        self.assertIsInstance(result, zc.twist.Failure)


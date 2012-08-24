import unittest
from Products.CMFPlomino.testing import PLOMINO_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer

from Products.CMFPlomino.tests.schemaextender.importexport import ExtendedFieldImportExporter

class SchemaExtenderLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        super(SchemaExtenderLayer, self).setUpZope(app, configurationContext)
        # Load ZCML for a product that uses atschemaextender to add a field
        # to the "Field" Plomino content
        # and sets up an adapter to import/export the extended fields
        import Products.CMFPlomino.tests.schemaextender
        self.loadZCML(package=Products.CMFPlomino.tests.schemaextender)

SCHEMAEXTENDER_FIXTURE = SchemaExtenderLayer()
PLOMINO_SCHEMAEXTENDER_TESTING = IntegrationTesting(bases=(SCHEMAEXTENDER_FIXTURE,PLOMINO_FIXTURE), name="Plomino:SchemaExtender")

class IntegrationTest(unittest.TestCase):

    layer = PLOMINO_SCHEMAEXTENDER_TESTING

    def create_field(self):
        mydb = self.layer['portal'].mydb
        mydb.invokeFactory('PlominoForm', id='frm1', title='Form 1')
        frm1 = mydb.frm1
        frm1.invokeFactory('PlominoField', id='a_field', Title='I am extended!',
                            FieldType="TEXT", FieldMode="EDITABLE")
        fieldobj = frm1.a_field
        fieldobj.at_post_create_script()
        schema = fieldobj.Schema()
        self.assertTrue('extension_field' in schema.keys())
        schema['extension_field'].set(fieldobj, 'A value for the custom field')

    def test_adapter(self):
        self.create_field()
        field = self.layer['portal'].mydb.frm1.a_field
        adapter = ExtendedFieldImportExporter(field)
        xml = adapter.export_xml()
        self.assertTrue("A value for the custom field" in xml)
        xml = xml.replace("A value for the custom field", "A NEW VALUE")
        adapter.import_xml(xml)
        self.assertEqual(field.Schema()['extension_field'].get(field), "A NEW VALUE")

    def test_export_extended_fields(self):
        self.create_field()
        mydb = self.layer['portal'].mydb
        xml = mydb.exportDesignAsXML()
        self.assertTrue('A value for the custom field' in xml)
        xml = xml.replace("A value for the custom field", "A NEW VALUE")
        mydb.importDesignFromXML(xml)
        field = self.layer['portal'].mydb.frm1.a_field
        self.assertEqual(field.Schema()['extension_field'].get(field), "A NEW VALUE")

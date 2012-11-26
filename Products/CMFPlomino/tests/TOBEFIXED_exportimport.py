import unittest
from Products.CMFPlomino.testing import PLOMINO_FIXTURE
from plone.app.testing import FunctionalTesting
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
PLOMINO_SCHEMAEXTENDER_TESTING = FunctionalTesting(bases=(SCHEMAEXTENDER_FIXTURE,PLOMINO_FIXTURE), name="Plomino:SchemaExtender")

class ExportImportTest(unittest.TestCase):

    layer = PLOMINO_SCHEMAEXTENDER_TESTING
    FIELD_CONTENT = '>>A value for the custom field'
    XML_FIELD_CONTENT = FIELD_CONTENT.replace('>', '&gt;')

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
        schema['extension_field'].set(fieldobj, self.FIELD_CONTENT)

    def test_adapter(self):
        field = self.layer['portal'].mydb.frm1.a_field
        adapter = ExtendedFieldImportExporter(field)
        xml = adapter.export_xml()
        self.assertTrue(self.XML_FIELD_CONTENT in xml)
        xml = xml.replace(self.XML_FIELD_CONTENT, "A NEW VALUE")
        adapter.import_xml(xml)
        self.assertEqual(field.Schema()['extension_field'].get(field), "A NEW VALUE")

    def test_export_extended_fields(self):
        mydb = self.layer['portal'].mydb
        xml = mydb.exportDesignAsXML()
        self.assertTrue(self.XML_FIELD_CONTENT in xml)
        xml = xml.replace(self.XML_FIELD_CONTENT, "A NEW VALUE")
        mydb.importDesignFromXML(xml)
        field = self.layer['portal'].mydb.frm1.a_field
        self.assertEqual(field.Schema()['extension_field'].get(field), "A NEW VALUE")

    def test_export_extended_empty_fields(self):
        # Ensure that empty fields are imported/exported correctly as well.
        mydb = self.layer['portal'].mydb
        frm1 = mydb.frm1
        frm1.invokeFactory('PlominoField', id='another_field', Title='I am extended too',
                            FieldType="TEXT", FieldMode="EDITABLE")
        fieldobj = frm1.another_field
        fieldobj.at_post_create_script()
        fieldobj.Schema()['extension_field'].set(fieldobj, '')

        xml = mydb.exportDesignAsXML()
        fieldobj.Schema()['extension_field'].set(fieldobj,
            'Overwrite me in the next line!')
        mydb.importDesignFromXML(xml)

        field = self.layer['portal'].mydb.frm1.another_field
        self.assertEqual(field.Schema()['extension_field'].get(field), "")

    def setUp(self):
        self.create_field()

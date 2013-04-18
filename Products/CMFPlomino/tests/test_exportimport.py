import unittest

import OFS

from Products.CMFPlomino.testing import PLOMINO_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer

from Products.CMFPlomino.tests.schemaextender.importexport import ExtendedFieldImportExporter

class SchemaExtenderLayer(PloneSandboxLayer):
    defaultBases = (PLOMINO_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        super(SchemaExtenderLayer, self).setUpZope(app, configurationContext)
        # Load ZCML for a product that uses atschemaextender to add a field
        # to the "Field" Plomino content
        # and sets up an adapter to import/export the extended fields
        import Products.CMFPlomino.tests.schemaextender
        self.loadZCML(package=Products.CMFPlomino.tests.schemaextender)

SCHEMAEXTENDER_FIXTURE = SchemaExtenderLayer()
PLOMINO_SCHEMAEXTENDER_TESTING = FunctionalTesting(bases=(SCHEMAEXTENDER_FIXTURE,), name="Plomino:SchemaExtender")


class ExportImportTest(unittest.TestCase):

    layer = PLOMINO_SCHEMAEXTENDER_TESTING
    FIELD_CONTENT = u'\u2794 A value for the custom field'
    ALTERNATIVE_CONTENT = u"A NEW VALUE \u2794"
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
        xml = adapter.export_xml().decode('utf8')
        self.assertTrue(self.XML_FIELD_CONTENT in xml)
        xml = xml.replace(self.XML_FIELD_CONTENT, self.ALTERNATIVE_CONTENT)
        adapter.import_xml(xml.encode('utf8'))
        fieldvalue = field.Schema()['extension_field'].get(field)
        self.assertEqual(unicode(fieldvalue, 'utf8'),
                         self.ALTERNATIVE_CONTENT)

    def test_export_extended_fields(self):
        mydb = self.layer['portal'].mydb
        xml = mydb.exportDesignAsXML().decode('utf8')
        self.assertTrue(self.XML_FIELD_CONTENT in xml)
        xml = xml.replace(self.XML_FIELD_CONTENT, self.ALTERNATIVE_CONTENT)
        mydb.importDesignFromXML(xml.encode('utf8'))
        field = self.layer['portal'].mydb.frm1.a_field
        fieldvalue = field.Schema()['extension_field'].get(field)
        self.assertEqual(unicode(fieldvalue, 'utf8'),
                         self.ALTERNATIVE_CONTENT)

    def test_export_extended_empty_fields(self):
        # Ensure that empty fields are imported/exported correctly as well.
        mydb = self.layer['portal'].mydb
        frm1 = mydb.frm1
        frm1.invokeFactory('PlominoField', id='another_field', Title='I am extended too',
                            FieldType="TEXT", FieldMode="EDITABLE")
        fieldobj = frm1.another_field
        fieldobj.at_post_create_script()
        fieldobj.Schema()['extension_field'].set(fieldobj, '')

        xml = mydb.exportDesignAsXML().decode('utf8')
        fieldobj.Schema()['extension_field'].set(fieldobj,
            'Overwrite me in the next line!')
        mydb.importDesignFromXML(xml.encode('utf8'))

        field = self.layer['portal'].mydb.frm1.another_field
        self.assertEqual(field.Schema()['extension_field'].get(field), "")

    def test_export_folder_in_resources(self):
        mydb = self.layer['portal'].mydb
        mydb.resources.manage_addFolder('test_folder')
        mydb.resources.test_folder.manage_addFolder('test_subfolder')
        xml = mydb.exportDesignAsXML()
        # Now delete the fodlers and check they are created back again
        mydb.resources.manage_delObjects(['test_folder'])
        mydb.importDesignFromXML(xml, replace=True)
        self.assertTrue('test_folder' in mydb.resources)
        folder = mydb.resources.test_folder.aq_base
        self.assertTrue(isinstance(folder, OFS.Folder.Folder))
        self.assertTrue('test_subfolder' in mydb.resources.test_folder)
        subfolder = folder.test_subfolder
        self.assertTrue(isinstance(subfolder, OFS.Folder.Folder))

    def test_empty_file(self):
        mydb = self.layer['portal'].mydb
        mydb.resources.manage_addFile('an_empty_file')
        xml = mydb.exportDesignAsXML()
        mydb.importDesignFromXML(xml, replace=True)

    def setUp(self):
        self.create_field()

These are the tests in this repo.

Doc tests
=========


General doc tests
=================

Refer more on test_doctest.py

- plomino.txt
  - getForm
  - getView
  - createDocument
  - getDocument
  - @@OpenForm
  - @@OpenBareForm
  - plomino_form_mode = READ
  - scripts from ``resources``
  - import script in scripts from ``resources``
  - include script in scripts from ``resources``
  - search form (search_view)
  - searchDocuments
  - setItem (add any type of item in a document)
  - getItem
  - can access item values as attributes
  - displayDocument
  - save(creation=True)
  - save()
  - Title()
  - dynamic_document_title
  - document_id
  - getAllDocuments in view
  - getDocumentsByKey in view
  - exportCSV in view
  - document can be exported as JSON
  - export only one field as JSON in document
  - get the ``lastmodified`` value as JSON in document
  - Text field
  - Selection field
  - Date/Time field
  - Number field
  - Rich-text field
  - Name field
  - Datagrid field
  - field mapping in Datagrid field
  - Computed field in text field
  - Computed field in selection field
  - Display computed field in selection field
  - cleanRequestCache()
  - getForm_layout()
  - setForm_layout()
  - validateInputs
  - Visual form layouts
    - Convert visual TinyMCE layout back to Plomino
    - Convert action, field and subform back to the right elements
    - Labels may or may not have custom text
    - Labels may have a field inside of them
    - A subform should appear inside the parent form
    - But the parent form shouldn't break with an empty sub-form
    - Or if there is no sub-form
  - Events
    - onCreateDocument
    - onOpenDocument
    - onSaveDocument
    - onDeleteDocument
  - Plomino index
    - dbsearch
    - getIndex().indexes()
    - column can be a reference to a field
    - key column in view
    - rename a view using `manage_renameObject`
    - rename a column using `manage_renameObject`
    - change the type of a column
    - Things shouldn't break if a column indexes a field with the same name as a form
    - can delete columns and have content indexed fine
- plomino_accesscontrol.txt
  Test adding different users for Plomino database
  Test adding group
  Test plomino roles and permissions
  Test adding an agent which will run as its owner
  Test plomino reader
  Test plomino author
  Test plomino editor
  Test author right for groups
  Test Plomino_Authors
  Test Plomino_Readers
- plomino_advanced.txt
  Test mandatory field in sub-form
  - in single-page form
  - in multi-page form
- plomino_import_export.txt
  - exportDesignAsJSON
  - exportDesign
  - importDesignFromJSON
  - exportDesignAsZip
  - importDesignFromZip
- plomino_browser.txt
  Testing using browser to
  - create new document
  - Plomino escape the backward slash, angle bracket, ampersand, cannot see the different between plus and space
  - generate view using 'manage_generateView' API
  - search form
  - name field search
  - Do not list user setting
- plomino_file_attachment.txt
  Test mandatory in both multi and single attachment
  - in single-page form
  - in single-page document
  - in multi-page form
  - in multi-page document
  - in sub-form
  - in single-page page
  - in multi-page page
  Test manually remove temporary folder and single-page form can save
  successully
  Test to check if another anonymous user cannot view your temporary file
- plomino_view.txt
  Test when csv export in view, the multi select data is readable in csv file
  Test unindexing document after deleted
- plomino_hidewhen.txt
  Test mandatory field validation inside hidewhen
  - in single-page
  - in multi-page
  - in sub-form
- plomino_index.txt
  Test dbsearch is still working after db is rename
- plomino_formula.txt
  Test on display formula for single-page and multi-page form
- plomino_linkto.txt
  Test plominoLinkto button in and multi-page form


Doc tests with macros
=====================

Refer more on test_doctest_with_macro.py

- plomino_macros.txt
  Test condition 'do', 'if', 'and', 'or', 'not', reverse order
  Test preserved custom code in validation_formula
  Test 'to_if' method
  Test macros:
  - Number in range
  - Invalid

- plomino_browser_with_macros.txt
  Check if selection formula is created from macro and manual formula from old code is not inserted
- defaultmacros/plomino_macro_field_selection_db_elements.txt
  Test 'Selection of elements from the current form/field' macro in 'Is email'
  macro able to show all fields in main and sub forms.

Robot tests
===========

- robot/description_datagrid.robot
- robot/description_dynamic.robot
- robot/description_plominodatabase.robot
- robot/description_redirect.robot
- robot/description_views.robot
- robot/description_workflow.robot
- robot/test_datagrid.robot
- robot/test_dynamic.robot
- robot/test_plominodatabase.robot
- robot/test_redirect.robot
- robot/test_validate.robot
- robot/test_views.robot
- robot/test_workflow.robot

Unit tests
==========


- test_doctest.py
  It just setup doc tests.
- test_doctest_with_macro.py
  It setup doc tests with macros.
- test_robot.py
  It setup robot tests under robot folder.

- test_plominodatabase.py
  Nothing here. Not in used.
- test_view.py
  Duplicate doc test for `plomino_view.txt`, it should be removed.

- test_plominoutils.py
  Test utils methods in Plomino
  - isDocument
- test_profile_subforms.py
  Test the number of the called method using cProfile
  - test_tempdoccache_next
  - test_tempdoccache_onsave
  - test_ldap
  - test_adp

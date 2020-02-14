Changelog
=========

PretaForm Releases
==================

0.9.34.dev0 (unreleased)
------------------------

- Fix dragging and dropping of existing elements within the TinyMCE editor [jeffersonbledsoe]
- Fix dragging vertical resizer not keeping up with mouse movemetns [jeffersonbledsoe]
- Remove the database ID from a database export [jeffersonbledsoe]
- Upgrade TypeScript to 3.7.5 [jeffersonbledsoe]
- Add ESlint rules [jeffersonbledsoe]

0.9.33 (2020-01-23)
-------------------

- Fix issue with script caching [instification]
- Add aria-hidden attribute to tree view icons [jeffersonbledsoe]

0.9.32 (2019-12-08)
-------------------

- Allow the customisation of a docklink's columns order [jeffersonbledsoe]
- Fix the initial size of the "select subform" dropdown [jeffersonbledsoe]
- Fix being able to select the current form as a subform [jeffersonbledsoe]
- Fix close button js on datagrid modal [quang]
- Make PlominoDocument.save safe to use when running in async [jeffersonbledsoe]

0.9.31 (2019-11-13)
-------------------

- Make alert dialogs more specific [jeffersonbledsoe]
- Move CI to GitHub Actions [JeffersonBledsoe]
- Add validation and tests for multiselect fields [jeffersonbledsoe]

0.9.30 (2019-09-27)
-------------------

- Import/Export resources as separate files [instification]

0.9.29 (2019-09-16)
-------------------

- Fix bug where whitespace causes redirect actions to fail [instification]
- Respect validation_mode when handling temporary documents [instification]
- Validate selection input [instification]
- Fix issue when checking user rights. #178 [instification]

0.9.28 (2019-7-31)
------------------

- Fix pickling issue with async jobs [instification]

0.9.27 (2019-05-07)
-------------------

- Add support for plone.app.async [djay]

0.9.26 (2019-03-06)
-------------------

- Update email validation to be RFC5322 compliant [instification]

0.9.25 (2019-02-18)
-------------------

- Fix datagrid column of docklink display document field out of order [quang]
- Display info message when search result is empty [quang]
- Enable 'Allow other value' on selection field using select2 widget [quang]
- Optionally don't display results on initial search form load. New setting [quang]
- Display DB name in IDE title bar [quang]

0.9.24 (2018-12-24)
-------------------

- Add datagrid style widget to doclinks [djay]
- Add the ability to add and edit documents in a popup when using datagrid widget with doclinks [djay]
- Enable caching on value return by selectionlist field [quang]
- Extend datagrid widget for doclink to select and display document [quang]

0.9.23 (2018-12-07)
-------------------

- Remove getSelectionList from doclink [quang]
- Add option to not load data on search form on intial display [quang]
- Fix timeout issue with searching docklink on-the-fly [quang]
- Add 'Allow other value' option to selection fields to alow add new option on-the-fly [quang]
- Add 'Unique field values' macro to select unique values stored of given document field [quang]
- Limit number of search item to 20 per page [quang]
- Fix close button on the datagrid popup not closing [quang]
- Remove error message displaying in console when docklink is used with widget rather than multi-select [quang]
- Fix select2 exception when on-the-fly searching return results containing empty display text [quang]

0.9.22 (2018-07-13)
-------------------

- Fix next page not appearing on search page [djay]
- Views and searchs links to documents work properly and close will go back [djay]
- Left over indexes no longer result in no data displayed in views [djay]
- Searches should render more kinds of fields properly [djay]
- fix selection fields in search forms [djay]

0.9.21 (2018-06-22)
-------------------

- Fix 'selection field not saving data' while editing documents by how missing values are process for booleans, doclinks and selection when its an add form. [quang]
- Export agents to zip file [instification]
- Edit document button goes to current page [quang]

0.9.20 (2018-01-29)
-------------------

- Update CMFPlone to 5.0.9 [quang]

0.9.19 (2017-12-20)
-------------------

- Fix redirect macro regression. Set default code value. [instification]
- Fix error while saving form with selection list by adding default value to selectionlistformula [quang]
- Fix to better handle form refreshes and browser button navigation [quang, instification]


0.9.18 (2017-12-07)
-------------------

- revert: cache and optmise calls to validation and hidewhen formulas and temporary document creation during form load, and next page. Further optimisaiton on save required. [djay]
- Set default redirect_type value in redirect_onsave macro. Fixes previous regression in redirect macros [instification, quang]

0.9.17 (2017-12-01)
-------------------

- Update macro redirect_on_save to have a separate choice for redirect on_save and on_load [quang]
- cache and optmise calls to validation and hidewhen formulas and temporary document creation during form load, and next page. Further optimisaiton on save required. [djay]
- Update do_not_list_user DB setting to follow Plone many_user setting [quang]

0.9.16 (2017-11-29)
-------------------

- Re-index document after renaming database using event subscription [quang]
- Fix error with selectionlistformula lost while saving field layout by add property NO_CHANGE to selection widget [quang]
- Add event subscriber to unindex document after being deleted [quang]
- Call to unindexing document after being indeleted regardless it is deleted with Plone API or not [quang]
- Fix regression with form onDisplay to accept different type of returned value [quang]

0.9.15 (2017-11-14)
-------------------

- Fix to ide when loading large forms [quang]
- Fix "Filter View by Form' macro causing an unresponsive error [quang]
- Improvement to 'redirect' macro, providing submitted data to target forms [quang]
- Merge 'redirect on save' and 'redirect on load' into one macro [quang]

0.9.14 (2017-11-14)
-------------------

- Fix to respect Plone Setting many_user or service setting do_not_list_users enabled [quang]
- Handle file attachments being cleared during validation errors in single and multipage forms [quang]
- Recompile Plomino for attachment script [quang]
- Remove select user macro [ivanteoh]

0.9.13 (2017-10-23)
-------------------

- Fix dynamic rendering computed on display text broken [ivanteoh]
- Fix hide checkbox in search view based from view [ivanteoh]
- Fix to view from form when custom theme is used [quang]
- Fix to re-ordering columns when custom theme is used [quang]

0.9.12 (2017-10-18)
-------------------

- Bugfix for dynamic evaluation and hidewhens [instification]

0.9.11 (2017-10-18)
-------------------

- Bug fix for extra space on triple quote statement [ivanteoh]
- Allow user to submit document, redirect to another form and access the document in that form [quang]
- Fix only last item in array is passed to dynamic_evaluation URL [ivanteoh]
- Fix missing code in IDE dynamic.js for reseting data in a hidewhen [ivanteoh]
- Fix refresh macro bug [quang]

0.9.10 (2017-10-02)
-------------------

- Further fixes to datagrid field mapping bugs [quang]
- Fix but where selection list formula is not showing in the IDE [quang]
- Display list values nicely during CSV export [ivanteoh]
- Add IDE feature to generate view from form with selected fields [quang]
- Fix to export function, causing additional lines in exported python [djay]
- Add search form functionality [quang]

0.9.9 (2017-09-25)
------------------

- Add test case for Plomino Browser, testing escape characters [quang]
- Fix a bug when closing the input dialog of a datagrid [quang]
- Fix the parsing of formid preventing users from editing a datagrid row [quang]
- Fix datagrid field mapping bugs [quang]
- Add multiple tests [apallar]

0.9.8 (2017-09-25)
------------------

- Fix bug that open new form when closing modal input dialog of datagrid [quang]
- Fix the parsing formid in input sent from server that prevent user from editing datagrid row [quang]
- Fix datagrid screwing up data when field mapping is set [quang]
- Fix exception issue with IDE when adding new column, re-ordering column in view [quang]
- Apply macro select_db_element to conditional macro to enable select field from subform [quang]

0.9.7 (2017-09-11)
------------------

- Allow select field from sub-form [quang]
- Modify macro select_db_element to allow select field from subform [quang]
- Fix the macros for field selection such that they let you pick all fields including those in any form or subsubforms [quang]
- Add test case for Plomino Browser, which test on escape characters [quang]
- fix handling of empty values in datagrid rendering [instification]
- Add dynamic title for macro 'Match text' that will display as 'Field-name contains expression-value'

0.9.6 (2017-09-04)
------------------

- fix sync of catalog when deleting views and columns and prevent leftover metadata columns from preventing saves [djay]
- Remove macro 'Select user data' to move it outside of basic macros [quang]

0.9.5 (2017-08-31)
------------------

- Allow select 'current field' from selection field macro [quang]
- Allow macro condition field to select 'current field' from field list [quang]
- Add Match text macro that support platform-dependant regular expression library [quang]
- Modify macro_number_range to use single field [quang]
- Modify macro select_db_element to allow select field from subform [quang]

0.9.4 (2017-08-28)
------------------

- fields with the same name forms/views no longer cause problems when used in view columns [djay]
- Bug fixes to macros [quang]
- Bug fixes to views [ivanteoh]
- Test suite improvements [ivanteoh]
- Bug fix for set permission macro [ivanteoh]
- Bug fixes to import/export [quang]

0.9.3 (2017-08-25)
------------------

- Fix exception issue with IDE when adding new column, re-ordering column in view [quang]
- Display lists from selection field in a text field in a nice way[quang]
- fixed a bug in openbareform that was preventing pdfs from rendering [djay]


0.9.2 (2017-08-23)
------------------

- fixed exception caused by unicode in Title when inserted into a label in the final html [ivanteoh]
- fixed "saving form scrolls to top. Also editing label then clicking field scrolls to the top" [ivanm]
- fix errors in catalog indexes caused by views or columns containing '_' and also being renamed.
  Renaming either now updates the indexes. [djay]
- new multi-file import/export format which seperates formulas and layouts into .py and .html files [quang]
- fix errors caused by runasowner when script is called inside a script [ivanteoh]


0.9.1 (2017-08-23)
------------------

- Edit document button goes to current page [quang]
- Restore View custom template
- Unquote plus signs when reading input [instification]
- Add option to send plain text emails [instification]
- CSV download macro can now be used on ViewA to download data from ViewB [ivanteoh]
- fixed IDE issues with reordering and adding removing macros [ivanm]
- Refresh code editor on save if is not dirty [ivanm]
- Fix "hang when creating new form from editor (+ icon next to tabs)" [ivanm]


Plomino Open Source Changes
===========================

2.0b4 (2016-05-27)
------------------

- Fix element portlet


2.0b3 (2016-05-10)
------------------

- Form formula
- Fix computed columns in datagrid
- Restore bare read/edit doc and bare form rendering


2.0b2 (2016-04-14)
------------------

- Fix columns ordering
- Fix formula editor


2.0b1 (2016-04-13)
------------------

- Restore design portlet.
  [ebrehault]


2.0a6 (2016-03-25)
------------------

- Fix hidden columns.
  [ebrehault]


2.0a5 (2016-03-23)
------------------

- Datagrid
  [ebrehault]

2.0a4 (2016-01-06)
------------------

- Create modal database design view [instification]

2.0a3 (2015-09-29)
------------------

- Hidewhen and subforms
  [ebrehault]

2.0a2 (2015-09-08)
------------------

- Design import/export from/to JSON
  [ebrehault]

2.0a1 (2015-09-02)
------------------

- Plone 5 compliancy (WIP)
  [ebrehault]

1.19.5 (unreleased)
-------------------

- Enable fields validation in Page forms [ebrehault]
- Allow to define a custom JS validation callback (window.plomino_custom_validation_callback) [ebrehault]

1.19.4 (2015-04-10)
-------------------

- Fix isCurrentUserAuthor (the doc creator is always Onwer, so we should test Plone rights
  in the db context, not the doc) [ebrehault]


1.19.3 (2015-02-27)
-------------------
- Fix sorting of view docs [jean]
- Fix importDesignFromZip for when there are script resources [jean]
- Generate canonical URLs for local resources [jean]

1.19.2 (2015-01-09)
-------------------
* Forgot to bump the version string [jean]

1.19.1 (2015-01-06)
-------------------
* Enable standard behaviour when looking up portal_skins resources [jean]

1.19 (2014-10-15)
-----------------
* Allow to post data with open_url util [manuelep]
* Enable multiple file upload [robystar]
* Fixes [ebrehault, ivant, fulv, gaudenz]

1.18.6 (2014-04-10)
-------------------
* Datagrid inline editing [davisp1]
* jQuery-ui datepicker widget for DATETIME fields [manuelep]
* Redirect on save document if a value for plominoredirecturl is specified in
  request [manuelep]
* Make views searchable: accept a query as URL parameter [manuelep]
* Inject computed HTML attributes based on name, and not id [manuelep]
* Allow indexing of computed display fields [djay, ivant]

1.18.5 (2013-12-04)
-------------------
* Working on BaseField.getFieldValue, handling of field defaults

1.18.4 (2013-11-29)
-------------------
* Fix few Chameleon compatibility issues
* Improve document properties page
* Split key column from sort column
* Remove Close action from views

1.18.3 (2013-11-04)
-------------------
* Fix getFieldValue

1.18.2 (2013-10-29)
-------------------
* Optimize TemporaryDocument
* Fixes for dates and decimal

1.18.1 (2013-10-24)
-------------------
* Fix timezone support in date conversion
* Fix temporary doc behaviour when evaluation hide-when

1.18 (2013-10-15)
-----------------
* support for labels associated to fields
* disabled formula editing for PlominoDesigner (so we can allow a user to change
  form layouts without breaking the formulas)
* fix a major vulnerability in open_url (now, targeted sources must be declared
  safe from an local package)
* allow to load specific CSS and JS in a PlominoForm
* GenericSetup import/export for Plomino db marked as templates
* allow to inject HTML attributes on fields
* extended translation support for views

1.17.5 (2013-09-24)
-------------------
* Reorder validation, so that submitted values can be
  massaged [jean]
* Enable Views to use field rendering [jean]
* Allow forms to specify their HTTP submit method [jean]

1.17.4 (2013-09-11)
-------------------
* Dynamic titles [jean]
* Add labels in layout [jean]
* add import from zip function for database design [davismr]
* add export as zip function for database design [davismr]
* fix missing encoding on exportCSV view [jpcw]

1.17.3.1 (2013-05-28)
---------------------
* filtering feature in datatabse design tab [davisp1]

1.17.3 (2013-05-28)
-------------------
* Depend on zope.app.component and zope.globalrequest
  so that our users on Plone 4.0 don't have to [silviot]
* Test Plone 4.0, 4.1, 4.2 and 4.3 on travis [silviot]
* Don't choke on XML import when there is an empty file
* Hide/display checkboxes in views
* Make sure formulas are compiled with db manager rights
* context.abortOnError() API
* use coveralls.io for test coverage reporting

1.17.2 (2013-04-08)
-------------------
* EditBareDocument template
* Add headers (based on fields titles) on datagrid in static mode
* Fix action bar displaying at both top and bottom

1.17.1 (2013-03-28)
-------------------
* Fix batching in dynamic view

1.17 (2013-03-20)
-----------------
* Add Boolean field type
* Add onBeforeSave event
* Date serialization support in the JSON API
* Give access to i18n support directly from Plomino forms and fields
* Pass JQueryUI dialog settings through datagrid field configuration
* Fix "run as owner" agent behavior

1.16.4 (2013-01-16)
-------------------
* Avoid transaction save when viewing a document [silviot]
* clean up pdb

1.16.3 (2013-01-11)
-------------------
* new Plomino util function: is_email
* new Plomino util function: urlquote
* fix field validation
* Plone 4.3 compliancy fixes

1.16.2 (2012-12-12)
-------------------
* various fixes for datagrids

1.16.1 (2012-10-16)
-------------------
* integrate jsonutils to manage decimal [jean]
* use iframe in overlay for datagrid popup [silviot]
* working on Plone4.3 support [alert]
* hide-when fixes [manuelep]
* static display for datagrids in read mode [ebrehault]

1.16 (2012-08-27)
-----------------
* server-side pagination and filtering for dynamic views
* new Plomino utils: decimal and escape_xml_illegal_chars
* offer selection lists instead of free text entries in various design parameters (source view, sorting column, ...)
* re-sync all .po
* Fix getItem to return a deepcopy

1.15.1 (2012-05-23)
-------------------
* Migration fix: initialize and refresh documents as BTreeFolder properly

1.15 (2012-05-18)
-----------------
* Performance profiling utility.
* Sort search results according search view sorting settings.

1.14.4 (2012-05-09)
-------------------
* Plone 3 compliancy: define __nonzero__ method on PlominoDocument (as it is not defined in Plone 3 by CMFBTreeFolder2)
* Czech translation (contributed by Jakub Svab)

1.14.3 (2012-05-03)
-------------------
* codemirror integration
* Depends on collective.js.datatables [toutpt]
* fix buildout for Plone 3
* fix popups for Plone 3

1.14.2 (2012-04-12)
-------------------
* Display validation errors in a nice popup.
* Fix importFromXML bugs.
* Fix File attachment indexing.

1.14.1 (2012-03-29)
-------------------
* Use CMFBTreeFolder instead of basic PortalFolder for PlominoDocuments so existing (<1.14) attached files keep accessible.

1.14 (2012-03-26)
-------------------
* PlominoDocument is not Archetypes-based anymore, it uses pure CMF now.
* 'Plomino' package is renamed 'Products.CMFPlomino'.
* Plone 4.2 compliancy.
* Fix design portlet on Plone 3.

1.13.3 (2012-03-06)
-------------------
* JSON API improvements

1.13.2 (2012-02-16)
-------------------
* Add JSON utils: json_dumps and json_loads
* Add CSS class containing the element id on the Plomino element portlet

1.13.1 (2012-01-11)
-------------------
* Fix agent security when running as owner
* New content-type addable in PlominoForm: PlominoCache, to indicate cache fragments
* Fix exportCSV and exportXLS for views
* Fix OpenDatabase when doc counting is active

1.13 (2011-11-30)
-----------------
* onOpenView event
* getCache and setCache which use plone.memoize to cache data
* getRequestCache and setRequestCache to cache data into the request
* Allow keyword args for agent __call__

1.12.1 (2011-10-07)
-------------------
* fix transform exceptions in attached file indexing
* fix editor permissions to allow file attachment deletion

1.12 (2011-10-03)
-----------------
* fix reader access control on getfile
* add cgi_escape to utils
* create plomino_workflow and fix permissions
* integrate plone.app.async support to enable asynchronous agent execution and asynchronous refreshdb
* allow to run agent as current user or as owner
* don't use File for everything in /resources/; use Script (Python) for script libraries

1.11 (2011-09-12)
-----------------
* use onSave returned value to redirect to url after save
* getAllDocuments() returns PlominoDocuments (and not brains anymore, unless getObject=False)
* various fixes

1.10.4 (2011-08-03)
-------------------
* (for Plone 4 only) use MailHost.send instead of secureSend
* fix document portal indexation behaviour
* fix permission issues with Document id formula
* fix Mandatory field checking with File attachments fields

1.10.3 (2011-07-19)
-------------------
* i18n fixes
* fix translation method
* display rendered values in datagrid in edit mode

1.10.2 (2011-07-12)
-------------------
* Only use Unicode in the Plomino index,
* Fix ConflictError issue: avoid writing annotations in fields objects constantly,
* Plone 4.1 compliancy fixes.

1.10.1 (2011-06-29)
-------------------
* Plone 3 compliancy (broken after Plone 4.1 compliancy)

1.10 (2011-06-26)
-----------------
* Plone 4.1 compliancy

1.9.8.1 (2011-05-27)
--------------------
* Fix applyHideWhen behaviour to avoid meaningless errors when applyHideWhen is not used for actual rendering.

1.9.8 (2011-05-26)
------------------
* Enable Plomino documents in sitemap
* Use Plomino_SearchableText field in search form to match SearchableText
* Display design tree into the design portlet
* Fix processImportAPI separator
* Support field validation at submit time in datagrid popup forms
* Fix behaviour with hidden fields passed as param in request
* Update french translation

1.9.7 (2011-05-05)
------------------
* Fix resources import/export
* Fix dynamic view for IE<9 compliancy
* Fix conflicts with Collage
* Update french translation

1.9.6 (2011-04-20)
------------------
* enable JQuery UI theme support in datatables
* load accordions content on click if url provided
* external utils pluggin mechanism
* refreshdb improvements

1.9.5 (2011-03-25)
------------------
* fix richtext field bug with Products.TinyMCE 1.1.8 (a commit was missing in 1.9.4)

1.9.4 (2011-03-24)
------------------
* isDocument method in PlominoUtils to test if context is a document
* fix categorized dynamic view (when column contains multivalues)
* fix richtext field bug with Products.TinyMCE 1.1.8

1.9.3 (2011-03-09)
------------------
* File handling fixes
* onSearch event (for Search forms)

1.9.2 (2011-02-21)
------------------
* Fix view generation
* Allow Plomino designers to manage Plomino element portlets

1.9.1 (2011-02-17)
------------------
* Fix import/export encoding problems
* Fix error traceback pop-up rendering

1.9
---
* Document id formula to compute document id at creation time.
* Display error traceback in a pop-up (showing error message and formula code).
* Import/export documents to/from a server local folder
* Validator to avoid using underscores in views and columns ids.
* Fix URLs in virtual hosting context.
* Plomino_Readers: Plomino_Readers allows to restrict the list of users, groups, and/or user roles allowed to view the document.
* Use collective.js.jqueryui instead of custom jqueryui. IMPORTANT NOTE: in Plone 3, please use collective.js.jqueryui = 1.7.3.1
* Fix replication (file attachments support with blob + push/pull behavior).
* Plomino element portlet can be conditionally displayed.
* Generate a view based on a form (use fields for columns, set selection formula, and create "Add new" button).
* Clean "browserims" (make sure Plomino API works when REQUEST is not defined to allow proper usage from a script).
* Plomino documents are not necessarily indexed into the portal catalog.

1.8
---
* Replace mode for design import (existing design is entirely replaced by the imported one).
* German translation.
* User-friendly error messages for failing formulas.
* TEXT and NAME fields indexed as FieldIndex (instead not ZCTextIndex) to allow sorting.
* New field mode "Computed on save": value is computed when document is saved and stored, it is not re-computed when the document is opened.
* Online debugger (integration with Clouseau): failing formula can be executed step-by-step from the web interface.

1.7.5
-----
* Documents stored in a BTreeFolder.
* If available, use plone.app.blob to store file attachments.
* When importing design or documents, use savepoints instead of actual commit.
* CSV import uses fields definition (so values are casted accordingly, instead of storing everything as strings).
* Excel export method on views.
* Categorized views supported with dynamic mode.
* Fix file attachment bug under Plone 4.
*

1.7.4
-----
* Dynamic picklist for selection field

1.7.3
-----
* fix datagrid (it was storing rendered values and not raw values)
* localization for datatables: en, es, fr, it, lt, nl
* dynamic hidewhen are now manage at hidewhen level (and not as a global setting in the form)
* few minor fixes

1.7.2
-----
* fix delete button in Plomino views when using the Dynamic view rendering
* fix XML import with indexed datagrid fields

1.7.1
-----
* fix jqueryui skin elements access

1.7
---
* Remove dependencies with: collective.js.jquery, collective.js.jqueryui, plone.app.jquerytools.
* Dynamic hide-when.
* Fields can be provided by external products as plugin utilities.
* Fields improvements: picklist for names and doclinks.
* Store all texts in unicode.
* Lithuanian translation.
* Improve import/replication/refresh performances and display a progress bar.

1.6.3
-----
* Plone 4 compliant
* JQueryUI accordion integration (ability to create collapsible sections in forms)
* New portlet to insert a Plomino form anywhere in your Plone site
* Installation using a buildout extend
* Force form for a document using ?openwithform=formid in the request
* German translation fixes

1.6.2
-----

* ability to restrict documents XML export to a given view
* sort elements by id in the Design tab
* XML export improvements: elements are sorted, xml is pretty
  (so diff and svn play nicely), CDATA escaping has been removed, and
  lxml is used if installed
* unlock webdav-locked elements before importing
* fix: column sorting and summing
* fix: openWithForm encoding errors
* fix: do not call onSave when importing document from replication
  or XML file

1.6.1
-----

* JQuery datatables to render Plomino views
* Datagrid field type
* Fulltext indexing in local Plomino index
* Documents import/export via XML files
* Ability to define column values using existing fields

1.5.7
-----

* Portlet with useful links for design management (add items, acl, etc...)
* Google visualization table to display views
* Fixes for Plone 4 compliancy (work in progress)

1.5.6
-----

* Access control fix : Owner is author of any document (just like PlominoManager role)
* MissingValue() method in PlominoUtils : it returns Missing.Value which can be useful
  when processing ZCatalog brains (=search results) as Missing.Value cannot be imported
  into formulas.
* Do not compute column values in index if the document does not belong to the view.
  Note: it does not really change the performances when indexing, but it does reduce
  the index size.
  It also reduce the amount of error traceback in debug mode.

1.5.5
-----

* Fix: escape CDATA in XML import/export (Jean Jordaan contribution)
* Fix: handle empty multiselect and empty checkboxes
* Fix: do not default to PlominoAuthor right if Authenticated generic right
  is PlominoAuthor whereas the current user as PlominoReader right
* Fix: set encoding in exportCSV

1.5.4
-----

* Fix: insufficient privileges error when changing Anonymous access right from PlominoAuthor to No Access
* Enable multiple Google Visualization fields in the same form
* hide selection box in views if no remove permission
* refresh() method on PlominoDocument: same as save() but do not trigger onSaveDocument
* more i18n French translations
* Validation formula improvments (ability to test the current doc id + bug fixes)
* beforeCreateDocument event

1.5.3
-----

* Security fix: when a group has PlominoAuthors rights, members of this group are just authors on their own documents

1.5.2
-----

* Migration script

1.5.1
-----

* TinyMCE support fix

1.5
---

* Google chart integration : pie chart, bar chart, etc.
  (see http://code.google.com/intl/en/apis/chart/types.html )
* Ability to display the sum of a column in view (when columns contain figures)
* Google Visualization integration : organizational charts, dynamic charts, map, etc.
  (see http://code.google.com/intl/en/apis/visualization/documentation/gallery.html )
* CSV support improvement
* Ability to restrict a Names field to a given member group
* Import/export and replication improvements

1.4
---

* Control Kupu height for Richtext fields
* Delete button confirmation message
* German translation
* Ability to hide Default Actions in forms
* Group support in user roles and in Plomino_Authors
* Import/export database settings and ACL settings
* XML import/export design to/from file
* Replication filtering using a view (feature financed by ACEA)
* TinyMCE support
* Delete documents from view
* Bug fixes

1.3-stable
----------

* Custom start page

* Form as page (no action bar)

* i18n fixes

* bug fixes

1.3RC4
------

* fr-fr fallback for i18n fr files

* Date/Time widget fix for Plone 3.2

* IMPORTANT NOTE: this version does not support Plone versions < 3.2

* Better error handling for field rendering

1.3RC3
------

* Clean up debug trace

1.3RC2
------

* Fix migration script

1.3RC1 - Unreleased
---------------------------

* Initial release

--------
Concepts
--------

Plomino database
================

A Plomino *application* is supported by a Plomino *database*.

The Plomino database is the Plone object which contains the application
data (i.e. the documents; see below), and its structure (i.e. the
design; see below).

Forms
=====

A *form* allows users to view and/or to edit information.

A form contains some fields of different types (text, date, rich text,
checkbox, attached files, etc.).

The application designer designs the layout he needs for the form, and
inserts the fields wherever he wants.

A form can also contain some action buttons to trigger specific
processing.

A form might also not be used to create or view documents but just to provide 
specific features (see Search form, and Page form).

Documents
=========

A *document* is a set of data. Data can be submitted by a user using a
given form.

Important note: a document can be created using one form and then viewed
or edited using a different form. This mechanism allows the document
rendering and the displayed action buttons to change according to
different parameters (user access rights, current document state, field
values, etc.).

Views
=====

A *view* allows a list of documents to be displayed.

A view has a selection formula which filters the documents the
application designer wants to be displayed in the view.

A view contains columns. Column contents is computed using data stored
in the documents.

Search forms
============

The application designer can create specific forms dedicated to performs
search requests (those forms will not be used to create documents but to
input the request criteria).

It allows the designer to provide more accurate and more
business-oriented search features than the global Plone search.

Page forms
==========

The application designer can create page forms to build custom navigation 
menus, generate reports, provide portlet content, etc.

Design
======

A Plomino application design is the set of forms and views provided in
the Plomino database.

The design defines the structure of the application, and it is created
by the application designer. It differs from the documents, which are
the application data, created by the users.


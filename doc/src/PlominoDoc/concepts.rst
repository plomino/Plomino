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

A form usually contains some fields of various types (text, date, rich
text, checkbox, attached files, etc.).

The application designer designs the layout he needs for the form, and
inserts the fields wherever he wants.

A form can also contain some action buttons to trigger specific processing.

Forms are not always used to create or view documents --- sometimes they are
used to provide specific features (see `Search forms`_, and `Page forms`_).

Documents
=========

A *document* is a set of data. Data can be submitted by a user using a
given form.

.. Note: a document can be created using one form and then viewed or edited
   using a different form. The presentation of the document is determined
   by the form, which renders the data items found on the document. The
   fields on the form need not correspond one to one with the data items
   stored on the document: there may be more fields, or fewer fields, or
   the type of field may be different. Care should be taken to maintain
   consistency: make sure that the form matches the document. 

This mechanism allows the document rendering and the displayed action
buttons to change according to different parameters (user access rights,
current document state, field values, etc.).

Views
=====

A *view* defines a collection of documents.

A view has a *selection formula* which filters the documents that the
application designer wants to be displayed in the view.

A view contains *columns*. Column contents is computed from data stored in
the documents.

Search forms
============

The application designer can create specific forms dedicated to perform
searches. These forms are not used to create documents, but to input the
search criteria.

It allows the designer to provide more specific and more business-oriented
search features than the global Plone search.

Page forms
==========

The application designer can create page forms to build custom navigation 
menus, generate reports, provide portlet content, etc.

Design
======

The *design* of a Plomino application consists of the set of forms and views
provided in the Plomino database.

The design defines the structure of the application, and it is created by
the application designer. It differs from the documents, which are the
application data, created by the users.


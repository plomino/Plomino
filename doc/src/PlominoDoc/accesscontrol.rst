--------------
Access control
--------------

Standard Plomino access rights
==============================

Plomino offers 5 standard access levels for any Plomino database:

- *Reader*: can read any document, perform searches, but cannot create
  new documents or modify existing ones.

- *Author*: Reader + can create new documents, and modify/delete only
  documents he/she has created.

- *Editor*: Author + can modify/delete any documents.

- *Designer*: Editor + can change the database design.

- *Manager*: Designer + can change the access rights.

These rights can be granted to Plone members and/or to Plone groups.

Generic users
=============

Plomino handles 2 types of generic users:

- *Anonymous*: users not authenticated on the Plone site.

- *Authenticated*: any authenticated user.

The Plomino standard access rights can be applied to those 2 generic
users, but an anonymous user will never be able to delete a document.

.. Note:: 
    as nothing can differentiate an anonymous user from another one,
    this rule allows to make sure no one will delete a document created
    by someone else.

Roles
=====

Some applications may need to provide, for specific users, a specific
behaviour which is beyond the basic access rights mechanism we have just
described.

Plomino allows you to create roles which can be applied to Plone users.

By default, a role does not grant any extra rights, but the application
designer will use them as markers to enable specific behaviours in his
application.

For instance, if you build a Plomino application to handle purchase
requests, all the employees will be able to use the form to submit a
purchase request, but only the users with the `[FinancialReponsible]`
role would be able to modify the **Approval** section in this form.

.. Note:: roles are always noted with brackets.

Manage the access rights
========================

Access rights are managed in the tab named **ACL** (Access Control List). 

.. image:: images/30eab40c.png 

Application-level access control
================================

In addition to the global access rights, it may also be necessary to
configure access to documents individually. As an example, here is one way to restrict
document access to the creator of the document:

- create a ``Name`` field named ``creator`` for instance,
  `Computed on creation`, with the following formula::

    plominoDocument.getCurrentUser().getMemberId()
  
  This will store the user id of the user who creates the
  document (it might be dangerous to use the `Plomino_Authors`
  item on the document, as its value may evolve during the
  document life cycle).
  
  Add this field to the index.

- add a formula for the `onOpenDocument` event to make sure the
  user is the creator (if this formula returns a false value,
  opening is allowed, but if it returns a true value, e.g. a
  string, opening fails, and the value is displayed as an error
  message).
  
  Here's an example formula::

    if plominoDocument.getCurrentUser().getMemberId()==plominoDocument.getItem('creator'):
        return None

    roles=plominoDocument.getCurrentUserRoles()
    if "[controller]" in roles:
        return None

    return "You are not allowed to view this document."

- create a search form which filters documents where the creator
  field matches the current user id.

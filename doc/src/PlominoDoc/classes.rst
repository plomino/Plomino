-----------------------
Plomino class reference
-----------------------

Non-exhaustive list of the classes' methods.

TO BE UPDATED

PlominoDatabase
===============

`callScriptMethod(self, scriptname, methodname, *args)`
    calls a method named methodname in a file named scriptname, stored in
    the ``resources`` folder. If the called method allows it, you may
    pass some arguments.

`createDocument(self)`
    returns a new empty document.

`deleteDocument(self, doc)`
    deletes the document

`deleteDocuments(self, ids=None, massive=True)`
    batch delete documents from database. If `massive` is ``True``, the
    `onDelete` formula and index updating are not performed (use
    `refreshDB` to update).
    
`getAgents(self)`
    returns all the PlominoAgent objects stored in the database.

`getAllDocuments(self)`
    returns catalog brains for all the PlominoDocument objects stored in
    the database.

`getCurrentUser(self)`
    returns the current user.

`getCurrentUserRights(self)` 
    returns the current user's access rights.

`getCurrentUserRoles(self)`
    returns the current user's roles.

`getDocument(self, docid)`
    returns the PlominoDocument object corresponding to the identifier.

`getForm(self, formname)`
    returns the PlominoForm object corresponding to the identifier.

`getForms(self)`
    returns all the PlominoForm objects stored in the database.

`getIndex(self)`
    returns the PlominoIndex object.

`getPortalGroups(self)`
    returns the Plone site groups.

`getPortalMembers(self)`
    returns the Plone site members.

`getPortalMembersIds(self)`
    returns the Plone site member ids.

`getPortalMembersGroupsIds(self)`
    returns the Plone site groups ids and all the Plone site members
    ids.

`getUserRoles(self)`
    returns all the roles declared in the database.

`getUsersForRight(self, right)`
    returns the users declared in the ACL and having the given right.

`getUsersForRoles(self,role)`
    returns the users declared in the ACL and having the given role.

`getView(self, viewname)`
    return the PlominoView object corresponding to the identifier.

`getViews(self)`
    returns all the PlominoView objects stored in the database.

`hasUserRole(self, userid, role)`
    returns `True` if the specified user id has the given role.

`isCurrentUserAuthor(self, doc)`
    returns `True` if the current user is author of the given document
    or has the PlominoAuthor right.

`refreshDB(self)`
    refresh the database index and the formulas.
    
`writeMessageOnPage(self, infoMsg, REQUEST, ifMsgEmpty = '', error = False)`
    displays a standard Plone status message.
    The REQUEST parameter is mandatory, most part of time plominoDocument.REQUEST will be the correct value.
    ifMsgEmpty is the default message to display if infoMsg is empty.
    If error is False, the message displays as an information message, if True, it displays as an Error message.

PlominoDocument
===============

`delete(self, REQUEST=None)`
    deletes the document, and if ``REQUEST`` contains a key named
    ``returnurl``, uses its value to redirect the client.

`deleteAttachment(self,` `REQUEST)`
    remove file object and update corresponding item value.

`getfile(self, filename=None, REQUEST=None)`
    return the file corresponding to the given filename.

`getFilenames(self)`
    return the filenames of all the files stored with the document.

`getForm(self)`
    returns the form given by the *view form* formula (if the document
    is opened from a view and if the view has a form formula), else
    returns the form given by the document's Form item.

`getItem(self, name, default='')`
    returns the item value if it exists, else returns the default value (an 
    empty string if not provided).
    
`getItemClassname(self, name)`
    returns the class name of the item .

`getItems(self)`
    returns the names of all the items existing in the document.

`getParentDatabase(self)`
    returns the PlominoDatabase object which contains the document.

`getRenderedItem(self, itemname, form=None, convertattachments=False)`
    returns the item value using the rendering corresponding to the
    field type defined in the form (if form is `None`, it uses the form
    returned by `getForm()`). If `convertattachments` is `True`,
    FileAttachments items are converted to text (if possible).

`hasItem(self,` `name)`
    returns `True` if the item exists in the document.

`isAuthor(self)`
    returns `True` if the current user is author of the document or has
    the PlominoAuthor right.

`isEditMode(self)`
    returns `True` is the document is being edited, `False` if it is
    being read. Note the same method is available in PlominoForm, so it
    can be used transparently in any formula to know if the document is
    being edited or not.

`isNewDocument(self)`
    returns `False` (because an existing document is necessarily not
    new). Note the same method is available in PlominoForm (and returns
    `True`), so it can be used transparently in any formula to know if
    the document is being created or not.

`openWithForm(self,` `form,` `editmode=False)`
    display the document using the given form's layout (but first, check
    if the user has proper access rights).

`removeItem(self,` `name)`
    remove the item.

`save(self, form=None, creation=False, refresh_index=True)`
    refresh the computed fields and re-index the document in the Plomino
    index and in the Plone `portal_catalog` (only if `refresh_index` is
    `True`; `False` might be useful to improve the performance, but a
    `refreshDatabase` will be needed). It uses the field's formulas
    defined in the provided form (by default, it uses the form returned
    by `getForm()`).

`send(self, recipients, title, form=None)`
    send the document by mail to the recipients. The document is
    rendered in HTML using the provided form (by default it uses the
    form returned by `getForm()`).

`setItem(self,name,value)`
    set the value (if the item does not exist, it is created).

PlominoForm
===========

`getFormName(self)`
    returns the form id.

`getParentDatabase(self)`
    returns the PlominoDatabase object which contains the form.

`isEditMode(self)`
    returns `True`. 
    
    .. Note:: 
        the same method is available in PlominoDocument, so it can be
        used transparently in any formula to know if the document is
        being edit or not.

`isNewDocument(self)`
    returns `True` (when the context is a form, it is necessarily a new
    doc). 
    
    .. Note:: 
        the same method is available in PlominoDocument (and returns
        `False`), so it can be used transparently in any formula to know
        if the document is being created or not.

PlominoView
===========

`exportCSV(self, REQUEST=None)`
    returns the columns values in CSV format. If REQUEST is not `None`,
    download is proposed to the user.

`getAllDocuments(self)`
    returns all the documents which match the Selection Formula.
    Documents are sorted according the sort column (if defined).

`getDocumentsByKey(self, key)`
    returns all documents for which the value of the column used as sort
    key matches the given key.

`getParentDatabase(self)`
    returns the PlominoDatabase object which contains the view.

`getViewName(self)`
    returns the view id.

PlominoIndex
============

`dbsearch(self, request, sortindex, reverse=0)`
    searches the documents corresponding to the request (see ZCatalog
    reference). The returned objects are ZCatalog brains pointing to the
    documents (see ZCatalog reference).

`getKeyUniqueValues(self,` `key)`
    returns the list of distinct values for an indexed field.

`getParentDatabase(self)`
    returns the PlominoDatabase object which contains the index.

`refresh(self)`
    refresh the index.

PlominoUtils
============

.. Note::
    PlominoUtils is imported for any formula execution, its methods are
    always available (importing the module is not needed).

`DateRange(d1, d2)`
    returns the dates of all the days between the 2 dates.

`DateToString(d, format='%d/%m/%Y')`
    converts a date to a string.

`htmlencode(s)`
    replaces unicode characters with their corresponding html entities

`Now()`
    returns current date and time.

`PlominoTranslate(message, context, domain='CMFPlomino')`
    translate the given message using the Plone i18n engine (using the
    given domain).

`sendMail(db, recipients, title, html_message)`
    send a mail to the recipients.

`StringToDate(str_d, format='%d/%m/%Y')`
    converts a string to a date.

`userFullname(db, userid)`
    returns the user full name.

`userInfo(db, userid)`
    returns the Member object corresponding to the user id (it may be
    used to get the user email address for instance).

PlominoAgent
============

`getParentDatabase(self)`
    returns the PlominoDatabase object which contains the agent.

`runAgent(self, REQUEST=None)`
    runs the agent. If REQUEST is provided, there is a redirection to
    the database home page, unless the REQUEST contains a REDIRECT key
    If so, the formula returned value is used as the redirection URL.

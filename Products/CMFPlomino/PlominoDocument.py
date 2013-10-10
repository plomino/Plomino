# -*- coding: utf-8 -*-
#
# File: PlominoDocument.py

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'

# From the standard library
from copy import deepcopy
from urllib import urlencode
# 3rd party Python 
from jsonutil import jsonutil as json

# Zope
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from DateTime import DateTime
from interfaces import *
from persistent.dict import PersistentDict
from zope.annotation import IAttributeAnnotatable
# 4.3 compatibility
try:
    from zope.container.contained import Contained
except ImportError:
    from zope.app.container.contained import Contained
from zope.component.factory import Factory
from zope.component import queryUtility
from zope.interface import implements
from ZPublisher.HTTPRequest import FileUpload
import transaction

try:
    from AccessControl.class_init import InitializeClass
except:
    from App.class_init import InitializeClass

# CMF/Plone
from OFS.ObjectManager import BadRequestException
from OFS.Image import File
from Products.Archetypes.config import RENAME_AFTER_CREATION_ATTEMPTS
from Products.CMFCore.CMFBTreeFolder import CMFBTreeFolder
from Products.CMFCore.exceptions import BadRequest
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString

try:
    from Products.CMFCore.CMFCatalogAware import CatalogAware
except ImportError, e:
    from Products.CMFCore.CMFCatalogAware import CMFCatalogAware as CatalogAware

try:
    from plone.app.blob.field import BlobWrapper
    from plone.app.blob.utils import guessMimetype
    HAS_BLOB = True
except ImportError, e:
    HAS_BLOB = False

# Plomino
from exceptions import PlominoScriptException
from PlominoUtils import sendMail, asUnicode, asList, PlominoTranslate
from Products.CMFPlomino.browser import PlominoMessageFactory as _
from Products.CMFPlomino.config import *
import interfaces

import logging
_logger = logging.getLogger('Plomino')

# Import conditionally, so we don't introduce a hard dependency
try:
    from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
    from plone.i18n.normalizer.interfaces import IURLNormalizer
    URL_NORMALIZER = True
except ImportError:
    URL_NORMALIZER = False


class PlominoDocument(CatalogAware, CMFBTreeFolder, Contained):
    """ These represent the contents in a Plomino database.

    A document contains *items*.
    An item may or may not correspond to fields on one or more forms.
    They may be manipulated by Formulas.
    """

    security = ClassSecurityInfo()
    implements(interfaces.IPlominoDocument, IAttributeAnnotatable)

    portal_type = "PlominoDocument"
    meta_type = "PlominoDocument"

    security.declarePublic('__init__')
    def __init__(self, id):
        """ Initialization
        """
        CMFBTreeFolder.__init__(self, id)
        self.id = id
        self.items = PersistentDict()
        self.plomino_modification_time = DateTime().toZone('UTC')

    security.declarePublic('checkBeforeOpenDocument')
    def checkBeforeOpenDocument(self):
        """ Check read permission and open view.

        .. NOTE:: if ``READ_PERMISSION`` is set on the ``view`` action
            itself, it causes an error ('maximum recursion depth exceeded')
            if user hasn't permission.
        """
        if self.isReader():
            return self.OpenDocument()
        else:
            raise Unauthorized, "You cannot read this content"

    def doc_path(self):
        return self.getPhysicalPath()

    def doc_url(self):
        """ Return valid and nice url:
        - hide plomino_documents
        - use physicalPathToURL if REQUEST available
        """
        path = self.doc_path()
        short_path = [p for p in path if p != "plomino_documents"]
        if hasattr(self, "REQUEST"):
            return self.REQUEST.physicalPathToURL(short_path)
        else:
            return "/".join(short_path)

    security.declarePublic('setItem')
    def setItem(self, name, value):
        """ Set item on document, converting str to unicode.
        """
        items = self.items
        if isinstance(value, str):
            db = self.getParentDatabase()
            translation_service = getToolByName(db, 'translation_service')
            value = translation_service.asunicodetype(value)
        items[name] = value
        self.items = items
        self.plomino_modification_time = DateTime().toZone('UTC')

    security.declarePublic('getItem')
    def getItem(self, name, default=''):
        """ Get item from document.
        """
        if self.items.has_key(name):
            return deepcopy(self.items[name])
        else:
            return default

    security.declarePublic('hasItem')
    def hasItem(self, name):
        """ Check if doc has item 'name'.
        """
        return self.items.has_key(name)

    security.declarePublic('removeItem')
    def removeItem(self,name):
        """ Delete item 'name', if it exists.
        """
        if self.items.has_key(name):
            items = self.items
            del items[name]
            self.items = items

    security.declarePublic('getItems')
    def getItems(self):
        """ Return all item names.
        """
        return self.items.keys()

    security.declarePublic('getItemClassname')
    def getItemClassname(self, name):
        """ Return class name of the item.
        """
        return self.getItem(name).__class__.__name__

    security.declarePublic('getLastModified')
    def getLastModified(self, asString=False):
        """ Return last modified date, setting it if absent.
        """
        if not hasattr(self, 'plomino_modification_time'):
            self.plomino_modification_time = self.bobobase_modification_time().toZone('UTC')
        if asString:
            return str(self.plomino_modification_time)
        else:
            return self.plomino_modification_time

    security.declarePublic('getRenderedItem')
    def getRenderedItem(self, itemname, form=None, formid=None,
            convertattachments=False):
        """ Return the item rendered according to the corresponding field.

        The form used can be, in order of precedence:
        - passed as the `form` parameter,
        - specified with the `formid` parameter and looked up,
        - looked up from the document.

        If no form or field is found, return the empty string.

        If `convertattachments` is True, then we assume that field
        attachments are text and append them to the rendered value.
        """
        db = self.getParentDatabase()
        result = ''
        if not form:
            if formid:
                form = db.getForm(formid)
            else:
                form = self.getForm()
        if form:
            field = form.getFormField(itemname)
            if field:
                result = field.getFieldRender(form, self, False)
                if (field.getFieldType() == 'ATTACHMENT' and
                        convertattachments):
                    result += ' ' + db.getIndex().convertFileToText(
                            self,
                            itemname).decode('utf-8')
                    result = result.encode('utf-8')

        return result

    security.declarePublic('tojson')
    def tojson(
        self,
        REQUEST=None,
        item=None,
        formid=None,
        rendered=False,
        lastmodified=None):
        """ Return item value as JSON.

        Return all items if `item=None`.
        Values on the REQUEST overrides parameters.

        If the requested item corresponds to a field on the found form, 
        the field value is returned. If not, it falls back to a plain item
        lookup on the document.

        `formid="None"` specifies plain item lookup.
        """
        # TODO: Don't always return the entire dataset: allow batching.

        if not self.isReader():
            raise Unauthorized, "You cannot read this content"

        datatables_format = False
        if REQUEST:
            REQUEST.RESPONSE.setHeader(
                    'content-type', 'application/json; charset=utf-8')
            item = REQUEST.get('item', item)
            formid = REQUEST.get('formid', formid)
            lastmodified = REQUEST.get('lastmodified', lastmodified)
            rendered_str = REQUEST.get('rendered', None)
            if rendered_str:
                rendered = True
            datatables_format_str = REQUEST.get('datatables', None)
            if datatables_format_str:
                datatables_format = True
        if item:
            if formid == "None":
                form = None
            elif formid:
                form = self.getParentDatabase().getForm(formid)
            else:
                form = self.getForm()
            if form:
                field = form.getFormField(item)
                if field:
                    if field.getFieldType() == 'DATAGRID':
                        adapt = field.getSettings()
                        fieldvalue = adapt.getFieldValue(
                                form, doc=self, request=REQUEST)
                        fieldvalue = adapt.rows(
                                fieldvalue, rendered=rendered)
                    else:
                        if rendered:
                            fieldvalue = self.getRenderedItem(item, form)
                        else:
                            adapt = field.getSettings()
                            fieldvalue = adapt.getFieldValue(
                                    form, doc=self, request=REQUEST)
                else:
                    _logger.info("Failed to find %s on %s, "
                            "fallback to getItem."%(item, form.id))
                    fieldvalue = self.getItem(item)
            else:
                fieldvalue = self.getItem(item)
            data = fieldvalue
        else:
            data = self.items.data

        if datatables_format:
            data = {'iTotalRecords': len(data),
                    'iTotalDisplayRecords': len(data),
                    'aaData': data }
        if lastmodified:
            data = {'lastmodified': self.getLastModified(), 'data': data}
        return json.dumps(data)

    security.declarePublic('computeItem')
    def computeItem(self, itemname, form=None, formid=None, store=True,
            report=True):
        """ Return the value of named item according to the formula 
        - of the field defined in the given form (default),
        - or the named `formid`,
        - or use the default doc form if no form found.
        Store the value in the doc (if `store=True`).
        (Pass `report` to `PlominoForm.computeFieldValue`.)
        """
        result = None
        if not form:
            if not formid:
                form = self.getForm()
            else:
                db = self.getParentDatabase()
                form = db.getForm(formid)
        if form:
            result = form.computeFieldValue(itemname, self, report=report)
            if store:
                # So this is a way to store the value of a DISPLAY field ..
                self.setItem(itemname, result)
        return result

    security.declarePublic('getPlominoReaders')
    def getPlominoReaders(self):
        """ Return list of readers; if none set, everyone can read.
        """
        if self.hasItem('Plomino_Readers'):
            return asList(self.Plomino_Readers)
        else:
            return ['*']

    security.declarePublic('isReader')
    def isReader(self):
        """
        """
        return self.getParentDatabase().isCurrentUserReader(self)

    security.declarePublic('isAuthor')
    def isAuthor(self):
        """
        """
        return self.getParentDatabase().isCurrentUserAuthor(self)

    security.declareProtected(REMOVE_PERMISSION, 'delete')
    def delete(self, REQUEST=None):
        """ Delete the current doc; redirect to `returnurl` if available.
        """
        db = self.getParentDatabase()
        db.deleteDocument(self)
        if REQUEST:
            return_url = REQUEST.get('returnurl')
            if not return_url:
                return_url = db.absolute_url()
            REQUEST.RESPONSE.redirect(return_url)

    security.declareProtected(EDIT_PERMISSION, 'validation_errors')
    def validation_errors(self, REQUEST):
        """ Check submitted values.
        """
        db = self.getParentDatabase()
        form = db.getForm(REQUEST.get('Form'))
        errors = form.validateInputs(REQUEST, doc=self)
        if errors:
            return self.errors_json(
                    errors=json.dumps({'success': False, 'errors': errors}))
        else:
            return self.errors_json(
                    errors=json.dumps({'success': True}))

    security.declareProtected(EDIT_PERMISSION, 'saveDocument')
    def saveDocument(self, REQUEST, creation=False):
        """ Save a document using the form submitted content
        """
        db = self.getParentDatabase()
        form = db.getForm(REQUEST.get('Form'))

        errors = form.validateInputs(REQUEST, doc=self)

        # execute the beforeSave code of the form
        error = None
        try:
            error = self.runFormulaScript(
                    'form_%s_beforesave' % form.id,
                    self,
                    form.getBeforeSaveDocument)
        except PlominoScriptException, e:
            e.reportError('Form submitted, but beforeSave formula failed')

        if error:
            errors.append(error)

        # if errors, stop here, and notify errors to user
        if errors:
            return form.notifyErrors(errors)

        self.setItem('Form', form.getFormName())

        # process editable fields (we read the submitted value in the request)
        form.readInputs(self, REQUEST, process_attachments=True)

        # refresh computed values, run onSave, reindex
        self.save(form, creation)

        redirect = REQUEST.get('plominoredirecturl')
        if not redirect:
            redirect = self.getItem("plominoredirecturl")
        if type(redirect) is dict:
            # if dict, we assume it contains "callback" as an URL that will be
            # called asynchronously, "redirect" as the redirect url (optional,
            # default=doc url), and "method" (optional, default=GET)
            redirect = "./async_callback?" + urlencode(redirect)
        if not redirect:
            redirect = self.absolute_url()
        REQUEST.RESPONSE.redirect(redirect)


    security.declareProtected(EDIT_PERMISSION, 'refresh')
    def refresh(self, form=None):
        """ Re-compute fields and re-index document.
        (`onSaveEvent` is not called, and authors are not updated)
        """
        self.save(
                form,
                creation=False,
                refresh_index=True,
                asAuthor=False,
                onSaveEvent=False)

    security.declareProtected(EDIT_PERMISSION, 'save')
    def save(self, form=None, creation=False, refresh_index=True,
            asAuthor=True, onSaveEvent=True):
        """ Refresh values according to form, and reindex the document.

        Computed fields are processed.
        """
        if not form:
            form = self.getForm()
        else:
            self.setItem('Form', form.getFormName())

        db = self.getParentDatabase()
        if form:
            for f in form.getFormFields(includesubforms=True, doc=self):
                mode = f.getFieldMode()
                fieldname = f.id
                # Computed for display fields are not stored
                if (mode in ["COMPUTED", "COMPUTEDONSAVE"] or 
                        (creation and mode=="CREATION")):
                    result = form.computeFieldValue(fieldname, self)
                    self.setItem(fieldname, result)

            # compute the document title
            title_formula = form.getDocumentTitle()
            if title_formula:
                # Use the formula if we have one
                try:
                    title = self.runFormulaScript(
                            'form_%s_title' % form.id,
                            self,
                            form.DocumentTitle)
                    if title != self.Title():
                        self.setTitle(title)
                except PlominoScriptException, e:
                    e.reportError('Title formula failed')
            elif creation:
                # If we have no formula and we're creating, use Form's title
                title = form.Title()
                if title != self.Title():
                    # We may be calling save with 'creation=True' on
                    # existing documents, in which case we may already have
                    # a title.
                    self.setTitle(title)

            # update the document id
            if creation and form.getDocumentId():
                new_id = self.generateNewId()
                if new_id:
                    transaction.savepoint(optimistic=True)
                    db.documents.manage_renameObject(self.id, new_id)

        # update the Plomino_Authors field with the current user name
        if asAuthor:
            # getItem('Plomino_Authors', []) might return '' or None
            authors = asList(self.getItem('Plomino_Authors') or [])
            name = db.getCurrentMember().getUserName()
            if not name in authors:
                authors.append(name)
            self.setItem('Plomino_Authors', authors)

        # execute the onSaveDocument code of the form
        if form and onSaveEvent:
            try:
                result = self.runFormulaScript(
                        'form_%s_onsave' % form.id,
                        self,
                        form.onSaveDocument)
                if result and hasattr(self, 'REQUEST'):
                    self.REQUEST.set('plominoredirecturl', result)
            except PlominoScriptException, e:
                if hasattr(self, 'REQUEST'):
                    e.reportError('Document saved, but onSave event failed.')
                    doc_path = self.REQUEST.physicalPathToURL(self.doc_path())
                    self.REQUEST.RESPONSE.redirect(doc_path)

        if refresh_index:
            # update index
            db.getIndex().indexDocument(self)
            # update portal_catalog
            if db.getIndexInPortal():
                db.portal_catalog.catalog_object(
                    self,
                    "/".join(db.getPhysicalPath() + (self.id,))
                )

    def _onOpenDocument(self, form=None):
        """ Execute the onOpenDocument code of the form.
        """
        if not form:
            form = self.getForm()

        onOpenDocument_error = ''
        try:
            if form.getOnOpenDocument():
                onOpenDocument_error = self.runFormulaScript(
                        'form_%s_onopen' % form.id,
                        self,
                        form.onOpenDocument)
                return onOpenDocument_error
        except PlominoScriptException, e:
            e.reportError('onOpenDocument event failed')


    security.declareProtected(READ_PERMISSION, 'openWithForm')
    def openWithForm(self, form, editmode=False):
        """ Display the document using the given form's layouts.
        First, check if the user has proper access rights.
        """
        db = self.getParentDatabase()
        if editmode:
            if not db.isCurrentUserAuthor(self):
                raise Unauthorized, "You cannot edit this document."
        else:
            if not self.isReader():
                raise Unauthorized, "You cannot read this content."

        onOpenDocument_error = self._onOpenDocument(form)

        if onOpenDocument_error:
            html_content = onOpenDocument_error
        else:
            # we use the specified form's layout
            request = getattr(self, 'REQUEST', None)
            if not request:
                import sys
                from ZPublisher.HTTPResponse import HTTPResponse
                from ZPublisher.HTTPRequest import HTTPRequest
                response = HTTPResponse(stdout=sys.stdout)
                env = {'SERVER_NAME': 'fake_server',
                       'SERVER_PORT': '80',
                       'REQUEST_METHOD': 'GET'}
                request = HTTPRequest(sys.stdin, env, response)
            html_content = form.displayDocument(self,
                                editmode=editmode,
                                request=request)

        plone_tools = getToolByName(db, 'plone_utils')
        encoding = plone_tools.getSiteEncoding()
        html_content = html_content.encode(encoding)
        return html_content

    security.declareProtected(EDIT_PERMISSION, 'editWithForm')
    def editWithForm(self, form):
        """ Shorthand for opening the form in edit mode.
        """
        return self.openWithForm(form, editmode=True)

    security.declarePublic('send')
    def send(self, recipients, title, form=None):
        """ Send current doc by mail.
        """
        db = self.getParentDatabase()
        if form is None:
            form = self.getForm()
        message = self.openWithForm(form)
        sendMail(db, recipients, title, message)

    security.declarePublic('Title')
    def Title(self):
        """ Return the stored title or compute the title (if dynamic).
        """
        form = self.getForm()
        if form.getDynamicDocumentTitle():
            # compute the document title
            title_formula = form.getDocumentTitle()
            if title_formula:
                # Use the formula if we have one
                try:
                    title = self.runFormulaScript(
                            'form_%s_title' % form.id,
                            self,
                            form.DocumentTitle)
                    if (form.getStoreDynamicDocumentTitle() and
                            title != super(PlominoDocument, self).Title()):
                        self.setTitle(title)
                    return title
                except PlominoScriptException, e:
                    e.reportError('Title formula failed')
        return super(PlominoDocument, self).Title()

    security.declarePublic('getForm')
    def getForm(self):
        """ Look for a form and return it if found. 
        
        - Look in `REQUEST`,
        - then try to compute from view, 
        - and finally fall back to document `Form` item.
        """
        formname = None
        if hasattr(self, 'REQUEST'):
            formname = self.REQUEST.get("openwithform", None)
        if not formname:
            if hasattr(self, 'evaluateViewForm'):
                formname = self.evaluateViewForm(self)
        if not formname:
            formname = self.getItem('Form')
        form = self.getParentDatabase().getForm(formname)
        if not form:
            if hasattr(self, "REQUEST") and formname:
                self.writeMessageOnPage(
                        "Form %s does not exist." % formname,
                        self.REQUEST,
                        True)
        return form

    def _getCatalogTool(self):
        return self.getParentDatabase().getIndex()

    security.declarePublic('__getattr__')
    def __getattr__(self, name):
        """ Overloads `getattr` to return item values as attributes.
        """
        if self.items.has_key(name):
            return self.items[name]
        else:
            if name in ['__parent__', '__conform__', '__annotations__',
                    '_v_at_subobjects', '__getnewargs__', 'aq_inner',
                    'im_self']:
                raise AttributeError, name
            else:
                try:
                    return CMFBTreeFolder.__getattr__(self, name)
                except Exception, e:
                    raise AttributeError, name

    security.declareProtected(READ_PERMISSION, 'isSelectedInView')
    def isSelectedInView(self, viewname):
        """ Return `True` if this document is included in `viewname`.
        """
        db = self.getParentDatabase()
        v = db.getView(viewname)
        if not v:
            _logger.info("Failed to find view %s" % viewname)
            return False
        try:
            #result = RunFormula(self, v.SelectionFormula())
            result = self.runFormulaScript(
                    'view_%s_selection' % v.id,
                    self,
                    v.SelectionFormula)
            return result
        except PlominoScriptException, e:
            e.reportError('%s view selection formula failed' % viewname)

    security.declareProtected(READ_PERMISSION, 'computeColumnValue')
    def computeColumnValue(self, viewname, columnname):
        """ Compute the value of `columnname` for this document in `viewname`.
        """
        # The view is not updated. TODO: is this true?
        db = self.getParentDatabase()
        v = db.getView(viewname)
        if not v:
            _logger.info("Failed to find view %s" % viewname)
            return None
        try:
            c = v.getColumn(columnname)
            #result = RunFormula(self, c.Formula())
            return self.runFormulaScript(
                    'column_%s_%s_formula' % (v.id, c.id),
                    self,
                    c.Formula)
        except PlominoScriptException, e:
            e.reportError('"%s" column formula failed in %s view' % (
                c.Title(), viewname))
            return None

    security.declareProtected(EDIT_PERMISSION, 'deleteAttachment')
    def deleteAttachment(self, REQUEST=None, fieldname=None, filename=None):
        """ Remove file object and update corresponding item value.
        """
        if REQUEST:
            fieldname = REQUEST.get('field')
            filename = REQUEST.get('filename')
        if fieldname and filename:
            current_files = self.getItem(fieldname)
            if current_files.has_key(filename):
                if len(current_files.keys()) == 1:
                    # if it is the only file attached, we need to make sure
                    # the field is not mandatory, to allow deletion
                    form = self.getForm()
                    if form:
                        field = form.getFormField(fieldname)
                        if field and field.getMandatory():
                            error = "%s %s" % (
                                    fieldname,
                                    PlominoTranslate(_("is mandatory"), self))
                            return form.notifyErrors([error])
                del current_files[filename]
                self.setItem(fieldname, current_files)
                self.deletefile(filename)
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url() + "/EditDocument")

    def UID(self):
        # needed for portal_catalog indexing
        return "%s-%s" % (self.getParentDatabase().UID(), self.id)

    security.declarePublic('SearchableText')
    def SearchableText(self):
        """ Return value for the Plone catalog's `SearchableText` index.
        """
        values = []
        index_attachments = self.getParentDatabase().getIndexAttachments()
        form = self.getForm()

        for itemname in self.items.keys():
            item_value = self.getItem(itemname)
            if isinstance(item_value, list):
                for v in item_value:
                    if isinstance(v, list):
                        values = values + [asUnicode(k) for k in v]
                    else:
                        values.append(asUnicode(v))
            else:
                values.append(asUnicode(item_value))
            # if selection or attachment field, we try to index rendered
            # values too
            try:
                if form:
                    field = form.getFormField(itemname)
                    if field and field.getFieldType() in ["SELECTION", "ATTACHMENT"]:
                        v = asUnicode(
                                self.getRenderedItem(
                                    itemname,
                                    form=form,
                                    convertattachments=index_attachments))
                        if v:
                            values.append(v)
            except:
                _logger.error('Exception during indexing', exc_info=True)
                pass
        return ' '.join(values)

    security.declareProtected(READ_PERMISSION, 'getfile')
    def getfile(self, filename=None, REQUEST=None, asFile=False):
        """ Return an attribute named `filename`, assumed to be a file object. 

        If `filename` is found on request, it overrides the parameter.
        """
        if not self.isReader():
            raise Unauthorized, "You cannot read this content"

        # Check access based on doc's current form. Plomino may be busy
        # rendering a different doc, using some requested form, which 
        # probably doesn't apply to this document.
        form = self.getParentDatabase().getForm(self.Form)
        onOpenDocument_error = self._onOpenDocument(form=form)
        if onOpenDocument_error:
            raise Unauthorized, onOpenDocument_error

        if REQUEST:
            filename = REQUEST.get('filename')
        if not filename:
            return None

        file_obj = self.get(filename, None)
        if not file_obj:
            return None
        if asFile:
            return file_obj
        if REQUEST:
            REQUEST.RESPONSE.setHeader(
                    'content-type', file_obj.getContentType())
            REQUEST.RESPONSE.setHeader(
                    "Content-Disposition", "inline; filename="+filename)
        return file_obj.data

    security.declareProtected(READ_PERMISSION, 'getFilenames')
    def getFilenames(self):
        """ Return names of items that are File or Blob.
        """
        if HAS_BLOB:
            return [id for id in self.objectIds()
                    if isinstance(self[id], BlobWrapper)]
        else:
            return [id for id in self.objectIds()
                    if isinstance(self[id], File)]

    security.declareProtected(EDIT_PERMISSION, 'setfile')
    def setfile(self, submittedValue, filename='', overwrite=False, contenttype=''):
        """ Store `submittedValue` (assumed to be a file) as a blob (or FSS).

        The name is normalized before storing. Return the normalized name and
        the guessed content type. (The `contenttype` parameter is ignored.)
        """
        # TODO: does the `contenttype` parameter exist for BBB? 
        # If so, mention it. If not, can it go?
        if filename == '':
            filename = submittedValue.filename
        if filename:
            if """\\""" in filename:
                filename = filename.split("\\")[-1]
            filename = '.'.join(
                    [normalizeString(s, encoding='utf-8') 
                        for s in filename.split('.')])
            if overwrite and filename in self.objectIds():
                self.deletefile(filename)
            try:
                self._checkId(filename)
            except BadRequest:
                # if filename is a reserved id, we rename it
                filename = '%s_%s' % (
                        DateTime().toZone('UTC').strftime("%Y%m%d%H%M%S"),
                        filename)
            
            if HAS_BLOB:
                if (isinstance(submittedValue, FileUpload) or 
                        type(submittedValue) == file):
                    submittedValue.seek(0)
                    contenttype = guessMimetype(submittedValue, filename)
                    submittedValue = submittedValue.read()
                elif submittedValue.__class__.__name__ == '_fileobject':
                    submittedValue = submittedValue.read()
                try:
                    blob = BlobWrapper(contenttype)
                except:  # XXX Except what?
                    # BEFORE PLONE 4.0.1
                    blob = BlobWrapper()
                file_obj = blob.getBlob().open('w')
                file_obj.write(submittedValue)
                file_obj.close()
                blob.setFilename(filename)
                blob.setContentType(contenttype)
                self._setObject(filename, blob)
            else:
                self.manage_addFile(filename, submittedValue)
                contenttype = self[filename].getContentType()
            return (filename, contenttype)
        else:
            return (None, "")

    security.declareProtected(EDIT_PERMISSION, 'deletefile')
    def deletefile(self, filename):
        """ Delete blob or FSS obj.
        """
        if filename in self.objectIds():
            self.manage_delObjects(filename)

    security.declarePublic('isNewDocument')
    def isNewDocument(self):
        """ Return true if the URL says `/createDocument`
        """
        req = getattr(self, 'REQUEST', None)
        if req and '/createDocument' in req['ACTUAL_URL']:
            return True
        return False

    security.declarePublic('isDocument')
    def isDocument(self):
        """ A PlominoDocument instance is a document.
        """
        return True

    security.declarePublic('isEditMode')
    def isEditMode(self):
        """ Return `True` if the URL says we're editing a document.
        """
        # if REQUEST exists, test the current command
        if hasattr(self, 'REQUEST'):
            command = self.REQUEST.URL.split('/')[-1].lower()
            return command in [
                'editdocument',
                'edit',
                'savedocument',
                'editbaredocument'
            ]
        else:
            return False

    security.declarePrivate('_findUniqueId')
    def _findUniqueId(self, id):
        """ Find a unique id in the parent folder, based on the given id, by
        appending -n, where n is a number between 1 and the constant
        RENAME_AFTER_CREATION_ATTEMPTS, set in config.py. If no id can be
        found, return None.

        Copied from Archetypes/BaseObject.py
        """
        check_id = getattr(self, 'check_id', None)
        if check_id is None:
            parent = aq_parent(aq_inner(self))
            parent_ids = parent.objectIds()
            check_id = lambda id, required: id in parent_ids

        invalid_id = check_id(id, required=1)
        if not invalid_id:
            return id

        idx = 1
        while idx <= RENAME_AFTER_CREATION_ATTEMPTS:
            new_id = "%s-%d" % (id, idx)
            if not check_id(new_id, required=1):
                return new_id
            idx += 1

        return None

    def generateNewId(self):
        """ Compute the id using the Document id formula.

        The value returned by the formula is normalized and completed with
        '-1', '-2', ..., if the id already exists.
        """

        # Don't do anything without the plone.i18n package
        if not URL_NORMALIZER:
            return None

        form = self.getForm()
        if not form:
            return None

        if not form.getDocumentId():
            return None

        result = None
        try:
            result = self.runFormulaScript(
                    'form_%s_docid' % form.id, self, form.DocumentId)
        except PlominoScriptException, e:
            e.reportError('Document id formula failed')

        if not result:
            return None

        if not isinstance(result, unicode):
            charset = self.getCharset()
            result = unicode(result, charset)

        request = getattr(self, 'REQUEST', None)
        if request:
            new_id = IUserPreferredURLNormalizer(request).normalize(result)
        else:
            new_id = queryUtility(IURLNormalizer).normalize(result)

        # check if the id already exists
        documents = self.getParentDatabase().documents
        try:
            documents._checkId(new_id)
        except BadRequestException:
            new_id = self._findUniqueId(new_id)
        return new_id

    def __nonzero__(self):
        # Needed for Plone 3 compliancy
        # (as BTreeFolder2 1.0 does not define __nonzero__)
        return True


InitializeClass(PlominoDocument)
addPlominoDocument = Factory(PlominoDocument)
addPlominoDocument.__name__ = "addPlominoDocument"

class TemporaryDocument(PlominoDocument):

    security = ClassSecurityInfo()

    def __init__(self, parent, form, REQUEST, real_doc=None, validation_mode=False):
        self._parent = parent
        self.REQUEST = REQUEST
        if real_doc:
            self.items = PersistentDict(real_doc.items)
            self.real_id = real_doc.id
        else:
            self.items = {}
            self.real_id = "TEMPDOC"
        self.setItem('Form', form.getFormName())
        form.readInputs(self, REQUEST, validation_mode=validation_mode)

    security.declarePublic('getParentDatabase')
    def getParentDatabase(self):
        """ Temporary docs are able to acquire from the db
        """
        return self._parent

    security.declarePublic('isEditMode')
    def isEditMode(self):
        """
        """
        return True

    security.declarePublic('isNewDocument')
    def isNewDocument(self):
        """
        """
        if self.real_id == "TEMPDOC":
            return True
        return False

    security.declarePublic('isDocument')
    def isDocument(self):
        """ Return `True` if we're representing an existing document.
        """
        if self.id == 'TEMPDOC':
            return False
        return True

    security.declarePublic('id')
    @property
    def id(self):
        """
        """
        return self.real_id

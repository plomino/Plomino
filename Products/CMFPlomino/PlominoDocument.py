# -*- coding: utf-8 -*-
#
# File: PlominoDocument.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString

from exceptions import PlominoScriptException
from Products.CMFPlomino.config import *

from interfaces import *
from Products.Archetypes.public import *
from AccessControl import Unauthorized
from time import strptime
from DateTime import DateTime
from zope import event
from Products.Archetypes.event import ObjectEditedEvent
from zope.component import queryUtility

import simplejson as json

import logging
logger = logging.getLogger('Plomino')

# Import conditionally, so we don't introduce a hard dependency
try:
    from plone.i18n.normalizer.interfaces import IUserPreferredURLNormalizer
    from plone.i18n.normalizer.interfaces import IURLNormalizer
    URL_NORMALIZER = True
except ImportError:
    URL_NORMALIZER = False
    
from PlominoUtils import DateToString, StringToDate, sendMail, asUnicode, asList, PlominoTranslate
from OFS.Image import File
from ZPublisher.HTTPRequest import FileUpload
try:
    from iw.fss.FileSystemStorage import FileSystemStorage, FSSFileInfo
except Exception, e:
    pass
try:
    from plone.app.blob.field import BlobWrapper
    from plone.app.blob.utils import guessMimetype
    HAS_BLOB = True
except Exception, e:
    HAS_BLOB = False

schema = Schema((

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoDocument_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoDocument(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoDocument)

    meta_type = 'PlominoDocument'
    _at_rename_after_creation = False

    schema = PlominoDocument_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('__init__')
    def __init__(self,oid,**kw):
        """initialization
        """
        ATFolder.__init__(self, oid, **kw)
        self.items={}
        self.plomino_modification_time = DateTime().toZone('UTC')

    security.declarePublic('checkBeforeOpenDocument')
    def checkBeforeOpenDocument(self):
        """check read permission and open view  NOTE: if READ_PERMISSION
        set on the 'view' action itself, it causes error 'maximum
        recursion depth exceeded' if user hasn't permission
        """
        if self.isReader():
            return self.OpenDocument()
        else:
            raise Unauthorized, "You cannot read this content"

    def doc_path(self):
        #db = self.getParentDatabase()
        #return db.getPhysicalPath() + (self.id,)
        # here we return actual path, we do not hide plomino_documents anymore
        return self.getPhysicalPath()

    def doc_url(self):
        """ return valid and nice url:
        - hide plomino_documents
        - use physicalPathToURL if REQUEST available
        """
        path = self.doc_path()
        short_path = [p for p in path if p!="plomino_documents"]
        if hasattr(self, "REQUEST"):
            return self.REQUEST.physicalPathToURL(short_path)
        else:
            return "/".join(short_path)
    
    security.declarePublic('setItem')
    def setItem(self,name,value):
        """
        """
        items = self.items
        if type(value) == type(''):
            db = self.getParentDatabase()
            translation_service = getToolByName(db, 'translation_service')
            value = translation_service.asunicodetype(value)
        items[name] = value
        self.items = items
        self.plomino_modification_time = DateTime().toZone('UTC')

    security.declarePublic('getItem')
    def getItem(self,name, default=''):
        """
        """
        if(self.items.has_key(name)):
            return self.items[name]
        else:
            return default

    security.declarePublic('hasItem')
    def hasItem(self,name):
        """
        """
        return self.items.has_key(name)

    security.declarePublic('removeItem')
    def removeItem(self,name):
        """
        """
        if(self.items.has_key(name)):
            items = self.items
            del items[name]
            self.items = items

    security.declarePublic('getItems')
    def getItems(self):
        """
        """
        return self.items.keys()

    security.declarePublic('getItemClassname')
    def getItemClassname(self,name):
        """
        """
        return self.getItem(name).__class__.__name__

    security.declarePublic('getLastModified')
    def getLastModified(self,asString=False):
        """
        """
        if not hasattr(self, 'plomino_modification_time'):
            self.plomino_modification_time = self.bobobase_modification_time().toZone('UTC')
        if asString:
            return str(self.plomino_modification_time)
        else:
            return self.plomino_modification_time

    security.declarePublic('getRenderedItem')
    def getRenderedItem(self, itemname, form=None, formid=None, convertattachments=False):
        """ return the item value rendered according the field defined in the given form
        (use default doc form if None)
        """
        result = ''
        db = self.getParentDatabase()
        if not form:
            if not formid:
                form = self.getForm()
            else:
                form = db.getForm(formid)
        if form:
            field = form.getFormField(itemname)
            if field:
                result = field.getFieldRender(form, self, False)
                if field.getFieldType()=='ATTACHMENT' and convertattachments:
                    result = result + ' ' + db.getIndex().convertFileToText(self,itemname)
                return result

        return result

    security.declarePublic('tojson')
    def tojson(self, REQUEST=None, item=None, formid=None):
        """return item value as JSON
        (return all items if item=None)
        """
        if not self.isReader():
            raise Unauthorized, "You cannot read this content"
        
        if REQUEST:
            item = REQUEST.get('item', item)
            formid = REQUEST.get('formid', formid)
        if not item:
            return json.dumps(self.items)
        
        if not formid:
            form = self.getForm()
        else:
            form = self.getParentDatabase().getForm(formid)
        if form:
            field = form.getFormField(item)
            if field:
                adapt = field.getSettings()
                fieldvalue = adapt.getFieldValue(form, self, False, False, REQUEST)
            else:
                fieldvalue = self.getItem(item)
        else:
            fieldvalue = self.getItem(item)
        return json.dumps(fieldvalue) 

    security.declarePublic('computeItem')
    def computeItem(self, itemname, form=None, formid=None, store=True, report=True):
        """ return the item value according the formula of the field defined in
        the given form (use default doc form if None)
        and store the value in the doc (if store=True)
        """
        result = None
        db = self.getParentDatabase()
        if not form:
            if not formid:
                form = self.getForm()
            else:
                form = db.getForm(formid)
        if form:
            result = form.computeFieldValue(itemname, self, report=report)
            if store:
                self.setItem(itemname, result)
        return result

    security.declarePublic('getPlominoReaders')
    def getPlominoReaders(self):
        """
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
        """delete the current doc
        """
        db = self.getParentDatabase()
        db.deleteDocument(self)
        if not REQUEST is None:
            return_url = REQUEST.get('returnurl')
            REQUEST.RESPONSE.redirect(return_url)

    security.declareProtected(EDIT_PERMISSION, 'saveDocument')
    def saveDocument(self, REQUEST, creation=False):
        """save a document using the form submitted content
        """
        db = self.getParentDatabase()
        form = db.getForm(REQUEST.get('Form'))

        errors=form.validateInputs(REQUEST, doc=self)
        if len(errors)>0:
            return form.notifyErrors(errors)

        self.setItem('Form', form.getFormName())

        # process editable fields (we read the submitted value in the request)
        form.readInputs(self, REQUEST, process_attachments=True)

        # refresh computed values, run onSave, reindex
        self.save(form, creation)

        redirect = REQUEST.get('plominoredirecturl')
        if not redirect:
            redirect = self.getItem("plominoredirecturl")
        if not redirect:
            redirect = self.absolute_url()
        REQUEST.RESPONSE.redirect(redirect)


    security.declareProtected(EDIT_PERMISSION, 'refresh')
    def refresh(self, form=None):
        """ re-compute fields and re-index document
        (onSave event is not called, and authors are not updated 
        """
        self.save(form, creation=False, refresh_index=True, asAuthor=False, onSaveEvent=False)

    security.declareProtected(EDIT_PERMISSION, 'save')
    def save(self, form=None, creation=False, refresh_index=True, asAuthor=True, onSaveEvent=True):
        """refresh values according form, and reindex the document
        """
        # we process computed fields (refresh the value)
        # TODO: manage computed fields dependencies
        if form is None:
            form = self.getForm()
        else:
            self.setItem('Form', form.getFormName())

        db=self.getParentDatabase()
        if form:
            for f in form.getFormFields(includesubforms=True, doc=self, applyhidewhen=False):
                mode = f.getFieldMode()
                fieldname = f.id
                if mode in ["COMPUTED", "COMPUTEDONSAVE"] or (mode=="CREATION" and creation):
                    result = form.computeFieldValue(fieldname, self)
                    self.setItem(fieldname, result)
                else:
                    # computed for display field are not stored
                    pass

            # compute the document title
            try:
                result = self.runFormulaScript("form_"+form.id+"_title", self, form.DocumentTitle)
            except PlominoScriptException, e:
                e.reportError('Title formula failed')
                result = ""
            if not result:
                result = form.Title()
            self.setTitle(result)

            # update the document id
            if creation and form.getDocumentId():
                self._renameAfterCreation()
                # _renameAfterCreation index doc in portal_catalog
                # 1: we do not necessarily want it (depending on IndexInPortal value)
                # 2: we will index it with the correct path anyway
                # so let's remove it for now
                db.portal_catalog.uncatalog_object("/".join(self.getPhysicalPath()))
            
        # update the Plomino_Authors field with the current user name
        if asAuthor:
            authors = self.getItem('Plomino_Authors')
            name = db.getCurrentUser().getUserName()
            if authors == '':
                authors = []
                authors.append(name)
            elif name in authors:
                pass
            else:
                authors.append(name)
            self.setItem('Plomino_Authors', authors)

        # execute the onSaveDocument code of the form
        if form and onSaveEvent:
            try:
                result = self.runFormulaScript("form_"+form.id+"_onsave", self, form.onSaveDocument)
                if result and hasattr(self, 'REQUEST'):
                    self.REQUEST.set('plominoredirecturl', result)
            except PlominoScriptException, e:
                if hasattr(self, 'REQUEST'):
                    e.reportError('Document has been saved but onSave event failed.')
                    doc_path = self.REQUEST.physicalPathToURL(self.doc_path())
                    self.REQUEST.RESPONSE.redirect(doc_path)

        if refresh_index:
            # update index
            db.getIndex().indexDocument(self)
            # update portal_catalog
            if db.getIndexInPortal():
                db.portal_catalog.catalog_object(self, "/".join(db.getPhysicalPath() + (self.id,)))
            event.notify(ObjectEditedEvent(self))

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
                raise Unauthorized, "You cannot read this content"

        # execute the onOpenDocument code of the form
        valid = ''
        try:
            if form.getOnOpenDocument():
                #RunFormula(self, form.getOnOpenDocument())
                valid = self.runFormulaScript("form_"+form.id+"_onopen", self, form.onOpenDocument)
        except PlominoScriptException, e:
            e.reportError('onOpen event failed')

        if not valid:
            # we use the specified form's layout
            request = getattr(self, 'REQUEST', None)
            if not request:
                import sys
                from ZPublisher.HTTPResponse import HTTPResponse
                from ZPublisher.HTTPRequest import HTTPRequest
                response = HTTPResponse(stdout=sys.stdout)
                env = {'SERVER_NAME':'fake_server',
                       'SERVER_PORT':'80',
                       'REQUEST_METHOD':'GET'}
                request = HTTPRequest(sys.stdin, env, response)
            html_content = form.displayDocument(self,
                                editmode=editmode,
                                request=request)
        else:
            html_content = valid

        plone_tools = getToolByName(db, 'plone_utils')
        encoding = plone_tools.getSiteEncoding()
        html_content = html_content.encode(encoding) 

        return html_content


    security.declareProtected(EDIT_PERMISSION, 'editWithForm')
    def editWithForm(self,form):
        """
        """
        return self.openWithForm(form, True)

    security.declarePublic('send')
    def send(self,recipients,title,form=None):
        """Send current doc by mail
        """
        db = self.getParentDatabase()
        if form is None:
            form = self.getForm()
        message = self.openWithForm(form)
        sendMail(db, recipients, title, message)

    security.declarePublic('getForm')
    def getForm(self):
        """ Return form: look in REQUEST, then try to acquire from view, and
        finally fall back to document Form item.
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
                self.writeMessageOnPage("Form %s does not exist." % formname, self.REQUEST, True)
        return form

    security.declarePrivate('manage_afterClone')
    def manage_afterClone(self,item):
        """after cloning
        """
        # changed from BaseFolder to ATFolder because now inherits fron ATFolder
        ATFolder.manage_afterClone(self, item)

    security.declarePublic('__getattr__')
    def __getattr__(self, name):
        """Overloads getattr to return item values as attibutes
        """
        if(self.items.has_key(name)):
            return self.items[name]
        else:
            if name not in ['__parent__', '__conform__', '__annotations__',
                           '_v_at_subobjects', '__getnewargs__', 'aq_inner', 'im_self']:
                try:
                    return ATFolder.__getattr__(self, name)
                except Exception, e:
                    raise AttributeError, name
            else:   
                raise AttributeError, name

    security.declareProtected(READ_PERMISSION, 'isSelectedInView')
    def isSelectedInView(self,viewname):
        """
        """
        db = self.getParentDatabase()
        v = db.getView(viewname)
        result = False
        if v:
            try:
                #result = RunFormula(self, v.SelectionFormula())
                result = self.runFormulaScript("view_"+v.id+"_selection", self, v.SelectionFormula)
            except PlominoScriptException, e:
                e.reportError('%s view selection formula failed' % viewname)
        return result

    security.declareProtected(READ_PERMISSION, 'computeColumnValue')
    def computeColumnValue(self,viewname,columnname):
        """
        """
        db = self.getParentDatabase()
        v = db.getView(viewname)
        try:
            c = v.getColumn(columnname)
            #result = RunFormula(self, c.Formula())
            result = self.runFormulaScript("column_"+v.id+"_"+c.id+"_formula", self, c.Formula)
        except PlominoScriptException, e:
            e.reportError('"%s" column formula failed in %s view' % (c.Title(), viewname))
            result = None
        return result

    security.declareProtected(EDIT_PERMISSION, 'deleteAttachment')
    def deleteAttachment(self, REQUEST=None, fieldname=None, filename=None):
        """remove file object and update corresponding item value
        """
        if REQUEST is not None:
            fieldname=REQUEST.get('field')
            filename=REQUEST.get('filename')
        if fieldname is not None and filename is not None:
            current_files=self.getItem(fieldname)
            if current_files.has_key(filename):
                if len(current_files.keys()) == 1:
                    # if it is the only file attached, we need to make sure the field
                    # is not mandatory to allow deletion
                    form = self.getForm()
                    if form:
                        field = form.getFormField(fieldname)
                        if field and field.getMandatory():
                            error = fieldname + " " + PlominoTranslate("is mandatory", self)
                            return form.notifyErrors([error])
                del current_files[filename]
                self.setItem(fieldname, current_files)
                self.deletefile(filename)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+"/EditDocument")

    security.declarePublic('SearchableText')
    def SearchableText(self):
        values = []
        index_attachments=self.getParentDatabase().getIndexAttachments()
        form = self.getForm()

        for itemname in self.items.keys():
            item_value = self.getItem(itemname)
            if type(item_value) is list: 
                for v in item_value:
                    if type(v) is list:
                        values = values + [asUnicode(k) for k in v]
                    else:
                        values.append(asUnicode(v))
            else:
                values.append(asUnicode(item_value))
            # if selection or attachment field, we try to index rendered values too
            try:
                if form:
                    field = form.getFormField(itemname)
                    if field and field.getFieldType() in ["SELECTION", "ATTACHMENT"]:
                        v = asUnicode(self.getRenderedItem(itemname,form=form, convertattachments=index_attachments))
                        if v:
                            values.append(v)
            except:
                pass
        return ' '.join(values)

    security.declareProtected(READ_PERMISSION, 'getfile')
    def getfile(self, filename=None, REQUEST=None):
        """
        """
        if not self.isReader():
            raise Unauthorized, "You cannot read this content"

        fss = self.getParentDatabase().getStorageAttachments()
        if REQUEST is not None:
            filename = REQUEST.get('filename')
        if filename is not None:
            if fss:
                storage = FileSystemStorage()
                file_obj = storage.get(filename, self)
            else:
                #file_obj = getattr(self, filename)
                file_obj = self.get(filename, None)
            if not file_obj:
                return None
            if REQUEST is None:
                return file_obj
            else:
                REQUEST.RESPONSE.setHeader('content-type', file_obj.getContentType())
                REQUEST.RESPONSE.setHeader("Content-Disposition", "inline; filename="+filename)
                if fss:
                    return file_obj.getData()
                else:
                    return file_obj.data
        else:
            return None

    security.declareProtected(READ_PERMISSION, 'getFilenames')
    def getFilenames(self):
        """
        """
        fss = self.getParentDatabase().getStorageAttachments()
        if fss:
            return [o.getTitle() for o in self.__dict__.values() if isinstance(o, FSSFileInfo)]
        else:
            #return [o.getId() for o in self.getChildNodes() if isinstance(o, File)]
            if HAS_BLOB:
                return [id for id in self.objectIds() if isinstance(self[id], BlobWrapper)]
            else:
                return [id for id in self.objectIds() if isinstance(self[id], File)]

    security.declareProtected(EDIT_PERMISSION, 'setfile')
    def setfile(self, submittedValue, filename='', overwrite=False, contenttype=''):
        """
        """
        if filename=='':
            filename=submittedValue.filename
        if filename!='':
            if """\\""" in filename:
                filename=filename.split("\\")[-1]
            filename = ".".join([normalizeString(s, encoding='utf-8') for s in filename.split('.')])
            if filename in self.objectIds():
                if overwrite:
                    self.deletefile(filename)
                else:
                    return ("ERROR: "+filename+" already exists", "")
            if(self.getParentDatabase().getStorageAttachments()==True):
                tmpfile=File(filename, filename, submittedValue)
                storage = FileSystemStorage();
                storage.set(filename, self, tmpfile);
                contenttype=storage.get(filename,self).getContentType()
            elif HAS_BLOB:
                if isinstance(submittedValue, FileUpload) or type(submittedValue) == file:
                    submittedValue.seek(0)
                    contenttype = guessMimetype(submittedValue, filename)
                    submittedValue = submittedValue.read()
                try:
                    blob = BlobWrapper(contenttype)
                except:
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
                contenttype=self[filename].getContentType()
            return (filename, contenttype)
        else:
            return (None, "")

    security.declareProtected(EDIT_PERMISSION, 'deletefile')
    def deletefile(self, filename):
        """
        """
        if(self.getParentDatabase().getStorageAttachments()):
            storage = FileSystemStorage();
            storage.unset(filename, self);
        else:
            if filename in self.objectIds():
                self.manage_delObjects(filename)

    security.declarePublic('isNewDocument')
    def isNewDocument(self):
        """
        """
        req = getattr(self, 'REQUEST', None)
        if req and '/createDocument' in req['ACTUAL_URL']:
            return True
        return False

    security.declarePublic('isDocument')
    def isDocument(self):
        """
        """
        return True

    security.declarePublic('isEditMode')
    def isEditMode(self):
        """
        """
        # if REQUEST exists, test the current command
        if hasattr(self, 'REQUEST'):
            command=self.REQUEST.URL.split('/')[-1].lower()
            return command in ['editdocument', 'edit']
        else:
            return False

    def generateNewId(self):
        """ compute the id using the Document id formula
        (overwrite Archetypes generateNewId, and provides same behaviour, 
        but use Document id formula instead of title)
        """
        form = self.getForm()
        if not form:
            return None

        if not form.getDocumentId():
            return None

        result = None
        try:
            result = self.runFormulaScript("form_"+form.id+"_docid", self, form.DocumentId)
        except PlominoScriptException, e:
            e.reportError('Document id formula failed')

        if not result:
            return None

        # Don't do anything without the plone.i18n package
        if not URL_NORMALIZER:
            return None

        if not isinstance(result, unicode):
            charset = self.getCharset()
            result = unicode(result, charset)

        request = getattr(self, 'REQUEST', None)
        if request is not None:
            return IUserPreferredURLNormalizer(request).normalize(result)

        return queryUtility(IURLNormalizer).normalize(result)
    
registerType(PlominoDocument, PROJECTNAME)
# end of class PlominoDocument

##code-section module-footer #fill in your manual code here
class TemporaryDocument(PlominoDocument):

    security = ClassSecurityInfo()

    def __init__(self, parent, form, REQUEST, real_doc=None):
        self._parent=parent
        if real_doc is not None:
            self.items=real_doc.items.copy()
            self.real_id=real_doc.id
        else:
            self.items={}
            self.real_id="TEMPDOC"
        self.setItem('Form', form.getFormName())
        form.readInputs(self, REQUEST)
        self._REQUEST=REQUEST

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
        if self.real_id=="TEMPDOC":
            return True
        else:
            return False

    security.declarePublic('REQUEST')
    @property
    def REQUEST(self):
        """
        """
        return self._REQUEST
    
    security.declarePublic('id')
    @property
    def id(self):
        """
        """
        return self.real_id

##/code-section module-footer




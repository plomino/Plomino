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

from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from interfaces import *
from Products.Archetypes.public import *
from AccessControl import Unauthorized
from time import strptime
from DateTime import DateTime
from zope import event
from Products.Archetypes.event import ObjectEditedEvent

from PlominoUtils import DateToString, StringToDate, sendMail
from OFS.Image import File
try:
    from iw.fss.FileSystemStorage import FileSystemStorage, FSSFileInfo
except Exception, e:
    pass

##/code-section module-header

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
    _at_rename_after_creation = True

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
        if self.checkUserPermission(READ_PERMISSION):
            if hasattr(self, 'REQUEST') and not self.checkUserPermission(DESIGN_PERMISSION):
                self.REQUEST["disable_border"]=True
            return self.OpenDocument()
        else:
            raise Unauthorized, "You cannot read this content"

    security.declarePublic('setItem')
    def setItem(self,name,value):
        """
        """
        items = self.items
        items[name] = value
        self.items = items
        self.plomino_modification_time = DateTime().toZone('UTC')

    security.declarePublic('getItem')
    def getItem(self,name):
        """
        """
        if(self.items.has_key(name)):
            return self.items[name]
        else:
            return ''

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
    def getRenderedItem(self, itemname, form=None, convertattachments=False):
        """ return the item value rendered according the field defined in the given form
        (use default doc form if None)
        """
        db=self.getParentDatabase()
        if form is None:
            form = db.getForm(self.Form)
        field=form.getFormField(itemname)
        if not field is None:
            content = field.getFieldRender(form, self, False)
            if field.getFieldType()=='ATTACHMENT' and convertattachments:
                content = content+' '+db.getIndex().convertFileToText(self,itemname)
            return content
        else:
            return ''

    security.declarePublic('getParentDatabase')
    def getParentDatabase(self):
        """
        """
        return self.getParentNode()

    security.declarePublic('isAuthor')
    def isAuthor(self):
        """
        """
        return self.getParentDatabase().isCurrentUserAuthor(self)

    security.declareProtected(REMOVE_PERMISSION, 'delete')
    def delete(self,REQUEST=None):
        """delete the current doc
        """
        db = self.getParentDatabase()
        db.deleteDocument(self)
        if not REQUEST is None:
            return_url = REQUEST.get('returnurl')
            REQUEST.RESPONSE.redirect(return_url)

    security.declareProtected(EDIT_PERMISSION, 'saveDocument')
    def saveDocument(self,REQUEST, creation=False):
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

        redirect = self.getItem("plominoredirecturl")
        if redirect=='':
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

        db=self.getParentDatabase()
        for f in form.getFields(includesubforms=True):
            mode = f.getFieldMode()
            fieldName = f.id
            if mode=="COMPUTED" or (mode=="CREATION" and creation):
                result = self.runFormulaScript("field_"+f.getParentNode().id+"_"+f.id+"_formula", self, f.Formula)
                self.setItem(fieldName, result)
            else:
                # computed for display field are not stored
                pass

        # compute the document title
        try:
            result = self.runFormulaScript("form_"+form.id+"_title", self, form.getDocumentTitle)
        except Exception:
            result = "Document"
        self.setTitle(result)

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
        if onSaveEvent:
            self.runFormulaScript("form_"+form.id+"_onsave", self, form.onSaveDocument)

        if refresh_index:
            # update index
            db.getIndex().indexDocument(self)
            # update portal_catalog
            self.reindexObject()
            event.notify(ObjectEditedEvent(self))

    security.declareProtected(READ_PERMISSION, 'openWithForm')
    def openWithForm(self,form,editmode=False):
        """display the document using the given form's layout - first,
        check if the user has proper access rights
        """
        if editmode:
            db = self.getParentDatabase()
            if not db.isCurrentUserAuthor(self):
                raise Unauthorized, "You cannot edit this document."

        # execute the onOpenDocument code of the form
        valid = ''
        try:
            if not form.getOnOpenDocument()=="":
                #RunFormula(self, form.getOnOpenDocument())
                valid = self.runFormulaScript("form_"+form.id+"_onopen", self, form.onOpenDocument)
        except Exception:
            pass

        if valid is None or valid=='':
            # we use the specified form's layout
            html_content = form.displayDocument(self, editmode)
            
        else:
            html_content = valid
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
        """try to acquire the formname using the parent view form formula,
        if nothing, use the Form item
        """
        if hasattr(self, 'evaluateViewForm'):
            formname = self.evaluateViewForm(self)
            if formname == "" or formname is None:
                formname = self.getItem('Form')
        else:
            formname = self.getItem('Form')
        return self.getParentDatabase().getForm(formname)

    security.declarePrivate('manage_afterClone')
    def manage_afterClone(self,item):
        """after cloning
        """
        # changed from BaseFolder to ATFolder because now inherits fron ATFolder
        ATFolder.manage_afterClone(self, item)

    security.declarePublic('__getattr__')
    def __getattr__(self,name):
        """Overloads getattr to return item values as attibutes
        """
        if(self.items.has_key(name)):
            return self.items[name]
        else:
            raise AttributeError, name
            #return BaseObject.__getattr__(self, name)

    security.declareProtected(READ_PERMISSION, 'isSelectedInView')
    def isSelectedInView(self,viewname):
        """
        """
        db = self.getParentDatabase()
        v = db.getView(viewname)
        try:
            #result = RunFormula(self, v.SelectionFormula())
            result = self.runFormulaScript("view_"+v.id+"_selection", self, v.SelectionFormula)
        except Exception:
            result = False
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
        except Exception:
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
            self.deletefile(filename)
            current_files=self.getItem(fieldname)
            if current_files.has_key(filename):
                del current_files[filename]
                self.setItem(fieldname, current_files)
        if REQUEST is not None:
            REQUEST.RESPONSE.redirect(self.absolute_url()+"/EditDocument")

    security.declarePublic('SearchableText')
    def SearchableText(self):
        values=[]
        index_attachments=self.getParentDatabase().getIndexAttachments()
        for itemname in self.items.keys():
            try:
                v = str(self.getRenderedItem(itemname,form=None, convertattachments=index_attachments))
                if v=='':
                    v = str(self.getItem(itemname))
                values.append(v)
            except:
                pass
        return ' '.join(values)

    security.declareProtected(READ_PERMISSION, 'getfile')
    def getfile(self, filename=None, REQUEST=None):
        """
        """
        fss = self.getParentDatabase().getStorageAttachments()
        if REQUEST is not None:
            filename = REQUEST.get('filename')
        if filename is not None:
            if fss:
                storage = FileSystemStorage()
                file_obj = storage.get(filename, self)
            else:
                file_obj = getattr(self, filename)
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
            return [o.getId() for o in self.getChildNodes() if isinstance(o, File)]

    security.declareProtected(EDIT_PERMISSION, 'setfile')
    def setfile(self, submittedValue, filename='', overwrite=False):
        """
        """
        if filename=='':
            filename=submittedValue.filename
        contenttype=''
        if filename!='':
            tmpfile=File(filename, filename, submittedValue)
            if """\\""" in filename:
                filename=filename.split("\\")[-1]
            if filename in self.objectIds():
                if overwrite:
                    self.deletefile(filename)
                else:
                    return ("ERROR: "+filename+" already exists", "")
            else:
                if(self.getParentDatabase().getStorageAttachments()==True):
                    storage = FileSystemStorage();
                    storage.set(filename, self, tmpfile);
                    contenttype=storage.get(filename,self).getContentType()
                else:
                    self.manage_addFile(filename, submittedValue)
                    contenttype=getattr(self,filename).getContentType()
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
        # when the context is an actual document, it is necessarily not new
        return False

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
        self.REQUEST=REQUEST

    security.declarePublic('getParentDatabase')
    def getParentDatabase(self):
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
     
    security.declarePublic('id')
    @property
    def id(self):
        """
        """
        return self.real_id
    
##/code-section module-footer




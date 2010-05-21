# -*- coding: utf-8 -*-
#
# File: PlominoForm.py
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
from DateTime import DateTime
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.CMFPlomino.config import *
from Products.CMFPlomino.PlominoUtils import PlominoTranslate, DateToString

##code-section module-header #fill in your manual code here
import sys
import re
import simplejson as json

from Products.CMFCore.utils import getToolByName

import PlominoDocument
from PlominoDocument import TemporaryDocument

##/code-section module-header

schema = Schema((

    StringField(
        name='id',
        widget=StringField._properties['widget'](
            label="Id",
            description="The form id",
            label_msgid='CMFPlomino_label_FormId',
            description_msgid='CMFPlomino_help_FormId',
            i18n_domain='CMFPlomino',
        ),
    ),
    TextField(
        name='onCreateDocument',
        widget=TextAreaWidget(
            label="On create document",
            description="Action to take when the document is created",
            label_msgid='CMFPlomino_label_onCreateDocument',
            description_msgid='CMFPlomino_help_onCreateDocument',
            i18n_domain='CMFPlomino',
        ),
        schemata="Events",
    ),
    TextField(
        name='onOpenDocument',
        widget=TextAreaWidget(
            label="On open document",
            description="Action to take when the document is opned",
            label_msgid='CMFPlomino_label_onOpenDocument',
            description_msgid='CMFPlomino_help_onOpenDocument',
            i18n_domain='CMFPlomino',
        ),
        schemata="Events",
    ),
    TextField(
        name='onSaveDocument',
        widget=TextAreaWidget(
            label="On save document",
            description="Action to take when saving the document",
            label_msgid='CMFPlomino_label_onSaveDocument',
            description_msgid='CMFPlomino_help_onSaveDocument',
            i18n_domain='CMFPlomino',
        ),
        schemata="Events",
    ),
    TextField(
        name='onDeleteDocument',
        widget=TextAreaWidget(
            label="On delete document",
            description="Action to take before deleting the document",
            label_msgid='CMFPlomino_label_onDeleteDocument',
            description_msgid='CMFPlomino_help_onDeleteDocument',
            i18n_domain='CMFPlomino',
        ),
        schemata="Events",
    ),
    TextField(
        name='beforeCreateDocument',
        widget=TextAreaWidget(
            label="Before document creation",
            description="Action to take when opening a blank form",
            label_msgid='CMFPlomino_label_beforeCreateDocument',
            description_msgid='CMFPlomino_help_beforeCreateDocument',
            i18n_domain='CMFPlomino',
        ),
        schemata="Events",
    ),
    TextField(
        name='FormLayout',
        widget=RichWidget(
            label="Form layout",
            description="The form layout. text with 'Plominofield' style correspond to the contained field elements",
            label_msgid='CMFPlomino_label_FormLayout',
            description_msgid='CMFPlomino_help_FormLayout',
            i18n_domain='CMFPlomino',
        ),
        default_output_type="text/html",
    ),
    TextField(
        name='DocumentTitle',
        widget=TextAreaWidget(
            label="Document title formula",
            description="Compute the document title",
            label_msgid='CMFPlomino_label_DocumentTitle',
            description_msgid='CMFPlomino_help_DocumentTitle',
            i18n_domain='CMFPlomino',
        ),
        schemata="Parameters",
    ),
    StringField(
        name='ActionBarPosition',
        default="TOP",
        widget=SelectionWidget(
            label="Position of the action bar",
            description="Select the position of the action bar",
            label_msgid='CMFPlomino_label_ActionBarPosition',
            description_msgid='CMFPlomino_help_ActionBarPosition',
            i18n_domain='CMFPlomino',
        ),
        schemata="Parameters",
        vocabulary=[["TOP", "At the top of the page"], ["BOTTOM", "At the bottom of the page"], ["BOTH", "At the top and at the bottom of the page "]],
    ),
    BooleanField(
        name='HideDefaultActions',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Hide default actions",
            description="Edit, Save, Delete, Close actions will not be displayed in the action bar",
            label_msgid='CMFPlomino_label_HideDefaultActions',
            description_msgid='CMFPlomino_help_HideDefaultActions',
            i18n_domain='CMFPlomino',
        ),
        schemata="Parameters",
    ),
    BooleanField(
        name='HideInMenu',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Hide in menu",
            description="It will not appear in the database main menu",
            label_msgid='CMFPlomino_label_HideInMenu',
            description_msgid='CMFPlomino_help_HideInMenu',
            i18n_domain='CMFPlomino',
        ),
        schemata="Parameters",
    ),
    BooleanField(
        name='isSearchForm',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Search form",
            description="A search form is only used to search documents, it cannot be saved.",
            label_msgid='CMFPlomino_label_SearchForm',
            description_msgid='CMFPlomino_help_SearchForm',
            i18n_domain='CMFPlomino',
        ),
        schemata="Parameters",
    ),
    BooleanField(
        name='isPage',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Page",
            description="A page cannot be saved and does not provide any action bar. It can be useful to build a welcome page, explanations, reports, navigation, etc.",
            label_msgid='CMFPlomino_label_isPage',
            description_msgid='CMFPlomino_help_isPage',
            i18n_domain='CMFPlomino',
        ),
        schemata="Parameters",
    ),
    StringField(
        name='SearchView',
        widget=StringField._properties['widget'](
            label="Search view",
            description="View used to display the search results",
            label_msgid='CMFPlomino_label_SearchView',
            description_msgid='CMFPlomino_help_SearchView',
            i18n_domain='CMFPlomino',
        ),
        schemata="Parameters",
    ),
    TextField(
        name='SearchFormula',
        widget=TextAreaWidget(
            label="Search formula",
            description="Leave blank to use default Zcatalog search",
            label_msgid='CMFPlomino_label_SearchFormula',
            description_msgid='CMFPlomino_help_SearchFormula',
            i18n_domain='CMFPlomino',
        ),
        schemata="Parameters",
    ),
    IntegerField(
        name='Position',
        widget=IntegerField._properties['widget'](
            label="Position",
            label_msgid="CMFPlomino_label_Position",
            description="Position in menu",
            description_msgid="CMFPlomino_help_Position",
            i18n_domain='CMFPlomino',
        ),
        schemata="Parameters",
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoForm_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoForm(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoForm)

    meta_type = 'PlominoForm'
    _at_rename_after_creation = True

    schema = PlominoForm_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declareProtected(CREATE_PERMISSION, 'createDocument')
    def createDocument(self,REQUEST):
        """create a document using the forms submitted content
        """
        db = self.getParentDatabase()
        
        is_childform = False
        parent_field = REQUEST.get("Plomino_Parent_Field", None)
        parent_form = REQUEST.get("Plomino_Parent_Form", None)
        if parent_field is not None:
            is_childform = True
            
        # validate submitted values
        errors=self.validateInputs(REQUEST)
        if len(errors)>0:
            if is_childform:
                return """<script>alert('erreur');</script>"""
            return self.notifyErrors(errors)
        
        # if child form
        if is_childform:
            tmp = TemporaryDocument(self.getParentDatabase(), self, REQUEST)
            tmp.setItem("Plomino_Parent_Field", parent_field)
            tmp.setItem("Plomino_Parent_Form", parent_form)
            return self.ChildForm(temp_doc=tmp)
            
        doc = db.createDocument()
        doc.setItem('Form', self.getFormName())
        
        # execute the onCreateDocument code of the form
        valid = ''
        valid = self.runFormulaScript("form_"+self.id+"_oncreate", doc, self.onCreateDocument)
        if valid is None or valid=='':
            doc.saveDocument(REQUEST, True)
        else:
            db.writeMessageOnPage(valid, REQUEST, '', False)
            REQUEST.RESPONSE.redirect(db.absolute_url())

    security.declarePublic('getFields')
    def getFields(self, includesubforms=False, doc=None):
        """get fields
        """
        fieldlist = self.portal_catalog.search({'portal_type' : ['PlominoField'], 'path': '/'.join(self.getPhysicalPath())})
        result = [f.getObject() for f in fieldlist]
        result.sort()
        if includesubforms:
            for subformname in self.getSubforms(doc):
                result=result+self.getParentDatabase().getForm(subformname).getFields(True)
        return result

    security.declarePublic('getHidewhenFormulas')
    def getHidewhenFormulas(self):
        """Get hidden formulae
        """
        list = self.portal_catalog.search({'portal_type' : ['PlominoHidewhen'], 'path': '/'.join(self.getPhysicalPath())})
        return [h.getObject() for h in list]

    security.declarePublic('getActions')
    def getActions(self, target, hide=True):
        """Get actions
        """
        all = self.portal_catalog.search({'portal_type' : ['PlominoAction'], 'path': '/'.join(self.getPhysicalPath())})

        filtered = []
        for a in all:
            obj_a=a.getObject()
            if hide:
                try:
                    #result = RunFormula(target, obj_a.getHidewhen())
                    result = self.runFormulaScript("action_"+self.id+"_"+obj_a.id+"_hidewhen", target, obj_a.Hidewhen)
                except Exception:
                    #if error, we hide anyway
                    result = True
                if not result:
                    filtered.append(obj_a)
            else:
                filtered.append(obj_a)
        return filtered

    security.declarePublic('getFormName')
    def getFormName(self):
        """Return the form name
        """
        return self.id

    security.declarePublic('getParentDatabase')
    def getParentDatabase(self):
        """Get the database containing this form
        """
        return self.getParentNode()


    security.declareProtected(READ_PERMISSION, 'displayDocument')
    def displayDocument(self,doc,editmode=False, creation=False, subform=False, request=None):
        """display the document using the form's layout
        """
        
        # remove the hidden content
        html_content = self.applyHideWhen(doc)
        
        #if editmode, we had a hidden field to handle the Form item value
        if editmode and not subform:
            html_content = "<input type='hidden' name='Form' value='"+self.getFormName()+"' />" + html_content

        # insert the fields with proper value and rendering
        for field in self.getFields():
            fieldName = field.id
            fieldblock='<span class="plominoFieldClass">'+fieldName+'</span>'
            if creation and not(fieldblock in html_content) and request is not None:
                html_content = "<input type='hidden' name='"+fieldName+"' value='"+str(request.get(fieldName,''))+"' />" + html_content
            html_content = html_content.replace(fieldblock, field.getFieldRender(self, doc, editmode, creation, request=request))

        # insert subforms
        for subformname in self.getSubforms(doc):
            subformrendering=self.getParentDatabase().getForm(subformname).displayDocument(doc, editmode, creation, subform=True, request=request)
            html_content = html_content.replace('<span class="plominoSubformClass">'+subformname+'</span>', subformrendering)

        # insert the actions
        if doc is None:
            target = self
        else:
            target = doc
        actionsToDisplay=[a.id for a in self.getActions(target, True)]
        for action in self.getActions(target, False):
            actionName = action.id
            if actionName in actionsToDisplay:
                actionDisplay = action.ActionDisplay
                pt=self.getRenderingTemplate(actionDisplay+"Action")
                if pt is None:
                    pt=self.getRenderingTemplate("LINKAction")
                action_render = pt(plominoaction=action, plominotarget=target)
            else:
                action_render=''
            html_content = html_content.replace('<span class="plominoActionClass">'+actionName+'</span>', action_render)

        return html_content

    security.declareProtected(READ_PERMISSION, 'childDocument')
    def childDocument(self,doc):
        """
        """
        parent_form = self.getParentDatabase().getForm(doc.Plomino_Parent_Form)
        parent_field = parent_form.getFormField(doc.Plomino_Parent_Field)
        fields = parent_field.getSettings().field_mapping.split(',')
        
        raw_values = []
        for f in fields:
            v = doc.getItem(f)
            if hasattr(v, 'strftime'):
                raw_values.append(DateToString(doc.getItem(f), self.getParentDatabase().getDateTimeFormat()))
            else:
                raw_values.append(v)
        
        html = """<div id="raw_values">%s</div>""" % json.dumps(raw_values)
        
        html = html + """<div id="parent_field">%s</div>""" % doc.Plomino_Parent_Field
        
        for f in fields:
            html = html + """<span id="%s" plomino="1">%s</span>""" % (f, doc.getRenderedItem(f, form=self))
        
        return html
                        
    security.declareProtected(READ_PERMISSION, 'applyHideWhen')
    def applyHideWhen(self, doc=None):
        """evaluate hide-when formula and return resulting layout
        """
        plone_tools = getToolByName(self, 'plone_utils')
        encoding = plone_tools.getSiteEncoding()
        html_content = self.getField('FormLayout').getRaw(self).decode(encoding)
        html_content = html_content.replace('\n', '')

        # remove the hidden content
        for hidewhen in self.getHidewhenFormulas():
            hidewhenName = hidewhen.id
            try:
                if doc is None:
                    target = self
                else:
                    target = doc
                result = self.runFormulaScript("hidewhen_"+self.id+"_"+hidewhen.id+"_formula", target, hidewhen.Formula)
            except Exception:
                #if error, we hide anyway
                result = True
            start = '<span class="plominoHidewhenClass">start:'+hidewhenName+'</span>'
            end = '<span class="plominoHidewhenClass">end:'+hidewhenName+'</span>'
            if result:
                regexp = start+'.+?'+end
                html_content = re.sub(regexp,'', html_content)
            else:
                html_content = html_content.replace(start, '')
                html_content = html_content.replace(end, '')
                
        return html_content
                
    security.declarePublic('formLayout')
    def formLayout(self, request=None):
        """return the form layout in edit mode (used to compose a new
        document)
        """
        return self.displayDocument(None, True, True, request=request)

    security.declarePublic('openBlankForm')
    def openBlankForm(self, request=None):
        """check beforeCreateDocument then open the form
        """
        # execute the beforeCreateDocument code of the form
        valid = ''
        if hasattr(self,'beforeCreateDocument') and self.beforeCreateDocument is not None:
            valid = self.runFormulaScript("form_"+self.id+"_beforecreate", self, self.beforeCreateDocument)
        if valid is None or valid=='':
            return self.displayDocument(None, True, True, request=request)
        else:
            self.REQUEST.RESPONSE.redirect(self.getParentDatabase().absolute_url()+"/ErrorsMessages?disable_border=1&error="+valid)
    
    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        """clean up the layout before saving
        """
        self.cleanFormulaScripts("form_"+self.id)

    security.declarePublic('getFormField')
    def getFormField(self, fieldname):
        """return the field
        """
        return getattr(self, fieldname, None)

    security.declarePublic('hasDateTimeField')
    def hasDateTimeField(self):
        """return true if the form contains at least one DateTime field
        or a datagrid (as a datagrid may contain a date)
        """
        fields=self.getFields(includesubforms=True)
        for f in fields:
            if f.getFieldType() in ["DATETIME", "DATAGRID"]:
                return True
        return False

    security.declarePublic('hasGoogleVisualizationField')
    def hasGoogleVisualizationField(self):
        """return true if the form contains at least one GoogleVisualization field
        """
        fields=self.getFields(includesubforms=True)
        for f in fields:
            if f.getFieldType() == "GOOGLEVISUALIZATION":
                return True
        return False
    
    security.declarePublic('getSubforms')
    def getSubforms(self, doc=None):
        """return the names of the subforms embedded in the form
        """
        html_content = html_content = self.applyHideWhen(doc)
        r = re.compile('<span class="plominoSubformClass">([^<]+)</span>')
        return [i.strip() for i in r.findall(html_content)]

    security.declarePublic('readInputs')
    def readInputs(self, doc, REQUEST, process_attachments=False):
        """ read submitted values in REQUEST and store them in document according
        fields definition
        """
        for f in self.getFields(includesubforms=True, doc=doc):
            mode = f.getFieldMode()
            fieldName = f.id
            if mode=="EDITABLE":
                submittedValue = REQUEST.get(fieldName)
                if submittedValue is not None:
                    if submittedValue=='':
                        doc.removeItem(fieldName)
                    else:
                        v = f.processInput(submittedValue, doc, process_attachments)
                        doc.setItem(fieldName, v)
                else:
                    #the field was not submitted, probably because it is not part of the form (hide-when, ...)
                    #so we just let it unchanged, but with SELECTION or DOCLINK, we need to presume it was empty
                    #(as SELECT/checkbox/radio tags do not submit an empty value, they are just missing
                    #in the querystring)
                    fieldtype = f.getFieldType()
                    if fieldtype == "SELECTION" or fieldtype == "DOCLINK":
                        doc.removeItem(fieldName)
                    

    security.declareProtected(READ_PERMISSION, 'searchDocuments')
    def searchDocuments(self,REQUEST):
        """search documents in the view matching the submitted form fields values
        """
        db = self.getParentDatabase()
        searchview = db.getView(self.getSearchView())

        #index search
        index = db.getIndex()
        query={'PlominoViewFormula_'+searchview.getViewName() : True}

        for f in self.getFields(includesubforms=True):
            fieldName = f.id
            #if fieldName is not an index -> search doesn't matter and returns all
            submittedValue = REQUEST.get(fieldName)
            if submittedValue is not None:
                if not submittedValue=='':
                    # if non-text field, convert the value
                    if f.getFieldType()=="NUMBER":
                        v = long(submittedValue)
                    elif f.getFieldType()=="FLOAT":
                        v = float(submittedValue)
                    elif f.getFieldType()=="DATETIME":
                        v = submittedValue
                    else:
                        v = submittedValue
                    query[fieldName]=v
        results=index.dbsearch(query, None)

        #filter search with searchformula
        searchformula=self.getSearchFormula()
        if searchformula:
            filteredResults = []
            for doc in results:
                try:
                    valid = self.runFormulaScript("form_"+self.id+"_searchformula", doc.getObject(), self.SearchFormula)
                except Exception, e:
                    valid = False
                if valid:
                    filteredResults.append(doc)
            results = filteredResults

        return self.OpenForm(searchresults=results)

    security.declarePublic('validateInputs')
    def validateInputs(self, REQUEST, doc=None):
        errors=[]
        for f in self.getFields(includesubforms=True, doc=doc):
            fieldname = f.id
            fieldtype = f.getFieldType()
            submittedValue = REQUEST.get(fieldname)

            # STEP 1: check mandatory fields
            if submittedValue is None or submittedValue=='':
                if f.getMandatory()==True:
                    errors.append(fieldname+" "+PlominoTranslate("is mandatory",self))
            else:
                # STEP 2: check data types
                errors = errors + f.validateFormat(submittedValue)
                
        if len(errors)==0:
            # STEP 3: check validation formula
            tmp = TemporaryDocument(self.getParentDatabase(), self, REQUEST, doc)
            for f in self.getFields(includesubforms=True):
                formula = f.getValidationFormula()
                if not formula=='':
                    s=''
                    try:
                        s = self.runFormulaScript("field_"+self.id+"_"+f.id+"_ValidationFormula", tmp, f.ValidationFormula)
                    except:
                        pass
                    if not s=='':
                        errors.append(s)

        return errors

    security.declarePublic('notifyErrors')
    def notifyErrors(self, errors):
        return self.ErrorsMessages(errors=errors)

    security.declarePublic('getPosition')
    def getPosition(self):
        """Return the form position in the database
        """
        try :
            return self.Position
        except Exception :
            return None

    security.declarePublic('isNewDocument')
    def isNewDocument(self):
        """
        """
        # when the context is a form, it is necessarily a new doc
        return True
        
    security.declarePublic('isEditMode')
    def isEditMode(self):
        """
        """
        # if REQUEST exists, test the current command
        if hasattr(self, 'REQUEST'):
            command=self.REQUEST.URL.split('/')[-1].lower()
            return command in ['openform', 'edit']
        else:
            return False
    
registerType(PlominoForm, PROJECTNAME)
# end of class PlominoForm

##code-section module-footer #fill in your manual code here
##/code-section module-footer




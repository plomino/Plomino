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
from Products.CMFPlomino.exceptions import PlominoDesignException

##code-section module-header #fill in your manual code here
import sys
import re
import simplejson as json

from Products.CMFCore.utils import getToolByName

from exceptions import PlominoScriptException
import PlominoDocument
from PlominoDocument import TemporaryDocument

import logging
logger = logging.getLogger('Plomino')

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
            description="Action to take when the document is opened",
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
        name='onSearch',
        widget=TextAreaWidget(
            label="On submssion of search form",
            description="Action to take when submitting a search",
            label_msgid='CMFPlomino_label_onSearch',
            description_msgid='CMFPlomino_help_onSearch',
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
    ),
    TextField(
        name='DocumentId',
        widget=TextAreaWidget(
            label="Document id formula",
            description="Compute the document id at creation. Must be globally unique if intended to sync with other databases.",
            label_msgid='CMFPlomino_label_DocumentId',
            description_msgid='CMFPlomino_help_DocumentId',
            i18n_domain='CMFPlomino',
        ),
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
#        schemata="Parameters",
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
#        schemata="Parameters",
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
#        schemata="Parameters",
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
#        schemata="Parameters",
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
#        schemata="Parameters",
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
#        schemata="Parameters",
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
#        schemata="Parameters",
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
#        schemata="Parameters",
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
    _at_rename_after_creation = False

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

        # Check for None: the request might yield an empty string.
        # TODO: try not to put misleading Plomino_* fields on the request.
        if parent_field is not None:
            is_childform = True

        # validate submitted values
        errors=self.validateInputs(REQUEST)
        if len(errors)>0:
            if is_childform:
                return """<html><body><span id="plomino_child_errors">%s</span></body></html>""" % " - ".join(errors)
            return self.notifyErrors(errors)

        # if child form
        if is_childform:
            tmp = TemporaryDocument(self.getParentDatabase(), self, REQUEST)
            tmp.setItem("Plomino_Parent_Field", parent_field)
            tmp.setItem("Plomino_Parent_Form", parent_form)
            tmp.setItem(parent_field+"_itemnames", [
                f.getId() for f in self.getFormFields() 
                if not f.getFieldMode() == 'DISPLAY'])
            return self.ChildForm(temp_doc=tmp)

        doc = db.createDocument()
        doc.setItem('Form', self.getFormName())

        # execute the onCreateDocument code of the form
        valid = ''
        try:
            valid = self.runFormulaScript("form_"+self.id+"_oncreate", doc, self.onCreateDocument)
        except PlominoScriptException, e:
            e.reportError('Document is created, but onCreate formula failed')

        if valid is None or valid=='':
            doc.saveDocument(REQUEST, True)
        else:
            db.documents._delOb(doc.id)
            db.writeMessageOnPage(valid, REQUEST, False)
            REQUEST.RESPONSE.redirect(db.absolute_url())

    security.declarePublic('getFormFields')
    def getFormFields(self, includesubforms=False, doc=None, applyhidewhen=False):
        """get fields
        """
#        fieldlist = self.portal_catalog.search({'portal_type' : ['PlominoField'], 'path': '/'.join(self.getPhysicalPath())})
#        result = [f.getObject() for f in fieldlist]
        fieldlist = self.objectValues(spec='PlominoField')
        result = [f for f in fieldlist]
        if applyhidewhen:
            layout = self.applyHideWhen(doc)
            result = [f for f in result if """<span class="plominoFieldClass">%s</span>""" % f.id in layout]
        result.sort(key=lambda elt: elt.id.lower())
        if includesubforms:
            subformsseen = []
            for subformname in self.getSubforms(doc, applyhidewhen):
                if subformname in subformsseen:
                    continue
                subform = self.getParentDatabase().getForm(subformname)
                if subform:
                    result=result + subform.getFormFields(includesubforms=True, doc=doc, applyhidewhen=applyhidewhen)
                subformsseen.append(subformname)
        return result

    security.declarePublic('getHidewhenFormulas')
    def getHidewhenFormulas(self):
        """Get hidden formulae
        """
        #list = self.portal_catalog.search({'portal_type' : ['PlominoHidewhen'], 'path': '/'.join(self.getPhysicalPath())})
        hidewhens = self.objectValues(spec='PlominoHidewhen')
        return [h for h in hidewhens]

    security.declarePublic('getActions')
    def getActions(self, target, hide=True, parent_id=None):
        """Get actions
        """
        #all = self.portal_catalog.search({'portal_type' : ['PlominoAction'], 'path': '/'.join(self.getPhysicalPath())})
        all = self.objectValues(spec='PlominoAction')

        filtered = []
        for obj_a in all:
            #obj_a=a.getObject()
            if hide:
                try:
                    #result = RunFormula(target, obj_a.getHidewhen())
                    result = self.runFormulaScript("action_"+self.id+"_"+obj_a.id+"_hidewhen", target, obj_a.Hidewhen, True, parent_id)
                except PlominoScriptException, e:
                    e.reportError('"%s" hide-when formula failed' % obj_a.Title())
                    #if error, we hide anyway
                    result = True
                if not result:
                    filtered.append((obj_a, parent_id))
            else:
                filtered.append((obj_a, parent_id))
        return filtered

    security.declarePublic('getCacheFormulas')
    def getCacheFormulas(self):
        """Get cache formulae
        """
        cacheformula = self.objectValues(spec='PlominoCache')
        return [c for c in cacheformula]
    
    security.declarePublic('getFormName')
    def getFormName(self):
        """Return the form name
        """
        return self.id


    security.declareProtected(READ_PERMISSION, 'displayDocument')
    def displayDocument(self, doc, editmode=False, creation=False, parent_form_id=False, request=None):
        """display the document using the form's layout
        """

        # remove the hidden content
        html_content = self.applyHideWhen(doc, silent_error=False)
        
        # evaluate cache formulae and insert already cached fragment
        (html_content, to_be_cached) = self.applyCache(html_content, doc)

        #if editmode, we had a hidden field to handle the Form item value
        if editmode and not parent_form_id:
            html_content = "<input type='hidden' name='Form' value='"+self.getFormName()+"' />" + html_content

        # insert the fields with proper value and rendering
        for field in self.getFormFields(doc=doc, applyhidewhen=False):
            fieldName = field.id
            fieldblock='<span class="plominoFieldClass">'+fieldName+'</span>'
            if creation and not(fieldblock in html_content) and request is not None:
                if request.has_key(fieldName):
                    html_content = "<input type='hidden' name='"+fieldName+"' value='"+str(request.get(fieldName,''))+"' />" + html_content
            if fieldblock in html_content:
                html_content = html_content.replace(fieldblock, field.getFieldRender(self, doc, editmode, creation, request=request))

        # insert subforms
        for subformname in self.getSubforms(doc):
            subform = self.getParentDatabase().getForm(subformname)
            if subform:
                subformrendering = subform.displayDocument(
                    doc, editmode, creation, parent_form_id=self.id,
                    request=request)
                html_content = html_content.replace('<span class="plominoSubformClass">'+subformname+'</span>', subformrendering)

        # insert the actions
        if doc is None:
            target = self
        else:
            target = doc
        form_id = parent_form_id and parent_form_id or self.id
        actionsToDisplay = [a.id for a, f_id in self.getActions(
            target, hide=True, parent_id=form_id)]
        for action, form_id in self.getActions(target, False, parent_id=form_id):
            actionName = action.id
            if actionName in actionsToDisplay:
                actionDisplay = action.ActionDisplay
                pt=self.getRenderingTemplate(actionDisplay+"Action")
                if pt is None:
                    pt=self.getRenderingTemplate("LINKAction")
                action_render = pt(plominoaction=action,
                                   plominotarget=target,
                                   plomino_parent_id=form_id)
            else:
                action_render=''
            html_content = html_content.replace('<span class="plominoActionClass">'+actionName+'</span>', action_render)
        
        # store fragment to cache
        html_content = self.updateCache(html_content, to_be_cached)
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
            html = html + """<span id="%s" class="plominochildfield">%s</span>""" % (f, doc.getRenderedItem(f, form=self))

        return html

    security.declareProtected(READ_PERMISSION, 'applyHideWhen')
    def applyHideWhen(self, doc=None, silent_error=True):
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
            except PlominoScriptException, e:
                if not silent_error:
                    # applyHideWhen is called by getFormFields and getSubForms, in those cases, error reporting
                    # is not accurate,
                    # we only need error reporting when actually rendering a page
                    e.reportError('%s hide-when formula failed' % hidewhen.id, request=getattr(self, 'REQUEST', None))
                #if error, we hide anyway
                result = True
            start = '<span class="plominoHidewhenClass">start:'+hidewhenName+'</span>'
            end = '<span class="plominoHidewhenClass">end:'+hidewhenName+'</span>'

            if getattr(hidewhen, 'isDynamicHidewhen', False):
                if result:
                    style = ' style="display: none"'
                else:
                    style = ''
                html_content = re.sub(start,'<div class="hidewhen-' + hidewhenName + '"' + style + '>', html_content, re.MULTILINE+re.DOTALL)
                html_content = re.sub(end,'</div>', html_content, re.MULTILINE+re.DOTALL)
            else:
                if result:
                    regexp = start+'.*?'+end
                    html_content = re.sub(regexp,'', html_content, re.MULTILINE+re.DOTALL)
                else:
                    html_content = html_content.replace(start, '')
                    html_content = html_content.replace(end, '')

        return html_content

    security.declareProtected(READ_PERMISSION, 'hasDynamicHidewhen')
    def hasDynamicHidewhen(self):
        """Search if a dynamic hidewhen is stored in the form
        """
        for hidewhen in self.getHidewhenFormulas():
           if getattr(hidewhen, 'isDynamicHidewhen', False):
               return True
        return False

    security.declareProtected(READ_PERMISSION, 'getHidewhenAsJSON')
    def getHidewhenAsJSON(self, REQUEST):
        """Return a JSON object to dynamically show or hide hidewhens (works only with isDynamicHidewhen)
        """
        result = {}
        target = TemporaryDocument(self.getParentDatabase(), self, REQUEST)
        for hidewhen in self.getHidewhenFormulas():
            if getattr(hidewhen, 'isDynamicHidewhen', False):
                try:
                    isHidden = self.runFormulaScript("hidewhen_"+self.id+"_"+hidewhen.id+"_formula", target, hidewhen.Formula)
                except PlominoScriptException, e:
                    e.reportError('%s hide-when formula failed' % hidewhen.id)
                    #if error, we hide anyway
                    isHidden = True
                result[hidewhen.id] = isHidden 

        return json.dumps(result)

    security.declareProtected(READ_PERMISSION, 'applyCache')
    def applyCache(self, html_content, doc=None):
        """evaluate cache formula and return resulting layout
        """
        
        to_be_cached = {}
        for cacheformula in self.getCacheFormulas():
            cacheid = cacheformula.id
            try:
                if doc is None:
                    target = self
                else:
                    target = doc
                cachekey = self.runFormulaScript("cache_"+self.id+"_"+cacheid+"_formula", target, cacheformula.Formula)
            except PlominoScriptException, e:
                e.reportError('%s cache formula failed' % cacheid, request=getattr(self, 'REQUEST', None))
                cachekey = None
                
            start = '<span class="plominoCacheClass">start:'+cacheid+'</span>'
            end = '<span class="plominoCacheClass">end:'+cacheid+'</span>'

            if cachekey:
                cachekey = 'fragment_'+cachekey
                fragment = self.getParentDatabase().getCache(cachekey)
                if fragment:
                    # the fragment was in cache, we insert it
                    regexp = start+'.*?'+end
                    html_content = re.sub(regexp, fragment, html_content, re.MULTILINE+re.DOTALL)
                else:
                    # the fragment is not cached yet, we let the marker
                    # they will be used after rendering to extract the fragment
                    # and store it in cache
                    to_be_cached[cacheid] = cachekey
            else:
                # no cache needed: we just remove the markers, the fragment
                # will processed regularly with no caching
                html_content = html_content.replace(start, '')
                html_content = html_content.replace(end, '')

        return (html_content, to_be_cached)

    security.declareProtected(READ_PERMISSION, 'updateCache')
    def updateCache(self, html_content, to_be_cached):
        """
        """
        db = self.getParentDatabase()
        for cacheid in to_be_cached.keys():
            start = '<span class="plominoCacheClass">start:'+cacheid+'</span>'
            end = '<span class="plominoCacheClass">end:'+cacheid+'</span>'
            regexp = start+'(.*?)'+end
            search_fragment = re.findall(regexp, html_content, re.MULTILINE+re.DOTALL)
            if len(search_fragment) > 0:
                fragment = search_fragment[0]
                db.setCache(to_be_cached[cacheid], fragment)
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
        invalid = False
        if hasattr(self,'beforeCreateDocument') and self.beforeCreateDocument is not None:
            try:
                invalid = self.runFormulaScript("form_"+self.id+"_beforecreate", self, self.beforeCreateDocument)
            except PlominoScriptException, e:
                e.reportError('beforeCreate formula failed')

        if (not invalid) or self.hasDesignPermission(self):
            return self.displayDocument(None, editmode=True, creation=True, request=request)
        else:
            self.REQUEST.RESPONSE.redirect(self.getParentDatabase().absolute_url()+"/ErrorMessages?disable_border=1&error="+invalid)

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        """clean up the layout before saving
        """
        self.cleanFormulaScripts("form_"+self.id)

    security.declarePublic('getFormField')
    def getFormField(self, fieldname, includesubforms=True):
        """return the field
        """
        field = getattr(self, fieldname, None)
        # if field is not in main form, we search in the subforms
        if not field:
            all_fields = self.getFormFields(includesubforms=includesubforms)
            matching_fields = [f for f in all_fields if f.id == fieldname]
            if matching_fields:
                if len(matching_fields) == 1:
                    field = matching_fields[0]
                else:
                    raise (PlominoDesignException,
                        'Ambiguous fieldname: %s' %`[
                            '/'.join(f.getPhysicalPath()) for f in matching_fields]`)
        return field

    security.declarePublic('computeFieldValue')
    def computeFieldValue(self, fieldname, target, report=True):
        """evalute field formula over target
        """
        field = self.getFormField(fieldname)
        fieldvalue = None
        if field:
            db = self.getParentDatabase()
            try:
                fieldvalue = db.runFormulaScript("field_"+self.id+"_"+fieldname+"_formula", target, field.Formula, True, self)
            except PlominoScriptException, e:
                if report:
                    e.reportError('%s field formula failed' % fieldname)

        return fieldvalue

    security.declarePublic('hasDateTimeField')
    def hasDateTimeField(self):
        """return true if the form contains at least one DateTime field
        or a datagrid (as a datagrid may contain a date)
        """
        fields=self.getFormFields(includesubforms=True, applyhidewhen=True)
        for f in fields:
            if f.getFieldType() in ["DATETIME", "DATAGRID"]:
                return True
        return False

    security.declarePublic('hasGoogleVisualizationField')
    def hasGoogleVisualizationField(self):
        """return true if the form contains at least one GoogleVisualization field
        """
        fields=self.getFormFields(includesubforms=True, applyhidewhen=True)
        for f in fields:
            if f.getFieldType() == "GOOGLEVISUALIZATION":
                return True
        return False

    security.declarePublic('getSubforms')
    def getSubforms(self, doc=None, applyhidewhen=True):
        """return the names of the subforms embedded in the form
        """
        if applyhidewhen:
            html_content = self.applyHideWhen(doc)
        else:
            plone_tools = getToolByName(self, 'plone_utils')
            encoding = plone_tools.getSiteEncoding()
            html_content = self.getField('FormLayout').getRaw(self).decode(encoding)
            html_content = html_content.replace('\n', '')

        r = re.compile('<span class="plominoSubformClass">([^<]+)</span>')
        return [i.strip() for i in r.findall(html_content)]

    security.declarePublic('readInputs')
    def readInputs(self, doc, REQUEST, process_attachments=False, applyhidewhen=True):
        """ read submitted values in REQUEST and store them in document according
        fields definition
        """
        all_fields = self.getFormFields(includesubforms=True, doc=doc, applyhidewhen=False)
        if applyhidewhen:
            displayed_fields = self.getFormFields(includesubforms=True, doc=doc, applyhidewhen=True)

        for f in all_fields:
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
                    if applyhidewhen and f in displayed_fields:
                        fieldtype = f.getFieldType()
                        if fieldtype == "SELECTION" or fieldtype == "DOCLINK":
                            doc.removeItem(fieldName)

    security.declareProtected(READ_PERMISSION, 'searchDocuments')
    def searchDocuments(self,REQUEST):
        """search documents in the view matching the submitted form fields values
        """
        if self.onSearch:
            # Manually generate a result set
            try:
                results = self.runFormulaScript("form_"+self.id+"_onsearch", self, self.onSearch)
            except PlominoScriptException, e:
                if self.REQUEST:
                    e.reportError('Search event failed.')
                    self.OpenForm(searchresults=[])
        else:
            # Allow Plomino to filter by view, default query, and formula
            db = self.getParentDatabase()
            searchview = db.getView(self.getSearchView())

            #index search
            index = db.getIndex()
            query={'PlominoViewFormula_'+searchview.getViewName() : True}

            for f in self.getFormFields(includesubforms=True):
                fieldname = f.id
                #if fieldname is not an index -> search doesn't matter and returns all
                submittedValue = REQUEST.get(fieldname)
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
                        # rename Plomino_SearchableText to perform full-text searches on
                        # regular SearchableText index
                        if fieldname == "Plomino_SearchableText":
                            fieldname = "SearchableText"
                        query[fieldname]=v
            results=index.dbsearch(query, None)

            #filter search with searchformula
            searchformula=self.getSearchFormula()
            if searchformula:
                filteredResults = []
                try:
                    for doc in results:
                        valid = self.runFormulaScript("form_"+self.id+"_searchformula", doc.getObject(), self.SearchFormula)
                        if valid:
                            filteredResults.append(doc)
                except PlominoScriptException, e:
                    e.reportError('Search formula failed')
                results = filteredResults

        return self.OpenForm(searchresults=results)

    security.declarePublic('validateInputs')
    def validateInputs(self, REQUEST, doc=None):
        errors=[]
        fields = self.getFormFields(includesubforms=True, doc=doc, applyhidewhen=True)
        for f in fields:
            fieldname = f.id
            fieldtype = f.getFieldType()
            submittedValue = REQUEST.get(fieldname)

            # STEP 1: check mandatory fields
            if not submittedValue:
                if f.getMandatory()==True:
                    if fieldtype == "ATTACHMENT" and doc:
                        existing_files = doc.getItem(fieldname)
                        if not existing_files:
                            errors.append(fieldname+" "+PlominoTranslate("is mandatory",self))
                    else:
                        errors.append(fieldname+" "+PlominoTranslate("is mandatory",self))
            else:
                # STEP 2: check data types
                errors = errors + f.validateFormat(submittedValue)

        if len(errors)==0:
            # STEP 3: check validation formula
            tmp = TemporaryDocument(self.getParentDatabase(), self, REQUEST, doc)
            for f in fields:
                formula = f.getValidationFormula()
                if not formula=='':
                    s=''
                    try:
                        s = self.runFormulaScript("field_"+self.id+"_"+f.id+"_ValidationFormula", tmp, f.ValidationFormula)
                    except PlominoScriptException, e:
                        e.reportError('%s validation formula failed' % f.id)
                    if not s=='':
                        errors.append(s)

        return errors

    security.declarePublic('notifyErrors')
    def notifyErrors(self, errors):
        return self.ErrorMessages(errors=errors)

    security.declareProtected(DESIGN_PERMISSION, 'manage_generateView')
    def manage_generateView(self, REQUEST=None):
        """ create a view automatically
        where selection is : plominoDocument.Form == "this_form"
        and displaying a column for all the acceptable fields
        (i.e. editable and not richtext, file attachment, datagrid, ...
        which might need reformatting)
        """
        db = self.getParentDatabase()
        view_id = "all" + self.id.replace('_', '').replace('-', '')
        if view_id in db.objectIds():
            if REQUEST:
                plone_tools = getToolByName(self, 'plone_utils')
                plone_tools.addPortalMessage('%s is already an existing object.' % view_id, 'error', REQUEST)
                REQUEST.RESPONSE.redirect(self.absolute_url_path())
            return
        view_title = "All " + self.Title()
        formula = 'plominoDocument.Form=="%s"' % self.id
        db.invokeFactory('PlominoView',
                         id=view_id,
                         title=view_title,
                         SelectionFormula=formula)
        view_obj = getattr(db, view_id)
        view_obj.at_post_create_script()
        
        fields = self.getFormFields(includesubforms=True)
        acceptable_types = ["TEXT", "NUMBER", "NAME", "SELECTION", "DATETIME"]
        fields = [f for f in fields if f.getFieldMode()=="EDITABLE" and f.FieldType in acceptable_types]
        for f in fields:
            col_id = f.id.replace('_', '').replace('-', '')
            col_title = col_id
            col_definition = self.id + '/' + f.id
            view_obj.invokeFactory('PlominoColumn',
                                      id=col_id,
                                      title=col_title,
                                      SelectedField=col_definition)
            getattr(view_obj, col_id).at_post_create_script()
        view_obj.invokeFactory('PlominoAction',
                                  id='add_new',
                                  title="Add a new "+self.Title(),
                                  ActionType="OPENFORM",
                                  ActionDisplay="BUTTON",
                                  Content=self.id)
        
        if REQUEST:
            REQUEST.RESPONSE.redirect(view_obj.absolute_url_path())
        
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

    security.declarePublic('isDocument')
    def isDocument(self):
        """
        """
        return False
    
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



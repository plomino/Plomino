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

# Standard
import re

import logging
logger = logging.getLogger('Plomino')

# Third-party
from jsonutil import jsonutil as json

# Zope
from AccessControl import ClassSecurityInfo
from zope.interface import implements

# CMF / Archetypes / Plone
from Products.Archetypes.atapi import *
from Products.ATContentTypes.content.folder import ATFolder

# Plomino
from exceptions import PlominoScriptException
from PlominoDocument import TemporaryDocument
from Products.CMFCore.utils import getToolByName
from Products.CMFPlomino.config import *
from Products.CMFPlomino.browser import PlominoMessageFactory as _
from Products.CMFPlomino import plomino_profiler
from Products.CMFPlomino.PlominoUtils import asList
from Products.CMFPlomino.PlominoUtils import asUnicode
from Products.CMFPlomino.PlominoUtils import DateToString, StringToDate
from Products.CMFPlomino.PlominoUtils import PlominoTranslate
from Products.CMFPlomino.PlominoUtils import translate
import interfaces

schema = Schema((
    StringField(
        name='id',
        widget=StringField._properties['widget'](
            label="Id",
            description="The form id",
            label_msgid=_('CMFPlomino_label_FormId', default="Id"),
            description_msgid=_('CMFPlomino_help_FormId', default='The form id'),
            i18n_domain='CMFPlomino',
        ),
    ),
    TextField(
        name='onCreateDocument',
        widget=TextAreaWidget(
            label="On create document",
            description="Action to take when the document is created",
            label_msgid=_('CMFPlomino_label_onCreateDocument', default="On create document"),
            description_msgid=_('CMFPlomino_help_onCreateDocument', default="Action to take when the document is created"),
            i18n_domain='CMFPlomino',
        ),
        schemata="Events",
    ),
    TextField(
        name='onOpenDocument',
        widget=TextAreaWidget(
            label="On open document",
            description="Action to take when the document is opened",
            label_msgid=_('CMFPlomino_label_onOpenDocument', default="On open document"),
            description_msgid=_('CMFPlomino_help_onOpenDocument', default="Action to take when the document is opened"),
            i18n_domain='CMFPlomino',
        ),
        schemata="Events",
    ),
    TextField(
        name='beforeSaveDocument',
        widget=TextAreaWidget(
            label="Before save document",
            description="Action to take before submitted values are saved into the document (submitted values are in context.REQUEST)",
            label_msgid=_('CMFPlomino_label_beforeSaveDocument', default="Before save document"),
            description_msgid=_('CMFPlomino_help_beforeSaveDocument', default="Action to take before submitted values are saved into the document (submitted values are in context.REQUEST)"),
            i18n_domain='CMFPlomino',
        ),
        schemata="Events",
    ),
    TextField(
        name='onSaveDocument',
        widget=TextAreaWidget(
            label="On save document",
            description="Action to take when saving the document",
            label_msgid=_('CMFPlomino_label_onSaveDocument', default="On save document"),
            description_msgid=_('CMFPlomino_help_onSaveDocument', default="Action to take when saving the document"),
            i18n_domain='CMFPlomino',
        ),
        schemata="Events",
    ),
    TextField(
        name='onDeleteDocument',
        widget=TextAreaWidget(
            label="On delete document",
            description="Action to take before deleting the document",
            label_msgid=_('CMFPlomino_label_onDeleteDocument', default="On delete document"),
            description_msgid=_('CMFPlomino_help_onDeleteDocument', default="Action to take before deleting the document"),
            i18n_domain='CMFPlomino',
        ),
        schemata="Events",
    ),
    TextField(
        name='onSearch',
        widget=TextAreaWidget(
            label="On submission of search form",
            description="Action to take when submitting a search",
            label_msgid=_('CMFPlomino_label_onSearch', default="On submission of search form"),
            description_msgid=_('CMFPlomino_help_onSearch', default="Action to take when submitting a search"),
            i18n_domain='CMFPlomino',
        ),
        schemata="Events",
    ),
    TextField(
        name='beforeCreateDocument',
        widget=TextAreaWidget(
            label="Before document creation",
            description="Action to take when opening a blank form",
            label_msgid=_('CMFPlomino_label_beforeCreateDocument', default="Before document creation"),
            description_msgid=_('CMFPlomino_help_beforeCreateDocument', default="Action to take when opening a blank form"),
            i18n_domain='CMFPlomino',
        ),
        schemata="Events",
    ),
    TextField(
        name='FormLayout',
        widget=RichWidget(
            label="Form layout",
            description="The form layout. Text with 'Plominofield' styles "
                "correspond to the contained field elements.",
            label_msgid=_('CMFPlomino_label_FormLayout', default="Form layout"),
            description_msgid=_('CMFPlomino_help_FormLayout', default="The form layout. Text with 'Plominofield' styles correspond to the contained field elements."),
            i18n_domain='CMFPlomino',
        ),
        default_output_type="text/html",
    ),
    TextField(
        name='FormMethod',
        accessor='getFormMethod',
        default='Auto',
        widget=SelectionWidget(
            label="Form method",
            description="The form method: GET, POST or Auto (default).",
            label_msgid=_('CMFPlomino_label_FormMethod', default="Form method"),
            description_msgid=_('CMFPlomino_help_FormMethod', default="The form method: GET or POST or Auto (default)."),
            i18n_domain='CMFPlomino',
        ),
        vocabulary=('GET', 'POST', 'Auto')
    ),
    TextField(
        name='DocumentTitle',
        widget=TextAreaWidget(
            label="Document title formula",
            description="Compute the document title",
            label_msgid=_('CMFPlomino_label_DocumentTitle', default="Document title formula"),
            description_msgid=_('CMFPlomino_help_DocumentTitle', default='Compute the document title'),
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='DynamicDocumentTitle',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Compute document title on view",
            description="Execute DocumentTitle formula when document is rendered",
            label_msgid=_('CMFPlomino_label_DynamicDocumentTitle', default="Compute document title on view"),
            description_msgid=_('CMFPlomino_help_DynamicDocumentTitle', default="Execute DocumentTitle formula when document is rendered"),
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='StoreDynamicDocumentTitle',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Store dynamically computed title",
            description="Store computed title every time document is rendered",
            label_msgid=_('CMFPlomino_label_StoreDynamicDocumentTitle', default="Store dynamically computed title"),
            description_msgid=_('CMFPlomino_help_StoreDynamicDocumentTitle', default="Store computed title every time document is rendered"),
            i18n_domain='CMFPlomino',
        ),
    ),
    TextField(
        name='DocumentId',
        widget=TextAreaWidget(
            label="Document id formula",
            description="Compute the document id at creation. "
                "(Undergoes normalization.)",
            label_msgid=_('CMFPlomino_label_DocumentId', default="Document id formula"),
            description_msgid=_('CMFPlomino_help_DocumentId', default='Compute the document id at creation. (Undergoes normalization.)'),
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='ActionBarPosition',
        default="TOP",
        widget=SelectionWidget(
            label="Position of the action bar",
            description="Select the position of the action bar",
            label_msgid=_('CMFPlomino_label_ActionBarPosition', default="Position of the action bar"),
            description_msgid=_('CMFPlomino_help_ActionBarPosition', default="Select the position of the action bar"),
            i18n_domain='CMFPlomino',
        ),
        vocabulary=[
            ["TOP", "At the top of the page"],
            ["BOTTOM", "At the bottom of the page"],
            ["BOTH", "At the top and at the bottom of the page "]],
    ),
    BooleanField(
        name='HideDefaultActions',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Hide default actions",
            description="Edit, Save, Delete, Close actions "
                "will not be displayed in the action bar",
            label_msgid=_('CMFPlomino_label_HideDefaultActions', default="Hide default actions"),
            description_msgid=_('CMFPlomino_help_HideDefaultActions', default='Edit, Save, Delete, Close actions will not be displayed in the action bar'),
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='HideInMenu',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Hide in menu",
            description="It will not appear in the database main menu",
            label_msgid=_('CMFPlomino_label_HideInMenu', default="Hide in menu"),
            description_msgid=_('CMFPlomino_help_HideInMenu', default='It will not appear in the database main menu'),
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='isSearchForm',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Search form",
            description="A search form is only used to search documents, "
                "it cannot be saved.",
            label_msgid=_('CMFPlomino_label_SearchForm', default="Search form"),
            description_msgid=_('CMFPlomino_help_SearchForm', default="A search form is only used to search documents, it cannot be saved."),
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='isPage',
        default="0",
        widget=BooleanField._properties['widget'](
            label="Page",
            description="A page cannot be saved and does not provide "
                "any action bar. It can be useful to build a welcome page, "
                "explanations, reports, navigation, etc.",
            label_msgid=_('CMFPlomino_label_isPage', default="Page"),
            description_msgid=_('CMFPlomino_help_isPage', default="A page cannot be saved and does not provide any action bar. It can be useful to build a welcome page, explanations, reports, navigation, etc."),
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='SearchView',
        widget=SelectionWidget(
            label="Search view",
            description="View used to display the search results",
            format='select',
            label_msgid=_('CMFPlomino_label_SearchView', default="Search view"),
            description_msgid=_('CMFPlomino_help_SearchView', default="View used to display the search results"),
            i18n_domain='CMFPlomino',
        ),
        vocabulary='_getDatabaseViews',
    ),
    TextField(
        name='SearchFormula',
        widget=TextAreaWidget(
            label="Search formula",
            description="Leave blank to use default ZCatalog search",
            label_msgid=_('CMFPlomino_label_SearchFormula', default="Search formula"),
            description_msgid=_('CMFPlomino_help_SearchFormula', default="Leave blank to use default ZCatalog search"),
            i18n_domain='CMFPlomino',
        ),
    ),
    IntegerField(
        name='Position',
        widget=IntegerField._properties['widget'](
            label="Position",
            label_msgid=_("CMFPlomino_label_Position", default="Position"),
            description="Position in menu",
            description_msgid=_("CMFPlomino_help_Position", default="Position in menu"),
            i18n_domain='CMFPlomino',
        ),
    ),
),
)

PlominoForm_schema = getattr(ATFolder, 'schema', Schema(())).copy() + \
    schema.copy()

label_re =  re.compile('<span class="plominoLabelClass">((?P<optional_fieldname>\S+):){0,1}\s*(?P<fieldname_or_label>.+?)</span>')
# Not bothering with Legend for now. Label will generate a fieldset and legend for CHECKBOX and RADIO widgets.
# legend_re = re.compile('<span class="plominoLegendClass">((?P<optional_fieldname>\S+):){0,1}\s*(?P<fieldname_or_label>.+)</span>')

class PlominoForm(ATFolder):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoForm)

    meta_type = 'PlominoForm'
    _at_rename_after_creation = False

    schema = PlominoForm_schema

    def getForm(self, formname=None):
        """ In case we're being called via acquisition.
        """
        if formname:
            return self.getParentDatabase().getForm(self, formname)

        form = self
        while getattr(form, 'meta_type', '') != 'PlominoForm':
            form = obj.aq_parent
        return form

    def getFormMethod(self):
        """ Return form submit HTTP method
        """
        # if self.isEditMode():
        #     Log('POST because isEditMode', 'PlominoForm/getFormMethod') #DBG 
        #     return  'POST'

        value = self.Schema()['FormMethod'].get(self)
        if value == 'Auto':
            if self.isPage or self.isSearchForm:
                return 'GET'
            else:
                return 'POST'
        return value

    security.declareProtected(READ_PERMISSION, 'createDocument')
    def createDocument(self, REQUEST):
        """ Create a document using the form's submitted content.

        The created document may be a TemporaryDocument, in case 
        this form was rendered as a child form. In this case, we 
        aren't adding a document to the database yet.

        If we are not a child form, delegate to the database object 
        to create the new document.
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
        errors = self.validateInputs(REQUEST)
        if errors:
            if is_childform:
                return ("""<html><body><span id="plomino_child_errors">"""
                    """%s</span></body></html>""" % " - ".join(errors))
            return self.notifyErrors(errors)

        ################################################################
        # If child form, return a TemporaryDocument
        if is_childform:
            tmp = TemporaryDocument(db, self, REQUEST).__of__(db)
            tmp.setItem("Plomino_Parent_Field", parent_field)
            tmp.setItem("Plomino_Parent_Form", parent_form)
            tmp.setItem(
                    parent_field + "_itemnames",
                    [f.getId() for f in self.getFormFields(request=REQUEST)
                        if not f.getFieldMode() == 'DISPLAY']
                    )
            return self.ChildForm(temp_doc=tmp)

        ################################################################
        # Add a document to the database
        doc = db.createDocument()
        doc.setItem('Form', self.getFormName())

        # execute the onCreateDocument code of the form
        valid = ''
        try:
            valid = self.runFormulaScript(
                    'form_%s_oncreate' % self.id,
                    doc,
                    self.onCreateDocument)
        except PlominoScriptException, e:
            e.reportError('Document is created, but onCreate formula failed')

        if valid is None or valid == '':
            doc.saveDocument(REQUEST, creation=True)
        else:
            db.documents._delOb(doc.id)
            db.writeMessageOnPage(valid, REQUEST, False)
            REQUEST.RESPONSE.redirect(db.absolute_url())

    security.declarePublic('getFormFields')
    def getFormFields(self, includesubforms=False, doc=None,
            applyhidewhen=False, validation_mode=False, request=None,
            deduplicate=True):
        """ Get fields
        """
        db = self.getParentDatabase()
        cache_key = "getFormFields_%d_%d_%d_%d_%d_%d" % (
                hash(self),
                hash(doc),
                includesubforms,
                applyhidewhen,
                validation_mode,
                deduplicate
                )
        cache = db.getRequestCache(cache_key)
        if cache:
            return cache
        if not request and hasattr(self, 'REQUEST'):
            request = self.REQUEST
        form = self.getForm()
        fieldlist = form.objectValues(spec='PlominoField')
        result = [f for f in fieldlist]  # Convert from LazyMap to list
        if applyhidewhen:
            doc = doc or TemporaryDocument(
                    db, self, request,
                    validation_mode=validation_mode).__of__(db)
            layout = self.applyHideWhen(doc)
            result = [f for f in result
                    if """<span class="plominoFieldClass">%s</span>""" %
                    f.id in layout]
        result.sort(key=lambda elt: elt.id.lower())
        if includesubforms:
            subformsseen = []
            for subformname in self.getSubforms(
                    doc, applyhidewhen, validation_mode=validation_mode):
                if subformname in subformsseen:
                    continue
                subform = db.getForm(subformname)
                if subform:
                    result = result + subform.getFormFields(
                            includesubforms=True,
                            doc=doc,
                            applyhidewhen=applyhidewhen,
                            validation_mode=validation_mode,
                            request=request,
                            deduplicate=False)
                subformsseen.append(subformname)

        if deduplicate:
            # Deduplicate, preserving order
            seen = {}
            report = False
            deduped = []
            for f in result:
                fpath = '/'.join(f.getPhysicalPath())
                if fpath in seen:
                    seen[fpath] = seen[fpath] + 1
                    report = True
                    continue
                seen[fpath] = 1
                deduped.append(f)
            result = deduped

            if report:
                report = ', '.join(
                        ['%s (occurs %s times)' % (f, c)
                            for f,c in seen.items() if c > 1])
                logger.debug('Ambiguous fieldnames: %s' % report)

        db.setRequestCache(cache_key, result)
        return result

    security.declarePublic('getHidewhenFormulas')
    def getHidewhenFormulas(self):
        """Get hide-when formulae
        """
        hidewhens = self.objectValues(spec='PlominoHidewhen')
        return [h for h in hidewhens]

    security.declarePublic('getActions')
    def getActions(self, target, hide=True, parent_id=None):
        """Get actions
        """
        all = self.objectValues(spec='PlominoAction')

        filtered = []
        for obj_a in all:
            if hide and obj_a.Hidewhen:
                try:
                    result = self.runFormulaScript(
                            'action_%s_%s_hidewhen' % (self.id, obj_a.id),
                            target,
                            obj_a.Hidewhen,
                            True,
                            parent_id)
                except PlominoScriptException, e:
                    e.reportError(
                            '"%s" hide-when formula failed' % obj_a.Title())
                    #if error, we hide anyway
                    result = True
                if not result:
                    filtered.append((obj_a, parent_id))
            else:
                filtered.append((obj_a, parent_id))
        return filtered

    security.declarePublic('getCacheFormulas')
    def getCacheFormulas(self):
        """ Get cache formulas
        """
        cacheformulas = self.objectValues(spec='PlominoCache')
        return [c for c in cacheformulas]

    security.declarePublic('getFormName')
    def getFormName(self):
        """ Return the form name
        """
        return self.id

    def _handleLabels(self, html_content_orig, editmode):
        """ Parse the layout for label tags, 

        - add 'label' or 'fieldset/legend' markup to the corresponding fields.
        - if the referenced field does not exist, leave the layout markup as
          is (as for missing field markup).
        """
        html_content_processed = html_content_orig # We edit the copy
        match_iter = label_re.finditer(html_content_orig)
        for match_label in match_iter:
            d = match_label.groupdict()
            if d['optional_fieldname']:
                fn = d['optional_fieldname']
                field = self.getFormField(fn)
                if field:
                    label = d['fieldname_or_label']
                else:
                    continue
            else:
                fn = d['fieldname_or_label']
                field = self.getFormField(fn)
                if field:
                    label = field.Title()
                else:
                    continue

            field_re = re.compile('<span class="plominoFieldClass">%s</span>' % fn)
            match_field = field_re.search(html_content_processed)
            field_type = field.getFieldType()
            if field_type != 'DATETIME':
                widget_name = field.getSettings().widget

            # Handle input groups:
            if (field_type == 'DATETIME' or
                    field_type == 'SELECTION' and 
                    widget_name in ['CHECKBOX', 'RADIO', 'PICKLIST']):
                # Delete processed label
                html_content_processed = label_re.sub('', html_content_processed, count=1)
                # Is the field in the layout?
                if match_field:
                    # Markup the field
                    if editmode:
                        mandatory = (
                                field.getMandatory()
                                and " class='required'"
                                or '')
                        html_content_processed = field_re.sub(
                                "<fieldset><legend%s>%s</legend>%s</fieldset>" % (
                                mandatory, label, match_field.group()),
                                html_content_processed)
                    else:
                        html_content_processed = field_re.sub(
                                "<div class='fieldset'><span class='legend' title='Legend for %s'>%s</span>%s</div>" % (
                                fn, label, match_field.group()),
                                html_content_processed)

            # Handle single inputs:
            else:
                # Replace the processed label with final markup
                if editmode and (field_type not in ['COMPUTED', 'DISPLAY']):
                    mandatory = (
                            field.getMandatory()
                            and " class='required'"
                            or '')
                    html_content_processed = label_re.sub(
                            "<label for='%s'%s>%s</label>" % (fn, mandatory, label),
                            html_content_processed, count=1)
                else:
                    html_content_processed = label_re.sub(
                            "<span class='label' title='Label for %s'>%s</span>" % (fn, label),
                            html_content_processed, count=1)

        return html_content_processed


    security.declareProtected(READ_PERMISSION, 'displayDocument')
    @plomino_profiler('form')
    def displayDocument(self, doc, editmode=False, creation=False,
            parent_form_id=False, request=None):
        """ Display the document using the form's layout
        """
        # remove the hidden content
        html_content = self.applyHideWhen(doc, silent_error=False)
        if request:
            parent_form_ids = request.get('parent_form_ids', [])
            if parent_form_id:
                parent_form_ids.append(parent_form_id)
                request.set('parent_form_ids', parent_form_ids)

        # get the field lists
        fields = self.getFormFields(doc=doc, request=request)
        fields_in_layout = []
        fieldids_not_in_layout = []
        for field in fields:
            fieldblock = '<span class="plominoFieldClass">%s</span>' % field.id
            if fieldblock in html_content:
                fields_in_layout.append([field, fieldblock])
            else:
                fieldids_not_in_layout.append(field.id)

        # inject request parameters as input hidden for fields not part of the layout
        if creation and request is not None:
            for field_id in fieldids_not_in_layout:
                if request.has_key(field_id):
                    html_content = (
                            "<input type='hidden' "
                            "name='%s' "
                            "value='%s' />%s" % (
                                field_id,
                                asUnicode(request.get(field_id, '')),
                                html_content)
                            )

        # evaluate cache formulae and insert already cached fragment
        (html_content, to_be_cached) = self.applyCache(html_content, doc)

        #if editmode, we add a hidden field to handle the Form item value
        if editmode and not parent_form_id:
            html_content = ("<input type='hidden' "
                    "name='Form' "
                    "value='%s' />%s"% (
                        self.getFormName(),
                        html_content))

        # Handle legends and labels
        html_content = self._handleLabels(html_content, editmode)
        # html_content = self._handleLabels(legend_re, html_content)

        # insert the fields with proper value and rendering
        for (field, fieldblock) in fields_in_layout:
            # check if fieldblock still here after cache replace
            if fieldblock in html_content:
                html_content = html_content.replace(
                        fieldblock,
                        field.getFieldRender(
                            self,
                            doc,
                            editmode,
                            creation,
                            request=request)
                        )

        # insert subforms
        for subformname in self.getSubforms(doc):
            subform = self.getParentDatabase().getForm(subformname)
            if subform:
                subformrendering = subform.displayDocument(
                        doc, editmode, creation, parent_form_id=self.id,
                        request=request)
                html_content = html_content.replace(
                        '<span class="plominoSubformClass">%s</span>' %
                        subformname,
                        subformrendering)

        # insert the actions
        if doc is None:
            target = self
        else:
            target = doc
        form_id = parent_form_id and parent_form_id or self.id
        actionsToDisplay = [a.id for a, f_id in self.getActions(
            target, hide=True, parent_id=form_id)]
        for action, form_id in self.getActions(
                target,
                False,
                parent_id=form_id):
            action_id = action.id
            action_span = '<span class="plominoActionClass">%s</span>' % action_id
            if action_span in html_content:
                if action_id in actionsToDisplay:
                    actionDisplay = action.ActionDisplay
                    pt = self.getRenderingTemplate(actionDisplay + "Action")
                    if pt is None:
                        pt = self.getRenderingTemplate("LINKAction")
                    action_render = pt(plominoaction=action,
                                       plominotarget=target,
                                       plomino_parent_id=form_id)
                else:
                    action_render = ''
                html_content = html_content.replace(action_span, action_render)

        # translation
        db = self.getParentDatabase()
        i18n_domain = db.getI18n()
        if request and request.get("translation")=="off":
            i18n_domain = None
        if i18n_domain:
            html_content = translate(db, html_content, i18n_domain)

        # store fragment to cache
        html_content = self.updateCache(html_content, to_be_cached)
        return html_content

    security.declareProtected(READ_PERMISSION, 'childDocument')
    def childDocument(self, doc):
        """
        """
        db = self.getParentDatabase()
        parent_form = db.getForm(doc.Plomino_Parent_Form)
        parent_field = parent_form.getFormField(doc.Plomino_Parent_Field)
        field_ids = parent_field.getSettings().field_mapping.split(',')

        raw_values = []
        for f in field_ids:
            v = doc.getItem(f)
            if hasattr(v, 'strftime'):
                raw_values.append(
                        DateToString(
                            doc.getItem(f),
                            db.getDateTimeFormat()))
            else:
                raw_values.append(v)

        html = ("<div id='raw_values'>%(raw_values)s</div>"
                "<div id='parent_field'>%(parent_field)s</div>"
                "%(fields)s")
        field_html = "<span id='%s' class='plominochildfield'>%s</span>"

        field_items = []
        for i in field_ids:
            field_items.append(
                    field_html % (
                        i,
                        doc.getRenderedItem(i, form=self)
                        ))

        return html % {
                'raw_values': json.dumps(raw_values),
                'parent_field': doc.Plomino_Parent_Field,
                'fields': ''.join(field_items)
                }

    security.declarePrivate('_get_html_content')
    def _get_html_content(self):
        plone_tools = getToolByName(self, 'plone_utils')
        encoding = plone_tools.getSiteEncoding()
        layout = self.getField('FormLayout')
        html_content = layout.getRaw(self).decode(encoding)
        return html_content.replace('\n', '')

    security.declareProtected(READ_PERMISSION, 'applyHideWhen')
    def applyHideWhen(self, doc=None, silent_error=True):
        """ Evaluate hide-when formula and return resulting layout
        """
        html_content = self._get_html_content()

        # remove the hidden content
        for hidewhen in self.getHidewhenFormulas():
            hidewhenName = hidewhen.id
            try:
                if doc is None:
                    target = self
                else:
                    target = doc
                result = self.runFormulaScript(
                    'hidewhen_%s_%s_formula' % (self.id, hidewhen.id),
                    target,
                    hidewhen.Formula)
            except PlominoScriptException, e:
                if not silent_error:
                    # applyHideWhen is called by getFormFields and
                    # getSubForms; in those cases, error reporting
                    # is not accurate,
                    # we only need error reporting when actually rendering a
                    # page
                    e.reportError(
                        '%s hide-when formula failed' % hidewhen.id,
                        request=getattr(self, 'REQUEST', None))
                #if error, we hide anyway
                result = True

            start = ('<span class="plominoHidewhenClass">start:%s</span>' %
                    hidewhenName)
            end = ('<span class="plominoHidewhenClass">end:%s</span>' %
                    hidewhenName)

            if getattr(hidewhen, 'isDynamicHidewhen', False):
                if result:
                    style = ' style="display: none"'
                else:
                    style = ''
                html_content = re.sub(
                        start,
                        '<div class="hidewhen-%s"%s>' % (
                            hidewhenName,
                            style),
                        html_content,
                        re.MULTILINE + re.DOTALL)
                html_content = re.sub(
                        end,
                        '</div>',
                        html_content,
                        re.MULTILINE + re.DOTALL)
            else:
                if result:
                    regexp = start + '.*?' + end
                    html_content = re.sub(
                            regexp,
                            '',
                            html_content,
                            re.MULTILINE + re.DOTALL
                            )
                else:
                    html_content = html_content.replace(start, '')
                    html_content = html_content.replace(end, '')

        return html_content

    security.declareProtected(READ_PERMISSION, 'hasDynamicHidewhen')
    def hasDynamicHidewhen(self):
        """ Search if a dynamic hidewhen is stored in the form
        """
        for hidewhen in self.getHidewhenFormulas():
            if getattr(hidewhen, 'isDynamicHidewhen', False):
                return True
        for subformname in self.getSubforms():
            form = self.getParentDatabase().getForm(subformname)
            if form:
                if form.hasDynamicHidewhen():
                    return True
            else:
                msg = 'Missing subform: %s. Referenced on: %s' % (subformname, self.id)
                self.writeMessageOnPage(msg, self.REQUEST)
                logger.info(msg)

        return False

    security.declareProtected(READ_PERMISSION, 'getHidewhenAsJSON')
    def getHidewhenAsJSON(self, REQUEST, parent_form=None, validation_mode=False):
        """ Return a JSON object to dynamically show or hide hidewhens
        (works only with isDynamicHidewhen)
        """
        db = self.getParentDatabase()
        result = {}
        target = TemporaryDocument(
                db,
                parent_form or self,
                REQUEST,
                validation_mode=validation_mode).__of__(db)
        for hidewhen in self.getHidewhenFormulas():
            if getattr(hidewhen, 'isDynamicHidewhen', False):
                try:
                    isHidden = self.runFormulaScript(
                            'hidewhen_%s_%s_formula' % (
                                self.id,
                                hidewhen.id),
                            target,
                            hidewhen.Formula)
                except PlominoScriptException, e:
                    e.reportError(
                            '%s hide-when formula failed' % hidewhen.id)
                    #if error, we hide anyway
                    isHidden = True
                result[hidewhen.id] = isHidden
        for subformname in self.getSubforms():
            form = db.getForm(subformname)
            if not form:
                msg = 'Missing subform: %s. Referenced on: %s' % (subformname, self.id)
                self.writeMessageOnPage(msg, self.REQUEST)
                logger.info(msg)
                continue
            form_hidewhens = json.loads(
                    form.getHidewhenAsJSON(REQUEST,
                        parent_form=parent_form or self,
                        validation_mode=validation_mode))
            result.update(form_hidewhens)

        return json.dumps(result)

    security.declareProtected(READ_PERMISSION, 'applyCache')
    def applyCache(self, html_content, doc=None):
        """ Evaluate cache formula and return resulting layout
        """
        to_be_cached = {}

        for cacheformula in self.getCacheFormulas():
            cacheid = cacheformula.id
            try:
                if doc is None:
                    target = self
                else:
                    target = doc
                cachekey = self.runFormulaScript(
                        "cache_"+self.id+"_"+cacheid+"_formula",
                        target,
                        cacheformula.Formula)
            except PlominoScriptException, e:
                e.reportError(
                        '%s cache formula failed' % cacheid,
                        request=getattr(self, 'REQUEST', None))
                cachekey = None

            start = ('<span class="plominoCacheClass">start:%s</span>' %
                    cacheid)
            end = ('<span class="plominoCacheClass">end:%s</span>' %
                    cacheid)

            if cachekey:
                cachekey = 'fragment_'+cachekey
                fragment = self.getParentDatabase().getCache(cachekey)
                if fragment:
                    # the fragment was in cache, we insert it
                    regexp = start+'.*?'+end
                    html_content = re.sub(
                            regexp,
                            fragment,
                            html_content,
                            re.MULTILINE + re.DOTALL)
                else:
                    # the fragment is not cached yet, we let the marker
                    # they will be used after rendering to extract the
                    # fragment and store it in cache
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
            start = ('<span class="plominoCacheClass">start:%s</span>' %
                    cacheid)
            end = ('<span class="plominoCacheClass">end:%s</span>' %
                    cacheid)
            regexp = start+'(.*?)'+end
            search_fragment = re.findall(
                    regexp,
                    html_content,
                    re.MULTILINE + re.DOTALL)
            if search_fragment:
                fragment = search_fragment[0]
                db.setCache(to_be_cached[cacheid], fragment)
            html_content = html_content.replace(start, '')
            html_content = html_content.replace(end, '')
        return html_content

    security.declarePublic('formLayout')
    def formLayout(self, request=None):
        """ Return the form layout in edit mode (used to compose a new
        document).
        """
        return self.displayDocument(None,
                editmode=True,
                creation=True,
                request=request)

    security.declarePublic('openBlankForm')
    def openBlankForm(self, request=None):
        """ Check beforeCreateDocument, then open the form
        """
        db = self.getParentDatabase()
        # execute the beforeCreateDocument code of the form
        invalid = False
        if (hasattr(self, 'beforeCreateDocument') and
                self.beforeCreateDocument):
            try:
                invalid = self.runFormulaScript(
                        'form_%s_beforecreate' % self.id,
                        self,
                        self.beforeCreateDocument)
            except PlominoScriptException, e:
                e.reportError('beforeCreate formula failed')

        tmp = None
        if not self.isPage and hasattr(self, 'REQUEST'):
            # hideWhens need a TemporaryDocument
            tmp = TemporaryDocument(
                    db,
                    self,
                    self.REQUEST).__of__(db)
        if (not invalid) or self.hasDesignPermission(self):
            return self.displayDocument(
                    tmp,
                    editmode=True,
                    creation=True,
                    request=request)
        else:
            self.REQUEST.RESPONSE.redirect(
                    db.absolute_url() +
                    "/ErrorMessages?disable_border=1&error=" +
                    invalid)

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        """ Clean up the layout before saving
        """
        self.cleanFormulaScripts("form_" + self.id)

    security.declarePublic('getFormField')
    def getFormField(self, fieldname, includesubforms=True):
        """ Return the field
        """
        field = None
        form = self.getForm()
        field_ids = form.objectIds(spec='PlominoField')
        if fieldname in field_ids:
            field = getattr(form, fieldname)
        else:
            # if field is not in main form, we search in the subforms
            all_fields = self.getFormFields(includesubforms=includesubforms)
            matching_fields = [f for f in all_fields if f.id == fieldname]
            if matching_fields:
                field = matching_fields[0]
        return field

    security.declarePublic('computeFieldValue')
    def computeFieldValue(self, fieldname, target, report=True):
        """ Evaluate field formula over target.
        """
        field = self.getFormField(fieldname)
        fieldvalue = None
        if field:
            db = self.getParentDatabase()
            try:
                fieldvalue = db.runFormulaScript(
                        'field_%s_%s_formula' % (self.id, fieldname),
                        target,
                        field.Formula,
                        True,
                        self)
            except PlominoScriptException, e:
                logger.warning(
                        '%s field formula failed' % fieldname,
                        exc_info=True)
                if report:
                    e.reportError('%s field formula failed' % fieldname)

        return fieldvalue

    security.declarePublic('hasDateTimeField')
    def hasDateTimeField(self):
        """ Return True if the form contains at least one DateTime field
        or a datagrid (as a datagrid may contain a date).
        """
        return self._has_fieldtypes(["DATETIME", "DATAGRID"])

    security.declarePrivate('_has_fieldtypes')
    def _has_fieldtypes(self, types):
        """ ``types`` is a list of strings.
        Check if any of those types are present.
        """
        tmp = None
        db = self.getParentDatabase()
        if hasattr(self, 'REQUEST'):
            # hideWhens need a TemporaryDocument
            tmp = TemporaryDocument(
                    db,
                    self,
                    self.REQUEST).__of__(db)
        fields = self.getFormFields(
                includesubforms=True,
                doc=tmp,
                applyhidewhen=True)
        for f in fields:
            if f.getFieldType() in types:
                return True
        return False

    security.declarePublic('hasGoogleVisualizationField')
    def hasGoogleVisualizationField(self):
        """ Return true if the form contains at least one GoogleVisualization field
        """
        return self._has_fieldtypes(["GOOGLEVISUALIZATION"])

    security.declarePublic('getSubforms')
    def getSubforms(self, doc=None, applyhidewhen=True, validation_mode=False):
        """ Return the names of the subforms embedded in the form.
        """
        if applyhidewhen:
            if doc is None and hasattr(self, 'REQUEST'):
                try:
                    db = self.getParentDatabase()
                    doc = TemporaryDocument(
                            db,
                            self,
                            self.REQUEST,
                            validation_mode=validation_mode).__of__(db)
                except:
                    # TemporaryDocument might fail if field validation is
                    # wrong and as we need getFormFields during field
                    # validation, we need to continue so the error is nicely
                    # returned to the user
                    doc = None
            html_content = self.applyHideWhen(doc)
        else:
            html_content = self._get_html_content()

        r = re.compile('<span class="plominoSubformClass">([^<]+)</span>')
        return [i.strip() for i in r.findall(html_content)]

    security.declarePublic('readInputs')
    def readInputs(self, doc, REQUEST, process_attachments=False, applyhidewhen=True, validation_mode=False):
        """ Read submitted values in REQUEST and store them in document
        according to fields definition.
        """
        all_fields = self.getFormFields(
                includesubforms=True,
                doc=doc,
                request=REQUEST)
        if applyhidewhen:
            displayed_fields = self.getFormFields(
                    includesubforms=True,
                    doc=doc,
                    applyhidewhen=True,
                    request=REQUEST)

        for f in all_fields:
            mode = f.getFieldMode()
            fieldName = f.id
            if mode == "EDITABLE":
                submittedValue = REQUEST.get(fieldName)
                if submittedValue is not None:
                    if submittedValue=='':
                        doc.removeItem(fieldName)
                    else:
                        v = f.processInput(
                                submittedValue,
                                doc,
                                process_attachments,
                                validation_mode=validation_mode)
                        if f.getFieldType() == 'SELECTION':
                            if f.getSettings().widget in [
                                    'MULTISELECT', 'CHECKBOX', 'PICKLIST']:
                                v = asList(v)
                        doc.setItem(fieldName, v)
                else:
                    # The field was not submitted, probably because it is
                    # not part of the form (hide-when, ...) so we just leave
                    # it unchanged. But with SELECTION, DOCLINK or BOOLEAN, we need
                    # to presume it was empty (as SELECT/checkbox/radio tags
                    # do not submit an empty value, they are just missing
                    # in the querystring)
                    if applyhidewhen and f in displayed_fields:
                        fieldtype = f.getFieldType()
                        if (fieldtype in ("SELECTION", "DOCLINK", "BOOLEAN")):
                            doc.removeItem(fieldName)

    security.declareProtected(READ_PERMISSION, 'searchDocuments')
    def searchDocuments(self, REQUEST):
        """ Search documents in the view matching the submitted form fields values.

        1. If there is an onSearch event, use the onSearch formula to generate a result set.
        2. Otherwise, do a dbsearch among the documents of the related view, and
        2.1. if there is a searchformula, evaluate that for every document in the view.
        """
        if self.onSearch:
            # Manually generate a result set
            try:
                results = self.runFormulaScript(
                        'from_%s_onsearch' % self.id,
                        self,
                        self.onSearch)
            except PlominoScriptException, e:
                if self.REQUEST:
                    e.reportError('Search event failed.')
                    return self.OpenForm(searchresults=[])
        else:
            # Allow Plomino to filter by view, default query, and formula
            db = self.getParentDatabase()
            searchview = db.getView(self.getSearchView())

            #index search
            index = db.getIndex()
            query = {'PlominoViewFormula_'+searchview.getViewName(): True}

            for f in self.getFormFields(
                    includesubforms=True,
                    request=REQUEST):
                fieldname = f.id
                #if fieldname is not an index -> search doesn't matter and returns all
                submittedValue = REQUEST.get(fieldname)
                if submittedValue:
                    submittedValue = asUnicode(submittedValue)
                    # if non-text field, convert the value
                    if f.getFieldType() == "NUMBER":
                        settings = f.getSettings()
                        if settings.type == "INTEGER":
                            v = long(submittedValue)
                        elif settings.type == "FLOAT":
                            v = float(submittedValue)
                        elif settings.type == "DECIMAL":
                            v = decimal(submittedValue)
                    elif f.getFieldType() == "DATETIME":
                        # The format submitted by the datetime widget:
                        v = StringToDate(submittedValue, format='%Y-%m-%d %H:%M ')
                    else:
                        v = submittedValue
                    # rename Plomino_SearchableText to perform full-text
                    # searches on regular SearchableText index
                    if fieldname == "Plomino_SearchableText":
                        fieldname = "SearchableText"
                    query[fieldname] = v

            sortindex = searchview.getSortColumn()
            if not sortindex:
                sortindex = None
            results = index.dbsearch(
                    query,
                    sortindex=sortindex,
                    reverse=searchview.getReverseSorting())

            #filter search with searchformula
            searchformula = self.getSearchFormula()
            if searchformula:
                filteredResults = []
                try:
                    for doc in results:
                        valid = self.runFormulaScript(
                                'form_%s_searchformula' % self.id,
                                doc.getObject(),
                                self.SearchFormula)
                        if valid:
                            filteredResults.append(doc)
                except PlominoScriptException, e:
                    e.reportError('Search formula failed')
                results = filteredResults

        return self.OpenForm(searchresults=results)


    security.declarePublic('validation_errors')
    def validation_errors(self, REQUEST):
        """ Check submitted values
        """
        errors = self.validateInputs(REQUEST)
        if errors:
            return self.errors_json(
                    errors=json.dumps({'success': False, 'errors': errors}))
        else:
            return self.errors_json(
                    errors=json.dumps({'success': True}))


    security.declarePrivate('_get_js_hidden_fields')
    def _get_js_hidden_fields(self, REQUEST, doc, validation_mode=False):
        hidden_fields = []
        hidewhens = json.loads(
                self.getHidewhenAsJSON(REQUEST,
                    validation_mode=validation_mode))
        html_content = self._get_html_content()
        for hidewhenName, doit in hidewhens.items():
            if not doit:  # Only consider True hidewhens
                continue
            start = ('<span class="plominoHidewhenClass">start:%s</span>' %
                    hidewhenName)
            end = ('<span class="plominoHidewhenClass">end:%s</span>' %
                    hidewhenName)
            for hiddensection in re.findall(
                    start + '(.*?)' + end,
                    html_content):
                hidden_fields += re.findall(
                    '<span class="plominoFieldClass">([^<]+)</span>',
                    hiddensection)
        for subformname in self.getSubforms(doc):
            subform = self.getParentDatabase().getForm(subformname)
            if not subform:
                msg = 'Missing subform: %s. Referenced on: %s' % (subformname, self.id)
                self.writeMessageOnPage(msg, self.REQUEST)
                logger.info(msg)
                continue
            hidden_fields += subform._get_js_hidden_fields(REQUEST, doc)
        return hidden_fields

    security.declarePublic('validateInputs')
    def validateInputs(self, REQUEST, doc=None):
        """
        """
        errors=[]
        fields = self.getFormFields(
                includesubforms=True,
                doc=doc,
                applyhidewhen=True,
                validation_mode=True,
                request=REQUEST)
        hidden_fields = self._get_js_hidden_fields(
                REQUEST,
                doc,
                validation_mode=True)
        fields = [field for field in fields
                if field.getId() not in hidden_fields]
        for f in fields:
            fieldname = f.id
            fieldtype = f.getFieldType()
            submittedValue = REQUEST.get(fieldname)

            # STEP 1: check mandatory fields
            if not submittedValue:
                if f.getMandatory() is True:
                    if fieldtype == "ATTACHMENT" and doc:
                        existing_files = doc.getItem(fieldname)
                        if not existing_files:
                            errors.append("%s %s" % (
                                f.Title(),
                                PlominoTranslate("is mandatory", self)))
                    else:
                        errors.append("%s %s" % (
                            f.Title(),
                            PlominoTranslate("is mandatory", self)))
            else:
                # STEP 2: check data types
                errors = errors + f.validateFormat(submittedValue)

        if not errors:
            # STEP 3: check validation formula
            db = self.getParentDatabase()
            tmp = TemporaryDocument(
                    db,
                    self,
                    REQUEST,
                    doc,
                    validation_mode=True).__of__(db)
            for f in fields:
                formula = f.getValidationFormula()
                if not formula=='':
                    s = ''
                    try:
                        s = self.runFormulaScript(
                                'field_%s_%s_ValidationFormula' % (
                                    self.id,
                                    f.id),
                                tmp,
                                f.ValidationFormula)
                    except PlominoScriptException, e:
                        e.reportError('%s validation formula failed' % f.id)
                    if s:
                        errors.append(s)

        return errors

    security.declarePublic('notifyErrors')
    def notifyErrors(self, errors):
        return self.ErrorMessages(errors=errors)

    security.declareProtected(DESIGN_PERMISSION, 'manage_generateView')
    def manage_generateView(self, REQUEST=None):
        """ Create a view automatically
        where selection is: plominoDocument.Form == "this_form"
        and displaying a column for all the acceptable fields
        (i.e. editable and not richtext, file attachment, datagrid, ...
        which might need reformatting)
        """
        db = self.getParentDatabase()
        view_id = "all" + self.id.replace('_', '').replace('-', '')
        if view_id in db.objectIds():
            if REQUEST:
                plone_tools = getToolByName(self, 'plone_utils')
                plone_tools.addPortalMessage(
                        '%s is already an existing object.' % view_id,
                        'error',
                        REQUEST)
                REQUEST.RESPONSE.redirect(self.absolute_url_path())
            return
        view_title = "All " + self.Title()
        formula = 'plominoDocument.getItem("Form")=="%s"' % self.id
        db.invokeFactory(
                'PlominoView',
                id=view_id,
                title=view_title,
                SelectionFormula=formula)
        view_obj = getattr(db, view_id)
        view_obj.at_post_create_script()

        fields = self.getFormFields(includesubforms=True)
        acceptable_types = ["TEXT", "NUMBER", "NAME", "SELECTION",
                "DATETIME"]
        fields = [f for f in fields
                if f.getFieldMode()=="EDITABLE" and
                f.FieldType in acceptable_types]
        for f in fields:
            col_id = f.id.replace('_', '').replace('-', '')
            col_title = col_id
            col_definition = self.id + '/' + f.id
            view_obj.invokeFactory(
                    'PlominoColumn',
                    id=col_id,
                    title=col_title,
                    SelectedField=col_definition)
            getattr(view_obj, col_id).at_post_create_script()
        view_obj.invokeFactory(
                'PlominoAction',
                id='add_new',
                title="Add a new "+self.Title(),
                ActionType="OPENFORM",
                ActionDisplay="BUTTON",
                Content=self.id)

        if REQUEST:
            REQUEST.RESPONSE.redirect(view_obj.absolute_url_path())

    security.declarePublic('getPosition')
    def getPosition(self):
        """ Return the form position in the database
        """
        try:
            return self.Position
        except Exception:
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
        """ When rendering a form without a document, it's always in edit mode.
        """
        return True

    security.declarePublic('tojson')
    def tojson(self, REQUEST=None, item=None):
        """ Return field value as JSON.
        If item=None, return all field values.
        (Note: we use 'item' instead of 'field' to match the
        PlominoDocument.tojson method signature)
        """
        datatables_format = False
        if REQUEST:
            REQUEST.RESPONSE.setHeader(
                    'content-type',
                    'application/json; charset=utf-8')
            item = REQUEST.get('item', item)
            datatables_format_str = REQUEST.get('datatables', None)
            if datatables_format_str:
                datatables_format = True

        result = None
        if not item:
            fields = self.getFormFields(request=REQUEST)
            result = {}
            for field in fields:
                adapt = field.getSettings()
                fieldvalue = adapt.getFieldValue(self, request=REQUEST)
                result[field.id] = fieldvalue
        else:
            field = self.getFormField(item)
            if field:
                adapt = field.getSettings()
                result = adapt.getFieldValue(self, request=REQUEST)

        if datatables_format:
            result = {
                    'iTotalRecords': len(result),
                    'iTotalDisplayRecords': len(result),
                    'aaData': result}

        return json.dumps(result)

    def _getDatabaseViews(self):
        db = self.getParentDatabase()
        views = db.getViews()
        return [''] + [v.id for v in views]

registerType(PlominoForm, PROJECTNAME)

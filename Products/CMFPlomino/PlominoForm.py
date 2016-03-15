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
from PlominoDocument import getTemporaryDocument
from Products.CMFCore.utils import getToolByName
from Products.CMFPlomino.config import *
from Products.CMFPlomino.browser import PlominoMessageFactory as _
from Products.CMFPlomino import plomino_profiler
from Products.CMFPlomino.PlominoUtils import asList
from Products.CMFPlomino.PlominoUtils import asUnicode
from Products.CMFPlomino.PlominoUtils import DateToString
from Products.CMFPlomino.PlominoUtils import StringToDate
from Products.CMFPlomino.PlominoUtils import PlominoTranslate
from Products.CMFPlomino.PlominoUtils import translate
import interfaces
from pyquery import PyQuery as pq

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
    TextField(
        name='ResourcesJS',
        widget=TextAreaWidget(
            label="JavaScripts",
            description="JavaScript resources loaded by this form. "
                "Enter one path per line.",
            label_msgid='CMFPlomino_label_FormResourcesJS',
            description_msgid='CMFPlomino_help_FormResourcesJS',
            i18n_domain='CMFPlomino',
        ),
    ),
    TextField(
        name='ResourcesCSS',
        widget=TextAreaWidget(
            label="CSS",
            description="CSS resources loaded by this form. "
                "Enter one path per line.",
            label_msgid='CMFPlomino_label_FormResourcesCSS',
            description_msgid='CMFPlomino_help_FormResourcesCSS',
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
            return self.getParentDatabase().getForm(formname)

        form = self
        while getattr(form, 'meta_type', '') != 'PlominoForm':
            form = form.aq_parent
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

    def _get_resource_urls(self, field_name):
        """ Return canonicalized URLs if local.

        Pass through fully specified URLs and un-found URLs (they may be
        statically served outside of Zope).
        """
        value = self.Schema()[field_name].get(self).splitlines()
        for url in value:
            url = url.strip()
            if url:
                if not url.lower().startswith(('http', '/')):
                    if url.startswith('./'):
                        # unrestrictedTraverse knows '../' but not './'
                        resource = self.unrestrictedTraverse(url[2:], None)
                    else:
                        resource = self.unrestrictedTraverse(url, None)
                    if resource:
                        url = resource.absolute_url()
                    else:
                        logger.info('Missing resource: %s' % url)
                        continue
                yield url

    def get_resources_css(self):
        return self._get_resource_urls('ResourcesCSS')

    def get_resources_js(self):
        return self._get_resource_urls('ResourcesJS')

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
                msgs = [x['error'] for x in errors]
                return ("""<html><body><span id="plomino_child_errors">"""
                        """%s</span></body></html>""" % " - ".join(msgs))
            return self.notifyErrors(errors)

        ################################################################
        # If child form, return a TemporaryDocument
        if is_childform:
            tmp = getTemporaryDocument(db, self, REQUEST).__of__(db)
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
                    SCRIPT_ID_DELIMITER.join(['form', self.id, 'oncreate']),
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
            #DBG logger.info('Cache hit: %s' % `cache`)
            return cache
        if not request and hasattr(self, 'REQUEST'):
            request = self.REQUEST
        form = self.getForm()
        fieldlist = form.objectValues(spec='PlominoField')
        result = [f for f in fieldlist]  # Convert from LazyMap to list
        if applyhidewhen:
            doc = doc or getTemporaryDocument(
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
                            for f, c in seen.items() if c > 1])
                logger.debug('Overridden fields: %s' % report)

        db.setRequestCache(cache_key, result)
        return result

    security.declarePublic('getHidewhenFormulas')
    def getHidewhenFormulas(self):
        """Get hide-when formulae
        """
        hidewhens = self.objectValues(spec='PlominoHidewhen')
        return [h for h in hidewhens]

    security.declarePublic('getActions')
    def getActions(self, target, hide=True):
        """ Get filtered form actions for the target (page or document).
        """
        actions = self.objectValues(spec='PlominoAction')

        filtered = []
        for action in actions:
            if hide:
                if not action.isHidden(target, self):
                    filtered.append((action, self.id))
            else:
                filtered.append((action, self.id))
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
        # from lxml import etree

        # dom = etree.HTML(html_content_processed)
        # d = pq(html_content_processed, parser='html_fragments')
        d = pq(html_content_processed)

        # interate over all the labels
        # if there is stuff inbetween its field then grab it too
        # create fieldset around teh field and put in the label and inbetween stuff
        # we will build up a map of field_id -> (field, nodes_to_group)
        # so we can check we group all labels for a given field
        field2group = {}

        for label_node in d("span.plominoLabelClass"):

            # work out the fieldid the label is for, and its text
            # we could have hide whens or other nodes in our label. filter them out
            #TODO: we really want to remove "fieldid:" and leave rest unchanged
            #label_text = pq(label_node).clone().children().remove().end().text()
            #label_text = pq(label_node).children().html()
            #label_re =  re.compile('<span class="plominoLabelClass">((?P<optional_fieldname>\S+):){0,1}\s*(?P<fieldname_or_label>.+?)</span>')
            # see if we have a label with fieldid buried in it somewhere.
            # we want to keep any html inside it intact.
            field = None
            for child in [label_node] + pq(label_node).find("*"):
                for text_attribute in ['text', 'tail']:
                    label_text = getattr(child, text_attribute)
                    if label_text and ':' in label_text:
                        field_id, label_text = label_text.split(':',1)
                        field_id = field_id.strip()
                        field = self.getFormField(field_id)
                        if field is not None:
                            # do we replace if we don't know if the field exists in teh layout? yes for ow
                            setattr(child, text_attribute, label_text)
                            break
                if field is not None:
                    break
            if field is None:
                # we aren't using custom label text. In that case we can blow any internal html away
                field_id = pq(label_node).clone().children().remove().end().text()
                field_id = field_id.strip()
                if not field_id:
                    # label is empty? #TODO: get rid of label?
                    continue
                field = self.getFormField(field_id)
                if field is not None:
                    pq(label_node).text(asUnicode(field.Title()))
                else:
                    #TODO? should we produce a label anyway?
                    # We could also look and see if the next field doesn't have a label and use that.
                    continue

            if field_id in field2group:
                # we have more than one label. We will try to form a group around both the other labels
                # and the field.
                (field, togroup, labels) = field2group[field_id]
                labels = labels + [label_node]
            else:
                labels = [label_node]


            #field_node.first(":parent")
            # do a breadth first search but starting at the label and going up
            togroup = []
            for parent in [label_node] + [n for n in reversed(pq(label_node).parents())]:
                #parent.next("span.plominoFieldClass")
                togroup = []
                to_find = set(labels+[field])
                # go through siblings until to find first and last target
                for sibling in pq(parent).parent().children():
                    found_in_sibling = False
                    field_node = pq(sibling)("span.plominoFieldClass").eq(0)
                    if field_node and field_node.text().strip() == field_id:
                        # found our field
                        found_in_sibling = True
                        to_find.remove(field)
                    elif field_node and togroup:
                        # found a field in our group thats not ours
                        # disolve grouping
                        togroup = found = []
                        break

                    for label in set(to_find):
                        if sibling in pq(label).parents() or label == sibling:
                            to_find.remove(label)
                            found_in_sibling = True
                    if found_in_sibling or togroup:
                        togroup.append(sibling)
                    if not to_find:
                        # we found everything already
                        break

                if not to_find:
                    # we found everything already
                    break

            if togroup:
                field2group[field_id] = (field, togroup, labels)

        for field_id, (field, togroup, labels) in field2group.items():


            field_type = field.getFieldType()
            if hasattr(field.getSettings(), 'widget'):
                widget_name = field.getSettings().widget

            compound_widget = (field_type == 'DATETIME' or
                    field_type == 'SELECTION' and
                    widget_name in ['CHECKBOX', 'RADIO', 'PICKLIST'])

            # groupit: take label, inbetween, field and wrap it in a container
            # if its a compound widget like datetime or selection then use a fieldset and legend
            # if a simple widget then just a div
            if editmode:
                legend = "<label for='%s'></span>" % field_id
            else:
                legend = "<span class='legend'></span>"
            grouping = ""
            #TODO: is testing the first element enough?
            if togroup and pq(togroup).eq(0).is_("span"):
                # we want to wrap in a div
                grouping = '<span class="plominoFieldGroup"></span>'
            elif togroup and pq(togroup).eq(0).is_("div,p"):
                if compound_widget and editmode:
                    grouping = "<fieldset></fieldset>"
                    legend = "<legend></legend>"
                else:
                    grouping = '<div class="plominoFieldGroup"></div>'
            else:
                # we don't want to group a table row or list elements
                togroup = []
            #wrapped = pq(togroup).wrap_all(grouping)

            # my own wrap method
            if grouping:
                #import pdb; pdb.set_trace()
                try:
                    ng = pq(grouping).insert_before(pq(togroup).eq(0))
                    pq(ng).append(pq(togroup))
                except:
                    raise
                if field.getMandatory():
                    pq(ng).add_class("required")

            for label_node in labels:

                #switch the label last so insert_before works properly
                #legend_node = pq(legend).append(pq(label_node).children())
                #pq(label_node).replace_with(pq(legend))
                pq(legend).html(pq(label_node).html()).insert_before(pq(label_node))
                pq(label_node).remove()

        return d.html()


    security.declareProtected(READ_PERMISSION, 'displayDocument')
    @plomino_profiler('form')
    def displayDocument(self, doc, editmode=False, creation=False,
            parent_form_id=False, request=None):
        """ Display the document using the form's layout
        """
        # Create a temp doc to work with
        if doc is None:
            db = self.getParentDatabase()
            temp_doc = getTemporaryDocument(
                db,
                self,
                self.REQUEST
            )
        else:
            # If there is already a doc, use this
            temp_doc = doc

        # remove the hidden content
        html_content = self.applyHideWhen(temp_doc, silent_error=False)
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
                            temp_doc,
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

        #
        # insert the actions
        #
        if doc is None:
            target = self
        else:
            target = doc

        if parent_form_id:
            form = self.getForm(parent_form_id)
        else:
            form = self

        for action, form_id in self.getActions(target, hide=False):

            action_id = action.id
            action_span = '<span class="plominoActionClass">%s</span>' % action_id
            if action_span in html_content:
                if not action.isHidden(target, form):
                    template = action.ActionDisplay
                    pt = self.getRenderingTemplate(template + "Action")
                    if pt is None:
                        pt = self.getRenderingTemplate("LINKAction")
                    action_render = pt(plominoaction=action,
                                       plominotarget=target,
                                       plomino_parent_id=form.id)
                else:
                    action_render = ''
                html_content = html_content.replace(action_span, action_render)

        # translation
        html_content = translate(self, html_content)

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
            # Watch out, this is lossy. Don't use DB date format here,
            # use a non-lossy representation.
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
        field_html = (
                "<span id='%(field_id)s' "
                "class='plominochildfield'>%(rendered_item)s</span>")

        field_items = []
        for i in field_ids:
            field_items.append(
                    field_html % {
                        'field_id': i,
                        'rendered_item': doc.getRenderedItem(i, form=self)
                        })

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
                    SCRIPT_ID_DELIMITER.join(['hidewhen', self.id, hidewhen.id, 'formula']),
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

    security.declareProtected(READ_PERMISSION, 'hasDynamicContent')
    def hasDynamicContent(self):
        """Check for dynamic content on the form"""
        if self.hasDynamicHidewhen():
            return True
        if self.hasDynamicFields():
            return True
        return False

    security.declareProtected(READ_PERMISSION, 'hasDynamicFields')
    def hasDynamicFields(self):
        """ Search for computed display fields """
        fields = self.getFormFields()
        for field in fields:
            if getattr(field, 'isDynamicField', False):
                return True
        return False

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

    security.declareProtected(READ_PERMISSION, 'getDynamicContentAsJSON')
    def getDynamicContentAsJSON(self, REQUEST, parent_form=None, doc=None, validation_mode=False):
        result = {
            'hidewhen': {},
            'dynamicfields': {},
        }
        if self.hasDynamicHidewhen():
            result['hidewhen'] = self.getHidewhen(
                REQUEST,
                parent_form=parent_form,
                doc=doc,
                validation_mode=validation_mode,
            )
        if self.hasDynamicFields():
            result['dynamicfields'] = self.getDynamicFields(
                REQUEST,
                parent_form=parent_form,
                doc=doc,
            )
        return json.dumps(result)

    security.declareProtected(READ_PERMISSION,'getDynamicFields')
    def getDynamicFields(self,REQUEST,parent_form=None,doc=None):
        """
        Return a python object to dynamically update dynamic fields
        Currently this only works for dynamic, computed fields
        """
        if parent_form is None:
            parent_form = self
        if doc is None:
            db = self.getParentDatabase()
            doc = getTemporaryDocument(
                db,
                parent_form,
                REQUEST,
                doc
            )
        result = {}
        fields = self.getFormFields()
        dynamic = [f for f in fields if getattr(f, 'isDynamicField', False)]
        for field in dynamic:
            # For now, only handle dynamic computed fields
            value = self.computeFieldValue(field.id, doc)
            result[field.id] = value
        return result

    security.declareProtected(READ_PERMISSION,'getHidewhen')
    def getHidewhen(self,REQUEST,parent_form=None, doc=None,validation_mode=False):
        """ Return a python object to dynamically show or hide hidewhens
        (works only with isDynamicHidewhen)
        """

        if parent_form is None:
            parent_form = self

        db = parent_form.getParentDatabase()
        result = {}
        target = getTemporaryDocument(
                db,
                parent_form,
                REQUEST,
                doc,
                validation_mode=validation_mode)

        hidewhens =  parent_form.getHidewhenFormulas()
        for subformname in self.getSubforms(doc=target):
            form = db.getForm(subformname)
            if not form:
                msg = 'Missing subform: %s. Referenced on: %s' % (subformname, parent_form.id)
                parent_form.writeMessageOnPage(msg, REQUEST)
                logger.info(msg)
                continue
            hidewhens += form.getHidewhenFormulas()


        for hidewhen in hidewhens:
            if hidewhen.id in result:
                # Previously hidewhens were run in the context of their own subform. Now we
                # run then all against the parent_form so there is no need to run it more than once
                continue
            if getattr(hidewhen, 'isDynamicHidewhen', False):
                try:
                    isHidden = parent_form.runFormulaScript(
                            SCRIPT_ID_DELIMITER.join(['hidewhen', parent_form.id, hidewhen.id, 'formula']),
                            target,
                            hidewhen.Formula)
                except PlominoScriptException, e:
                    e.reportError(
                            '%s hide-when formula failed' % hidewhen.id)
                    #if error, we hide anyway
                    isHidden = True
                result[hidewhen.id] = isHidden

        return result

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
                        SCRIPT_ID_DELIMITER.join(['form', self.id, 'beforecreate']),
                        self,
                        self.beforeCreateDocument)
            except PlominoScriptException, e:
                e.reportError('beforeCreate formula failed')

        tmp = None
        if not self.isPage and hasattr(self, 'REQUEST'):
            # hideWhens need a TemporaryDocument
            tmp = getTemporaryDocument(
                    db,
                    self,
                    self.REQUEST).__of__(db)
        if (not invalid) or self.hasDesignPermission(self):
            editmode=True
            form_mode = request.get('plomino_form_mode')
            if form_mode and form_mode == 'READ':
                editmode=False
            if form_mode and form_mode == 'EDIT':
                editmode=True

            alternate_form = request.get('plomino_alternate_form')
            if alternate_form:
                form = db.getForm('%s' % alternate_form)
                return form.displayDocument(
                    tmp,
                    editmode=editmode,
                    creation=False,
                    request=request
                )
            return self.displayDocument(
                    tmp,
                    editmode=editmode,
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
        self.cleanFormulaScripts(SCRIPT_ID_DELIMITER.join(["form", self.id]))

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
                        SCRIPT_ID_DELIMITER.join(['field', self.id, fieldname, 'formula']),
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
    def _has_fieldtypes(self, types, applyhidewhen=True):
        """ ``types`` is a list of strings.
        Check if any of those types are present.
        """
        tmp = None
        db = self.getParentDatabase()
        if hasattr(self, 'REQUEST'):
            # hideWhens need a TemporaryDocument
            tmp = getTemporaryDocument(
                    db,
                    self,
                    self.REQUEST).__of__(db)
        fields = self.getFormFields(
                includesubforms=True,
                doc=tmp,
                applyhidewhen=applyhidewhen)
        for f in fields:
            if f.getFieldType() in types:
                return True
        return False

    security.declarePublic('hasGoogleVisualizationField')
    def hasGoogleVisualizationField(self):
        """ Return true if the form contains at least one GoogleVisualization field
        """
        return self._has_fieldtypes(["GOOGLEVISUALIZATION"], applyhidewhen=False)

    security.declarePublic('getSubforms')
    def getSubforms(self, doc=None, applyhidewhen=True, validation_mode=False):
        """ Return the names of the subforms embedded in the form.
        """
        if applyhidewhen:
            if doc is None and hasattr(self, 'REQUEST'):
                try:
                    db = self.getParentDatabase()
                    doc = getTemporaryDocument(
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
                        # this case where 'None' can happen in the case of
                        # datetimes which need to process the input first before
                        # its possible to work out they are empty.
                        if v is not None:
                            if f.getFieldType() == 'SELECTION':
                                if f.getSettings().widget in [
                                        'MULTISELECT', 'CHECKBOX', 'PICKLIST']:
                                    v = asList(v)
                            doc.setItem(fieldName, v)
                        else:
                            doc.removeItem(fieldName)
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
                        # if datetime widget, the request param contains an object
                        if getattr(REQUEST.get(fieldname), 'year'):
                            submittedValue = "%(year)s-%(month)s-%(day)s %(hour)s:%(minute)s" % self.REQUEST.get('birthDate')
                        v = StringToDate(submittedValue, format='%Y-%m-%d %H:%M')
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
                                SCRIPT_ID_DELIMITER.join(['form', self.id, 'searchformula']),
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


    security.declarePrivate('_get_js_hidden_subforms')
    def _get_js_hidden_subforms(self, REQUEST, doc, validation_mode=False):
        hidden_forms = []
        hidewhens = self.getHidewhen(REQUEST, doc=doc,
                    validation_mode=validation_mode)
        html_content = self._get_html_content()
        for hidewhenName, doit in hidewhens.items():
            if not doit: # Only consider True hidewhens
                continue
            start = ('<span class="plominoHidewhenClass">start:%s</span>' %
                    hidewhenName)
            end = ('<span class="plominoHidewhenClass">end:%s</span>' %
                    hidewhenName)
            for hiddensection in re.findall(
                    start + '(.*?)' + end,
                    html_content):
                hidden_forms += re.findall(
                    '<span class="plominoSubformClass">([^<]+)</span>',
                    hiddensection)
        for subformname in self.getSubforms(doc):
            subform = self.getParentDatabase().getForm(subformname)
            if not subform:
                msg = 'Missing subform: %s. Referenced on: %s' % (subformname, self.id)
                self.writeMessageOnPage(msg, self.REQUEST)
                logger.info(msg)
                continue
            hidden_forms += subform._get_js_hidden_subforms(REQUEST, doc)
        return hidden_forms

    security.declarePrivate('_get_js_hidden_fields')
    def _get_js_hidden_fields(self, REQUEST, doc, validation_mode=False):
        hidden_fields = []
        hidewhens = self.getHidewhen(REQUEST, doc=doc,
                    validation_mode=validation_mode)
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
        db = self.getParentDatabase()
        tmp = getTemporaryDocument(
                db,
                self,
                REQUEST,
                doc,
                validation_mode=True).__of__(db)

        fields = self.getFormFields(
                includesubforms=True,
                # doc=doc,
                doc=tmp,
                applyhidewhen=True,
                validation_mode=True,
                request=REQUEST)

        hidden_fields = self._get_js_hidden_fields(
                REQUEST,
                # doc,
                tmp,
                validation_mode=True)

        hidden_forms = self._get_js_hidden_subforms(
                REQUEST,
                # doc,
                tmp,
                validation_mode=True)
        for form_id in hidden_forms:
            form = db.getForm(form_id)
            for field in form.getFormFields():
                hidden_fields.append(field.getId())

        fields = [field for field in fields
                if field.getId() not in hidden_fields]

        errors=[]
        for f in fields:
            fieldname = f.id
            fieldtype = f.getFieldType()
            submittedValue = REQUEST.get(fieldname)

            field_errors = []

            # STEP 1: check mandatory fields
            if not submittedValue:
                if f.getMandatory() is True:
                    if fieldtype == "ATTACHMENT" and doc:
                        existing_files = doc.getItem(fieldname)
                        if not existing_files:
                            field_errors.append("%s %s" % (
                                f.Title(),
                                PlominoTranslate("is mandatory", self)))
                    else:
                        field_errors.append("%s %s" % (
                            f.Title(),
                            PlominoTranslate("is mandatory", self)))
            else:
                #
                # STEP 2: check validation formula
                #
                # This may massage the submitted value e.g. to make it pass STEP 3
                #
                formula = f.getValidationFormula()
                if formula:
                    error_msg = ''
                    try:
                        error_msg = self.runFormulaScript(
                                SCRIPT_ID_DELIMITER.join([
                                    'field', self.id, f.id,
                                    'ValidationFormula']),
                                tmp,
                                # doc,
                                f.ValidationFormula)
                    except PlominoScriptException, e:
                        e.reportError('%s validation formula failed' % f.id)
                    if error_msg:
                        field_errors.append(error_msg)
                    # May have been changed by formula
                    submittedValue = REQUEST.get(fieldname)
                #
                # STEP 3: check data types
                #
                field_errors = field_errors + f.validateFormat(submittedValue)

            for field_error in field_errors:
                errors.append({'field': fieldname, 'error': field_error})

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
    def tojson(self, REQUEST=None, item=None, rendered=False):
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
            rendered_str = REQUEST.get('rendered', None)
            if rendered_str:
                rendered = True
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
                if field.getFieldType() == 'DATAGRID':
                    result = adapt.rows(
                            result, rendered=rendered)

        if datatables_format:
            result = {
                    'iTotalRecords': len(result),
                    'iTotalDisplayRecords': len(result),
                    'aaData': result}

        logger.info('PlominoForm.tojson> item: %s, result: %s' % (`item`, `result`[:20])) #DBG
        return json.dumps(result)

    def _getDatabaseViews(self):
        db = self.getParentDatabase()
        views = db.getViews()
        return [''] + [v.id for v in views]

registerType(PlominoForm, PROJECTNAME)

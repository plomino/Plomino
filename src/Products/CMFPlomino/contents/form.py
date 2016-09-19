from AccessControl import ClassSecurityInfo
import decimal
from jsonutil import jsonutil as json
import logging
from lxml.html import tostring
from plone import api
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives as form
from plone.dexterity.content import Container
from plone.supermodel import directives, model
from z3c.form.datamanager import AttributeField, zope
from Products.CMFPlomino.contents.action import PlominoAction
from Products.CMFPlomino.contents.field import PlominoField
import re
from zope import schema
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary

from .. import _, plomino_profiler
from ..config import (
    DESIGN_PERMISSION,
    READ_PERMISSION,
    SCRIPT_ID_DELIMITER,
)
from ..exceptions import PlominoScriptException
from ..interfaces import IPlominoContext
from ..utils import (
    asList,
    asUnicode,
    DateToString,
    PlominoTranslate,
    StringToDate,
    translate,
    urlquote,
)
from ..document import getTemporaryDocument
from pyquery import PyQuery as pq

logger = logging.getLogger('Plomino')
security = ClassSecurityInfo()

label_re = re.compile('<span class="plominoLabelClass">((?P<optional_fieldname>\S+):){0,1}\s*(?P<fieldname_or_label>.+?)</span>')

class IHelper(model.Schema):
    schema.Choice(values=[])

class IPlominoForm(model.Schema):
    """ Plomino form schema
    """

    # helpers = schema.List(value_type=schema.Object(IHelper),
    #                       title=u"Helpers",
    #                       description=u"Helpers applied",
    #                       required=False
    # )

    form.widget('form_layout_visual', WysiwygFieldWidget)
    form_layout_visual = schema.Text(
        title=_('CMFPlomino_label_FormLayout', default="Form layout"),
        description=_('CMFPlomino_help_FormLayout',
            default="Text with 'Plominofield' styles correspond to the"
                " contained field elements."),
        required=False,
    )

    form_method = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems(
            [("GET", "GET"), ("POST", "POST"), ("Auto", "Auto")]),
        title=_('CMFPlomino_label_FormMethod', default="Form method"),
        description=_('CMFPlomino_help_FormMethod',
            default="The form method: GET or POST or Auto (default)."),
        default="Auto",
    )

    form.widget('document_title', klass='plomino-formula')
    document_title = schema.Text(
        title=_('CMFPlomino_label_DocumentTitle',
            default="Document title formula"),
        description=_('CMFPlomino_help_DocumentTitle',
            default='Compute the document title'),
        required=False,
    )

    dynamic_document_title = schema.Bool(
        title=_('CMFPlomino_label_DynamicDocumentTitle',
            default="Compute document title on view"),
        default=False,
        description=_('CMFPlomino_help_DynamicDocumentTitle',
            default="Execute DocumentTitle formula when document is rendered"),
    )

    store_dynamic_document_title = schema.Bool(
        title=_('CMFPlomino_label_StoreDynamicDocumentTitle',
            default="Store dynamically computed title"),
        description=_('CMFPlomino_help_StoreDynamicDocumentTitle',
            default="Store computed title every time document is rendered"),
        default=False,
    )

    form.widget('document_id', klass='plomino-formula')
    document_id = schema.Text(
        title=_('CMFPlomino_label_DocumentId', default="Document id formula"),
        description=_('CMFPlomino_help_DocumentId',
            default='Compute the document id at creation. '
            '(Undergoes normalization.)'),
        required=False,
    )

    hide_default_actions = schema.Bool(
        title=_('CMFPlomino_label_HideDefaultActions',
            default="Hide default actions"),
        description=_('CMFPlomino_help_HideDefaultActions',
            default='Edit, Save, Delete, Close actions will not be displayed '
            'in the action bar'),
        default=False,
    )

    isPage = schema.Bool(
        title=_('CMFPlomino_label_isPage', default="Page"),
        default=False,
        description=_('CMFPlomino_help_isPage', default="A page cannot be"
            " saved and does not provide any action bar. It can be useful"
            " to build a welcome page, explanations, reports, navigation,"
            " etc."),
    )

    isSearchForm = schema.Bool(
        title=_('CMFPlomino_label_SearchForm', default="Search form"),
        description=_('CMFPlomino_help_SearchForm',
            default="A search form is only used to search documents, it cannot"
            " be saved."),
        default=False,
    )

    search_view = schema.TextLine(
        title=_('CMFPlomino_label_SearchView', default="Search view"),
        description=_('CMFPlomino_help_SearchView',
            default="View used to display the search results"),
        required=False,
    )

    form.widget('search_formula', klass='plomino-formula')
    search_formula = schema.Text(
        title=_('CMFPlomino_label_SearchFormula', default="Search formula"),
        description=_('CMFPlomino_help_SearchFormula',
            default="Leave blank to use default ZCatalog search"),
        required=False,
    )

    resources_js = schema.Text(
        title=_('CMFPlomino_label_FormResourcesJS', default="JavaScripts"),
        description=_('CMFPlomino_help_FormResourcesJS',
            default="JavaScript resources loaded by this form. "
                "Enter one path per line."),
        required=False,
    )

    resources_css = schema.Text(
        title=_('CMFPlomino_label_FormResourcesCSS', default="CSS"),
        description=_('CMFPlomino_help_FormResourcesCSS',
            default="CSS resources loaded by this form. "
                "Enter one path per line."),
        required=False,
    )

    # EVENTS
    directives.fieldset(
        'events',
        label=_(u'Events'),
        fields=(
            'onCreateDocument',
            'onOpenDocument',
            'beforeSaveDocument',
            'onSaveDocument',
            'onDeleteDocument',
            'onSearch',
            'beforeCreateDocument',
        ),
    )

    form.widget('onCreateDocument', klass='plomino-formula')
    onCreateDocument = schema.Text(
        title=_('CMFPlomino_label_onCreateDocument',
            default="On create document"),
        description=_('CMFPlomino_help_onCreateDocument',
            default="Action to take when the document is created"),
        required=False,
    )

    form.widget('onOpenDocument', klass='plomino-formula')
    onOpenDocument = schema.Text(
        title=_('CMFPlomino_label_onOpenDocument', default="On open document"),
        description=_('CMFPlomino_help_onOpenDocument',
            default="Action to take when the document is opened"),
        required=False,
    )

    form.widget('beforeSaveDocument', klass='plomino-formula')
    beforeSaveDocument = schema.Text(
        title=_('CMFPlomino_label_beforeSaveDocument',
            default="Before save document"),
        description=_('CMFPlomino_help_beforeSaveDocument',
            default="Action to take before submitted values are saved into "
            "the document (submitted values are in context.REQUEST)"),
        required=False,
    )

    form.widget('onSaveDocument', klass='plomino-formula')
    onSaveDocument = schema.Text(
        title=_('CMFPlomino_label_onSaveDocument', default="On save document"),
        description=_('CMFPlomino_help_onSaveDocument',
            default="Action to take when saving the document"),
        required=False,
    )

    form.widget('onDeleteDocument', klass='plomino-formula')
    onDeleteDocument = schema.Text(
        title=_('CMFPlomino_label_onDeleteDocument',
            default="On delete document"),
        description=_('CMFPlomino_help_onDeleteDocument',
            default="Action to take before deleting the document"),
        required=False,
    )

    form.widget('onSearch', klass='plomino-formula')
    onSearch = schema.Text(
        title=_('CMFPlomino_label_onSearch',
            default="On submission of search form"),
        description=_('CMFPlomino_help_onSearch',
            default="Action to take when submitting a search"),
        required=False,
    )

    form.widget('beforeCreateDocument', klass='plomino-formula')
    beforeCreateDocument = schema.Text(
        title=_('CMFPlomino_label_beforeCreateDocument',
            default="Before document creation"),
        description=_('CMFPlomino_help_beforeCreateDocument',
            default="Action to take when opening a blank form"),
        required=False,
    )


class PlominoForm(Container):
    implements(IPlominoForm, IPlominoContext)

    def getForm(self, formname=None):
        """ In case we're being called via acquisition.
        """
        if formname:
            return self.getParentDatabase().getForm(formname)

        form = self
        while getattr(form, 'portal_type', '') != 'PlominoForm':
            form = form.aq_parent
        return form

    def getFormMethod(self):
        """ Return form submit HTTP method
        """
        value = self.form_method
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
        value = getattr(self, field_name)
        if not value:
            return
        value = value.splitlines()
        for url in value:
            url = str(url.strip())
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
        return self._get_resource_urls('resources_css')

    def get_resources_js(self):
        return self._get_resource_urls('resources_js')

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
                REQUEST.RESPONSE.setStatus(400)
                REQUEST.RESPONSE.setHeader(
                    'content-type', 'application/json; charset=utf-8')
                return json.dumps({'errors': errors})
            return self.notifyErrors(errors)

        ################################################################
        # If child form, return a values as JSON
        if is_childform:
            tmp = getTemporaryDocument(db, self, REQUEST).__of__(db)
            rowdata = {}
            for field in self.getFormFields(request=REQUEST):
                rowdata[field.id] = {
                    'raw': tmp.getItem(field.id, None),
                    'rendered': tmp.getRenderedItem(field.id),
                }
            REQUEST.RESPONSE.setHeader(
                'content-type', 'application/json; charset=utf-8')
            return json.dumps(rowdata)

        ################################################################
        # Add a document to the database
        doc = db.createDocument()
        doc.setItem('Form', self.id)

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
            return cache
        if not request and hasattr(self, 'REQUEST'):
            request = self.REQUEST
        form = self.getForm()
        fieldlist = [obj for obj in form.objectValues()
            if obj.__class__.__name__ == 'PlominoField']
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
        hidewhens = [obj for obj in self.objectValues()
            if obj.__class__.__name__ == 'PlominoHidewhen']
        return hidewhens

    security.declarePublic('getFormActions')

    security.declarePublic('getHidewhen')

    def getHidewhen(self, id):
        """ Get a hide-when formula
        """
        return getattr(self, id)

    def getFormActions(self):
        """ Get all actions
        """
        actions = [obj for obj in self.objectValues()
            if obj.__class__.__name__ == 'PlominoAction']
        return actions

    security.declarePublic('getAction')

    def getAction(self, action_name):
        """ Get a single action
        """
        return getattr(self, action_name)

    security.declarePublic('getActions')

    def getActions(self, target=None, hide=True):
        """ Get filtered form actions for the target (page or document).
        """
        actions = self.getFormActions()
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
        cacheformulas = [obj for obj in self.objectValues()
            if obj.__class__.__name__ == 'PlominoCache']
        return cacheformulas

    def _handleLabels(self, html_content_orig, editmode):
        """ Parse the layout for label tags,

        - add 'label' or 'fieldset/legend' markup to the corresponding fields.
        - if the referenced field does not exist, leave the layout markup as
          is (as for missing field markup).
        """
        # Don't try to process an empty HTML doc
        if not html_content_orig:
            return html_content_orig

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
                        # If it's a dynamic field we want this in our groping
                        group_field_id = field_node.text().strip()
                        group_field = self.getFormField(group_field_id)
                        if group_field is not None and group_field.isDynamicField:
                            found_in_sibling = True
                        # otherwise disolve grouping
                        else:
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

            field_type = field.field_type
            if hasattr(field, 'widget'):
                widget_name = field.widget

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
                try:
                    ng = pq(grouping).insert_before(pq(togroup).eq(0))
                    pq(ng).append(pq(togroup))
                except:
                    raise
                if field.mandatory:
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
        # remove the hidden content
        if doc is None:
            db = self.getParentDatabase()
            hidewhen_target = getTemporaryDocument(
                db,
                self,
                self.REQUEST
            )
        else:
            hidewhen_target = doc
        html_content = self.applyHideWhen(hidewhen_target, silent_error=False)
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

        # inject request parameters as input hidden for fields not part of the
        # layout
        if creation and request is not None:
            for field_id in fieldids_not_in_layout:
                if field_id in request:
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

        # if editmode, we add a hidden field to handle the Form item value
        if editmode and not parent_form_id:
            html_content = ("<input type='hidden' "
                    "name='Form' "
                    "value='%s' />%s" % (
                        self.id,
                        html_content))

        # Handle legends and labels
        html_content = self._handleLabels(html_content, editmode)

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
            action_span = '<span class="plominoActionClass">%s</span>' % (
                action_id)
            if action_span in html_content:
                if not action.isHidden(target, form):
                    pt = form.unrestrictedTraverse(
                        "@@plomino_actions").embedded_action
                    action_render = pt(display=action.action_display,
                        plominoaction=action,
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
        field_ids = parent_field.field_mapping.split(',')

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

    #@property
    # Using special datamanager because @property losses acquisition
    def getForm_layout_visual(self):
        #update all teh example widgets
        # TODO: called twice during setter to check if changed
        d = pq(self.form_layout, parser='html_fragments')
        root = d[0].getparent() if d else d
        s = ".plominoActionClass,.plominoSubformClass,.plominoFieldClass"
        for element in d.find(s) + d.filter(s):
            widget_type = element.attrib["class"][7:-5].lower()
            id = element.text
            example = self.example_widget(widget_type, id)
            # .html has a bug - https://github.com/gawel/pyquery/issues/102
            # so can't use it. below will strip off initial text but that's ok
            # pq(element)\
            #     .empty()\
            #     .append(pq(example, parser='html_fragments'))\
            #     .add_class("mceNonEditable")\
            #     .attr("data-plominoid", id)
            html = u'<{tag} class="{pclass} mceNonEditable" data-plominoid="{id}">{example}</{tag}>'.format(
                id=id,
                example=example,
                tag=u'div' if pq(element).has_class('plominoSubformClass') else u'span',
                pclass=pq(element).attr('class')
            )
            pq(element).replace_with(html)

        s = ".plominoLabelClass"
        for element in d.find(s) + d.filter(s):
            # The label may either contain the id or some text/html
            #   <span class="plominoLabelClass">id</span>
            #   <span class="plominoLabelClass">id:Custom label</span>
            # If it contains text/html, wrap it inside a div
            if ':' not in element.text:
                id = element.text
                html = u'<span class="plominoLabelClass mceNonEditable" data-plominoid="{id}">&nbsp;</span>'.format(id=id)
            else:
                id, html = pq(element).html().split(':', 1)
                html = u'''<div class="plominoLabelClass mceNonEditable" data-plominoid="{id}">
<div class="plominoLabelContent mceEditable">
{html}
</div>
</div>'''.format(id=id, html=html)
            pq(element).replace_with(html)

        s = ".plominoHidewhenClass,.plominoCacheClass"
        for element in d.find(s) + d.filter(s):
            widget_type = element.attrib["class"][7:-5].lower()
            if ':' not in element.text:
                continue
            pos, id = element.text.split(':', 1)

            # .html has a bug - https://github.com/gawel/pyquery/issues/102
            tail = element.tail
            pq(element)\
                .html("&nbsp;")\
                .add_class("mceNonEditable")\
                .attr("data-plomino-position", pos)\
                .attr("data-plominoid", id)
            element.tail = tail

        return tostring_innerhtml(root)

    #@form_layout_visual.setter
    # Using special datamanager because @property losses acquisition
    def setForm_layout_visual(self, layout):
        # Handle an empty layout
        if not layout:
            layout = u''
        layout = layout.replace(u'\r' , u'')
        layout = layout.replace(u'\xa0', u' ')
        d = pq(layout, parser='html_fragments')
        root = d[0].getparent() if d else d

        # restore start: end: type elements
        s = ".plominoHidewhenClass,.plominoCacheClass"
        for e in d.find(s) + d.filter(s):
            # .html has a bug - https://github.com/gawel/pyquery/issues/102
            position = pq(e).attr("data-plomino-position")
            hwid = pq(e).attr("data-plominoid")
            if position and hwid:
                pq(e).text("{pos}:{id}".format(pos=position, id=hwid))
            pq(e)\
                .remove_class("mceNonEditable")\
                .remove_attr("data-plominoid")\
                .remove_attr("data-plomino-position")

        s = ".plominoLabelClass"
        for e in d.find(s) + d.filter(s):
            element = pq(e)
            tag = e.tag
            id = element.attr("data-plominoid")

            if tag == 'span':
                # Tidy up the label
                element.remove_class("mceNonEditable")
                element.remove_attr("data-plominoid")
                element.empty()
                # Set the id as the text
                element.text(id)
            elif tag == 'div':
                html = element.find('.plominoLabelContent').html()
                # XXX: Improve the unwrapping of block elements
                for elem in ['p']:
                    html = html.replace('<%s>' % elem, ' ')
                    html = html.replace('</%s>' % elem, ' ')
                    # Possible empty tag
                    html = html.replace('<%s/>' % elem , ' ')
                span = u'<span class="plominoLabelClass">{id}:{html}</span>'.format(id=id, html=html)
                element.replace_with(span)

        # Re-parse the html as we can't replace elements multiple times
        html = tostring_innerhtml(root)
        d = pq(html, parser='html_fragments')
        root = d[0].getparent() if d else d

        # strip out all the example widgets
        s="*[data-plominoid]"
        for e in d.find(s) + d.filter(s):
            span = '<span class="{pclass}">{id}</span>'.format(
                    id=pq(e).attr("data-plominoid"),
                    pclass=pq(e).remove_class("mceNonEditable").attr('class')
                )
            pq(e).replace_with(span)
        self.form_layout = tostring_innerhtml(root)

    security.declarePrivate('_get_html_content')

    def _get_html_content(self):
        # get the raw value for rendering the form
        html_content = self.form_layout or ''
        return html_content.replace('\n', '')

    def example_widget(self, widget_type, id):
        if not id:
            return
        db = self.getParentDatabase()
        if widget_type == "field":
            field = self.getFormField(id)
            if field is not None:
                html = field.getRenderedValue(fieldvalue=None,
                                              editmode="EDITABLE",
                                              target=self)
                # need to determine if the html will get wiped
                field_pq = pq(html)
                blocks = 'input,select,table,textarea,button,img,video'
                if not field_pq.text() and not field_pq.filter(blocks) and not field_pq.find(blocks):
                    #TODO: bit of a hack. perhaps need somethign better
                    return id
                else:
                    # Handle hidden fields
                    hidden = field_pq.find('input[type="hidden"]')
                    if hidden:
                        pq('<span>[hidden field]</span>').insertBefore(hidden)

                    return field_pq.outer_html()

        elif widget_type == "subform":
            subform = getattr(self, id, None)
            if not isinstance(subform, PlominoForm):
                return
            doc = getTemporaryDocument(db, form=subform,
                                       REQUEST={}).__of__(db)
            rendering = subform.displayDocument(
                doc, editmode=True, creation=True, parent_form_id=self.id,
            )
            return rendering

        elif widget_type == 'action':
            action = getattr(self, id, None)
            if not isinstance(action, PlominoAction):
                return
            pt = self.unrestrictedTraverse(
                        "@@plomino_actions").embedded_action
            action_render = pt(display=action.action_display,
                plominoaction=action,
                plominotarget=self,
                plomino_parent_id=self.id)
            return action_render


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
                    SCRIPT_ID_DELIMITER.join(
                        ['hidewhen', self.id, hidewhen.id, 'formula']),
                    target,
                    hidewhen.formula)
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
                # if error, we hide anyway
                result = True

            start = ('<span class="plominoHidewhenClass">start:%s</span>' %
                hidewhenName)
            end = ('<span class="plominoHidewhenClass">end:%s</span>' %
                hidewhenName)

            if hidewhen.isDynamicHidewhen:
                if result:
                    style = ' style="display: none"'
                else:
                    style = ''
                html_content = re.sub(
                    start,
                    '<div class="plomino-hidewhen" data-hidewhen="%s/%s"%s>' % (
                        self.id,
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

    security.declareProtected(READ_PERMISSION, 'dynamic_evaluation')

    def dynamic_evaluation(self, REQUEST):
        """ Return a JSON object to dynamically refresh the form
        (hidewhens, field validation, dynamic fields)
        """
        db = self.getParentDatabase()
        docid = REQUEST.get('_docid')
        if not docid:
            doc = None
        else:
            doc = db.getDocument(docid)
        temp = {}
        temp[self.id] = getTemporaryDocument(
            db,
            self,
            REQUEST,
            doc,
            validation_mode=True).__of__(db)

        results = {
            'errors': self.validateInputs(REQUEST, doc=doc, tmp=temp[self.id])
        }

        hidewhens = asList(REQUEST.get('_hidewhens[]', []))
        hidewhens_results = []
        for token in hidewhens:
            (formid, hwid) = token.split('/')
            if formid == self.id:
                form = self
            else:
                form = db.getForm(formid)
                if not form:
                    db.writeMessageOnPage(
                        "Form %s id missing" % formid, REQUEST, False)
                    hidewhens_results.append(["%s/%s" % (formid, hwid), True])
                    continue
            if formid not in temp:
                temp[formid] = getTemporaryDocument(
                    db,
                    db.getForm(formid),
                    REQUEST,
                    doc,
                    validation_mode=False)
            try:
                hidewhen = form.getHidewhen(hwid)
                isHidden = form.runFormulaScript(
                    SCRIPT_ID_DELIMITER.join([
                        'hidewhen', formid, hwid, 'formula'
                    ]),
                    temp[formid],
                    hidewhen.formula)
            except PlominoScriptException, e:
                e.reportError(
                    '%s hide-when formula failed' % hwid)
                # if error, we hide anyway
                isHidden = True
            hidewhens_results.append(["%s/%s" % (formid, hwid), isHidden])
        results['hidewhens'] = hidewhens_results

        fields = asList(REQUEST.get('_fields[]', []))
        fields_results = []
        for token in fields:
            (formid, fieldid) = token.split('/')
            if formid == self.id:
                form = self
            else:
                form = db.getForm(formid)
                if not form:
                    db.writeMessageOnPage(
                        "Form %s id missing" % formid, REQUEST, False)
                    fields_results.append(["%s/%s" % (formid, fieldid), True])
                    continue
            if formid not in temp:
                temp[formid] = getTemporaryDocument(
                    db,
                    db.getForm(formid),
                    REQUEST,
                    doc,
                    validation_mode=False)
            try:
                # We already have the right form for the field
                value = form.computeFieldValue(fieldid, temp[formid])
            except PlominoScriptException, e:
                e.reportError(
                    '%s field formula failed' % fieldid)
                # if error, return an empty value
                value = ''
            fields_results.append(["%s/%s" % (formid, fieldid), value])

        results['fields'] = fields_results

        REQUEST.RESPONSE.setHeader(
            'content-type', 'application/json; charset=utf-8')
        return json.dumps(results)

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
                    "cache_" + self.id + "_" + cacheid + "_formula",
                    target,
                    cacheformula.formula)
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
                cachekey = 'fragment_' + cachekey
                fragment = self.getParentDatabase().getCache(cachekey)
                if fragment:
                    # the fragment was in cache, we insert it
                    regexp = start + '.*?' + end
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
            regexp = start + '(.*?)' + end
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
                    SCRIPT_ID_DELIMITER.join([
                        'form', self.id, 'beforecreate']),
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
            return self.displayDocument(
                tmp,
                editmode=True,
                creation=True,
                request=request)
        else:
            self.REQUEST.RESPONSE.redirect(
                db.absolute_url() +
                "/plomino_errors?error=" +
                urlquote(invalid.encode('utf-8')))

    security.declarePublic('getFormField')

    def getFormField(self, fieldname, includesubforms=True):
        """ Return the field
        """
        field = None
        form = self.getForm()
        field_ids = [obj.id for obj in form.objectValues()
            if obj.__class__.__name__ == 'PlominoField']
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
                    SCRIPT_ID_DELIMITER.join(
                        ['field', self.id, fieldname, 'formula']),
                    target,
                    field.formula,
                    True,
                    self,
                )
            except PlominoScriptException, e:
                logger.warning(
                    '%s field formula failed' % fieldname,
                    exc_info=True)
                if report:
                    e.reportError('%s field formula failed' % fieldname)

        return fieldvalue

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
            if f.field_type in types:
                return True
        return False

    security.declarePublic('hasGoogleVisualizationField')

    def hasGoogleVisualizationField(self):
        """ Return true if the form contains at least one GoogleVisualization field
        """
        return self._has_fieldtypes(
            ["GOOGLEVISUALIZATION"], applyhidewhen=False)

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

    def readInputs(
        self,
        doc,
        REQUEST,
        process_attachments=False,
        applyhidewhen=True,
        validation_mode=False
    ):
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
            mode = f.field_mode
            fieldName = f.id
            if mode == "EDITABLE":
                submittedValue = REQUEST.get(fieldName)
                if submittedValue is not None:
                    if submittedValue == '':
                        doc.removeItem(fieldName)
                    else:
                        v = f.processInput(
                            submittedValue,
                            doc,
                            process_attachments,
                            validation_mode=validation_mode)
                        if f.field_type == 'SELECTION':
                            if f.widget in [
                                'MULTISELECT', 'CHECKBOX', 'PICKLIST'
                            ]:
                                v = asList(v)
                        doc.setItem(fieldName, v)
                else:
                    # The field was not submitted, probably because it is
                    # not part of the form (hide-when, ...) so we just leave
                    # it unchanged. But with SELECTION, DOCLINK or BOOLEAN, we
                    # need to presume it was empty (as SELECT/checkbox/radio
                    # tags do not submit an empty value, they are just missing
                    # in the querystring)
                    if applyhidewhen and f in displayed_fields:
                        fieldtype = f.field_type
                        if (fieldtype in ("SELECTION", "DOCLINK", "BOOLEAN")):
                            doc.removeItem(fieldName)

    security.declareProtected(READ_PERMISSION, 'searchDocuments')

    def searchDocuments(self, REQUEST):
        """ Search documents in the view matching the submitted form fields values.

        1. If there is an onSearch event, use the onSearch formula to generate
        a result set.
        2. Otherwise, do a dbsearch among the documents of the related view,
        2.1. and if there is a searchformula, evaluate that for every document
        in the view.
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

            # index search
            index = db.getIndex()
            query = {'PlominoViewFormula_' + searchview.id: True}

            for f in self.getFormFields(
                includesubforms=True,
                request=REQUEST
            ):
                fieldname = f.id
                # if fieldname is not an index -> search doesn't matter and
                # returns all
                submittedValue = REQUEST.get(fieldname)
                if submittedValue:
                    submittedValue = asUnicode(submittedValue)
                    # if non-text field, convert the value
                    if f.field_type == "NUMBER":
                        if f.number_type == "INTEGER":
                            v = long(submittedValue)
                        elif f.number_type == "FLOAT":
                            v = float(submittedValue)
                        elif f.number_type == "DECIMAL":
                            v = decimal(submittedValue)
                    elif f.field_type == "DATETIME":
                        # The format submitted by the datetime widget:
                        v = StringToDate(submittedValue,
                            format='%Y-%m-%d %H:%M')
                    else:
                        v = submittedValue
                    # rename Plomino_SearchableText to perform full-text
                    # searches on regular SearchableText index
                    if fieldname == "Plomino_SearchableText":
                        fieldname = "SearchableText"
                    query[fieldname] = v

            sortindex = searchview.sort_column
            if not sortindex:
                sortindex = None
            results = index.dbsearch(
                query,
                sortindex=sortindex,
                reverse=searchview.reverse_sorting)

            # filter search with searchformula
            searchformula = self.search_formula
            if searchformula:
                filteredResults = []
                try:
                    for doc in results:
                        valid = self.runFormulaScript(
                            SCRIPT_ID_DELIMITER.join(
                                ['form', self.id, 'searchformula']),
                            doc.getObject(),
                            self.searchFormula)
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

    security.declarePublic('validateInputs')

    def validateInputs(self, REQUEST, doc=None, tmp=None):
        """
        """
        db = self.getParentDatabase()
        if not tmp:
            tmp = getTemporaryDocument(
                db,
                self,
                REQUEST,
                doc,
                validation_mode=True).__of__(db)

        fields = self.getFormFields(
            includesubforms=True,
            doc=tmp,
            applyhidewhen=True,
            validation_mode=True,
            request=REQUEST)

        errors = []
        for f in fields:
            fieldname = f.id
            fieldtype = f.field_type
            submittedValue = REQUEST.get(fieldname)

            # STEP 1: check mandatory fields
            if not submittedValue:
                if f.mandatory is True:
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
            #
            # STEP 2: check validation formula
            #
            # This may massage the submitted value e.g. to make it pass
            # STEP 3
            formula = f.validation_formula
            if formula:
                error_msg = ''
                try:
                    error_msg = self.runFormulaScript(
                        SCRIPT_ID_DELIMITER.join([
                            'field', self.id, f.id,
                            'ValidationFormula']),
                        tmp,
                        f.validation_formula)
                except PlominoScriptException, e:
                    e.reportError('%s validation formula failed' % f.id)
                if error_msg:
                    errors.append(error_msg)
                # May have been changed by formula
                submittedValue = REQUEST.get(fieldname)
            #
            # STEP 3: check data types
            #
            if submittedValue:
                errors = errors + f.validateFormat(submittedValue)

        return errors

    security.declarePublic('notifyErrors')

    def notifyErrors(self, errors):
        return self.unrestrictedTraverse("@@plomino_errors")(errors=errors)

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
                api.portal.show_message(
                    message='%s is already an existing object.' % view_id,
                    request=REQUEST,
                    type='error'
                )
                REQUEST.RESPONSE.redirect(self.absolute_url_path())
            return
        view_title = "All " + self.Title()
        formula = 'plominoDocument.getItem("Form")=="%s"' % self.id
        db.invokeFactory(
            'PlominoView',
            id=view_id,
            title=view_title,
            selection_formula=formula)
        view_obj = getattr(db, view_id)

        fields = self.getFormFields(includesubforms=True)
        acceptable_types = ["TEXT", "NUMBER", "NAME", "SELECTION",
                "DATETIME"]
        fields = [f for f in fields
                if f.field_mode == "EDITABLE" and
                f.field_type in acceptable_types]
        for f in fields:
            col_id = f.id.replace('_', '').replace('-', '')
            col_title = f.title
            col_definition = self.id + '/' + f.id
            view_obj.invokeFactory(
                'PlominoColumn',
                id=col_id,
                title=col_title,
                displayed_field=col_definition)
        view_obj.invokeFactory(
            'PlominoAction',
            id='add_new',
            title="Add a new " + self.title,
            action_type="OPENFORM",
            action_display="BUTTON",
            content=self.id)

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



class GetterSetterAttributeField(AttributeField):
    """Special datamanager to get around loss on acqusition when using @property"""
    zope.component.adapts(
        IPlominoForm, zope.schema.interfaces.IField)

    def get(self):
        """See z3c.form.interfaces.IDataManager"""
        getter = "get%s"%self.field.__name__.capitalize()
        if hasattr(self.adapted_context, getter):
            return getattr(self.adapted_context, getter)()
        else:
            return getattr(self.adapted_context, self.field.__name__)

    def set(self, value):
        """See z3c.form.interfaces.IDataManager"""
        if self.field.readonly:
            raise TypeError("Can't set values on read-only fields "
                            "(name=%s, class=%s.%s)"
                            % (self.field.__name__,
                               self.context.__class__.__module__,
                               self.context.__class__.__name__))
        setter = "set%s"%self.field.__name__.capitalize()
        if hasattr(self.adapted_context, setter):
            getattr(self.adapted_context, setter)(value)
        else:
            # get the right adapter or context
            setattr(self.adapted_context, self.field.__name__, value)


def tostring_innerhtml(root):
    """ pyquery doesn't handle remove or replace_with well when you are dealing
    with fragments
    """
    if not root:
        return ''
    return (root.text or '') + ''.join([tostring(child) for child in root.iterchildren()])
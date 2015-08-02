from AccessControl import ClassSecurityInfo
import logging
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives as form
from plone.dexterity.content import Container
from plone.supermodel import model
import re
from zope import schema
from zope.interface import implements

from .. import _, plomino_profiler
from ..config import SCRIPT_ID_DELIMITER, READ_PERMISSION
from ..exceptions import PlominoScriptException
from ..utils import asUnicode, translate
from document import getTemporaryDocument

logger = logging.getLogger('Plomino')
security = ClassSecurityInfo()


class IPlominoForm(model.Schema):
    """ Plomino form schema
    """

    title = schema.TextLine(
        title=_(u"Title"),
        required=True,
    )

    description = schema.Text(
        title=_(u"Description"),
        required=False,
    )

    form.widget('form_layout', WysiwygFieldWidget)
    form_layout = schema.Text(
        title=_('CMFPlomino_label_FormLayout', default="Form layout"),
        description=_('CMFPlomino_help_FormLayout',
            default="Text with 'Plominofield' styles correspond to the"
                " contained field elements."),
    )

    isPage = schema.Bool(
        title=_('CMFPlomino_label_isPage', default="Page"),
        required=False,
        description=_('CMFPlomino_help_isPage', default="A page cannot be"
            " saved and does not provide any action bar. It can be useful"
            " to build a welcome page, explanations, reports, navigation,"
            " etc."),
    )


class PlominoForm(Container):
    implements(IPlominoForm)

    def getForm(self, formname=None):
        """ In case we're being called via acquisition.
        """
        if formname:
            return self.getParentDatabase().getForm(formname)

        form = self
        while getattr(form, 'portal_type', '') != 'PlominoForm':
            form = form.aq_parent
        return form

    security.declarePublic('getFormFields')

    def getFormFields(self, includesubforms=False, doc=None,
            applyhidewhen=False, validation_mode=False, request=None,
            deduplicate=True):
        """ Get fields
        """
        db = self.getParentDatabase()
        # cache_key = "getFormFields_%d_%d_%d_%d_%d_%d" % (
        #     hash(self),
        #     hash(doc),
        #     includesubforms,
        #     applyhidewhen,
        #     validation_mode,
        #     deduplicate
        # )
        # cache = db.getRequestCache(cache_key)
        # if cache:
        #     return cache
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

        # db.setRequestCache(cache_key, result)
        return result

    security.declarePublic('getActions')

    def getActions(self, target, hide=True):
        """ Get filtered form actions for the target (page or document).
        """
        actions = [obj for obj in self.objectValues()
            if obj.__class__.__name__ == 'PlominoAction']

        filtered = []
        for action in actions:
            if hide:
                if not action.isHidden(target, self):
                    filtered.append((action, self.id))
            else:
                filtered.append((action, self.id))
        return filtered

    security.declarePublic('getHidewhenFormulas')

    def getHidewhenFormulas(self):
        """Get hide-when formulae
        """
        hidewhens = [obj for obj in self.objectValues()
            if obj.__class__.__name__ == 'PlominoHidewhen']
        return [h for h in hidewhens]

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
        #(html_content, to_be_cached) = self.applyCache(html_content, doc)

        # if editmode, we add a hidden field to handle the Form item value
        if editmode and not parent_form_id:
            html_content = ("<input type='hidden' "
                    "name='Form' "
                    "value='%s' />%s" % (
                        self.id,
                        html_content))

        # Handle legends and labels
        #html_content = self._handleLabels(html_content, editmode)
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
        #html_content = self.updateCache(html_content, to_be_cached)
        return html_content

    security.declarePrivate('_get_html_content')

    def _get_html_content(self):
        html_content = self.form_layout
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
                    SCRIPT_ID_DELIMITER.join(
                        ['hidewhen', self.id, hidewhen.id, 'formula']),
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
                # if error, we hide anyway
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
            # tmp = getTemporaryDocument(
            #     db,
            #     self,
            #     self.REQUEST).__of__(db)
            tmp = None
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

from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider, zope
from plone.dexterity.browser.add import DefaultAddForm
from plone.dexterity.browser.edit import DefaultEditForm
from plone.supermodel import model
import z3c
from z3c.form.browser.text import TextWidget
from zope import component, interface, schema
from zope.interface import implementer

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.utils import createContentInContainer

from Products.CMFPlomino.config import FIELD_MODES
from Products.CMFPlomino.contents.field import get_field_types, IPlominoField
from Products.CMFPlomino.contents.action import ACTION_TYPES, ACTION_DISPLAY
from Products.CMFPlomino.contents.action import PlominoAction
from Products.CMFPlomino.contents.field import PlominoField
from Products.CMFPlomino.contents.form import PlominoForm
from Products.CMFPlomino.contents.hidewhen import PlominoHidewhen

import json

# -*- coding: utf-8 -*-
from zope.interface import classImplements, provider


class ITinyMCEPlominoFormView(interface.Interface):
    """Marker interface"""


class TinyMCEPlominoFormView(BrowserView):
    """
    """
    interface.implements(ITinyMCEPlominoFormView)
    
    action_template = ViewPageTemplateFile('templates/tinymce/action.pt')
    def action_form(self, **params):
        """."""
        params = {}
        return self.action_template(**params)
    
    #cache_template = ViewPageTemplateFile('templates/tinymce/cache.pt')
    def cache_form(self, **params):
        """."""
        params = {}
        return self.cache_template(**params)
    
    field_template = ViewPageTemplateFile('templates/tinymce/field.pt')
    def field_form(self, **params):
        """."""
        params = {}
        return self.field_template(**params)

    label_template = ViewPageTemplateFile('templates/tinymce/label.pt')
    def label_form(self, **params):
        """."""
        params = {}
        return self.label_template(**params)
    
    hidewhen_template = ViewPageTemplateFile('templates/tinymce/hidewhen.pt')
    def hidewhen_form(self, **params):
        """."""
        params = {}
        return self.hidewhen_template(**params)
    
    subform_template = ViewPageTemplateFile('templates/tinymce/subform.pt')
    def subform_form(self, **params):
        """."""
        params = {}
        return self.subform_template(**params)
    
    error_template = ViewPageTemplateFile('templates/tinymce/error.pt')
    def error_page(self, **params):
        """."""
        params = {}
        return self.error_template(**params)
    
    valid_template = ViewPageTemplateFile('templates/tinymce/valid.pt')
    def valid_page(self, **params):
        """."""
        params = {}
        return self.valid_template(**params)



class PlominoFormSettings(object):
    """
    """
    action_template = ViewPageTemplateFile('templates/tinymce/action.pt')

    def __init__(self, context, request):
        """Initialize adapter."""
        self.context = context
        self.request = request

    def __call__(self):
        """
        """
        return self

    def getFieldTypes(self):
        """Return a list of possible types for a field.
        """
        fieldtypes = [(pair[0], pair[1][0]) for pair in get_field_types().items()]
        fieldtypes.sort(key=lambda f:f[1])
        return fieldtypes


    def getFieldModes(self):
        """Return a list of possible modes for a field.
        """
        return FIELD_MODES

    def getField(self):
        """Return a field from the request, or the first field if empty, or None if the specified field doesn't exist.
        """
        fieldid = self.request.get("fieldid", None)
        if fieldid:
            field = getattr(self.context, fieldid, None)
            if isinstance(field, PlominoField):
                return field
            else:
                return None

    def getFieldProperties(self):
        """Return properties of an action, or , if no action is given, properties filled with default values.
        """
        field = self.getField()
        if field:
            return {'fieldType': field.field_type,
                    'fieldMode': field.field_mode,
                    'formula': field.formula
                    }
        else:
             return {'fieldType': 'TEXT',
                    'fieldMode': 'EDITABLE',
                    'formula': ''
                    }

    def addField(self):
        """Add a field to the form.
        """
        fieldid = self.request.get("fieldid", None)

        # self.context is the current form
        if fieldid:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/valid_page?type=field&value=" + fieldid)
        else:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/error_page?error=no_field")

    def getLabel(self):
        pass

    def addLabel(self):
        """Add a label to the form.
        """
        labelid = self.request.get("labelid", None)
        enablecustom = self.request.get("enablecustomlabel") and '1' or '0'

        if labelid:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/valid_page?type=label&value=" + labelid + "&option=" + enablecustom)
        else:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/error_page?error=no_label")

    def getActions(self):
        """Returns a sorted list of actions
        """
        actions = self.context.aq_inner.getActions(
            None,
            False
        )
        actions = [a[0] for a in actions]
        actions.sort(key=lambda elt: elt.id.lower())
        return actions


    def getActionTypes(self):
        """Return a list of possible types for an action.
        """
        return ACTION_TYPES

    def getActionDisplay(self):
        """Return a list of possible displays for an action.
        """
        return ACTION_DISPLAY

    def getAction(self):
        """Return an action from the request, or the first action if empty, or None if the specified action doesn't exist.
        """
        actionid = self.request.get("actionid", None)
        if actionid:
            action = getattr(self.context, actionid, None)
            if isinstance(action, PlominoAction):
                return action
            else:
                return None
        return None

    def getActionProperties(self):
        """Return properties of an action, or , if no action is given, properties filled with default values.
        """
        action = self.getAction()
        if action:
            return {'title': action.title,
                    'actionType': action.action_type,
                    'actionDisplay': action.action_display,
                    'content': action.content,
                    'hideWhen': action.hidewhen,
                    'inActionBar': action.in_action_bar
                    }
        else:
             return {'title': '',
                     'actionType': 'OPENFORM',
                     'actionDisplay': 'LINK',
                     'content': '',
                     'hideWhen': '',
                     'inActionBar': False
                     }

    def addAction(self):
        """ Add an action to the form.
        """
        actionid = self.request.get("actionid", None)

        if actionid:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/valid_page?type=action&value=" + actionid)
        else:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/error_page?error=no_action")

    def addSubForm(self):
        """Add a sub-form to the form.
        """
        subformid = self.request.get("subformid", None)

        if subformid:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/valid_page?type=subform&value=" + subformid)
        else:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/error_page?error=no_label")

    def getSubForms(self):
        """Returns a list of forms from the parent database, without the current form
        """
        form = self.context.aq_inner
        subforms = form.getParentDatabase().getForms()
        subforms.remove(form)
        subforms.sort(key=lambda elt: elt.id.lower())
        return subforms

    def getHidewhenFormulas(self):
        """Returns a sorted list of Hide-when
        """
        hw = self.context.aq_inner.getHidewhenFormulas()
        hw.sort(key=lambda elt: elt.id.lower())
        return hw

    def getHidewhen(self):
        """Returns a hide-when formula from the request, or the first hide-when formula if empty, or None if the specified hide-when doesn't exist.
        """
        hidewhenid = self.request.get("hidewhenid", None)

        #if self.request.get("create", False):
        #    return None

        if hidewhenid:
            hidewhen = getattr(self.context, hidewhenid, None)
            if isinstance(hidewhen, PlominoHidewhen):
                return hidewhen
            else:
                return None
        return None

    def getHidewhenProperties(self):
        """Returns properties of a hide-when formula, or, if no hide-when formula is given, properties filled with default values.
        """
        hidewhen = self.getHidewhen()
        if hidewhen:
            return { 'formula': hidewhen.formula, 'isdynamichidewhen': hidewhen.isDynamicHidewhen }
        else:
             return { 'formula': '', 'isdynamichidewhen': False }

    def addHidewhen(self):
        """ Add a hide-when to the form.
        """
        hidewhenid = self.request.get("hidewhenid", None)

        # self.context is the current form
        if hidewhenid:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/valid_page?type=hidewhen&value=" + hidewhenid)
        else:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/error_page?error=no_hidewhen")

    #PLOMINO CACHE
    def getCacheFormulas(self):
        """Returns a sorted list of caches
        """
        hw = self.context.aq_inner.getCacheFormulas()
        hw.sort(key=lambda elt: elt.id.lower())
        return hw

    def getCacheFormula(self):
        """Returns a cache formula from the request, or the first cache formula if empty, or None if the specified cache doesn't exist.
        """
        cacheid = self.request.get("cacheid", None)

        if self.request.get("create", False):
            return None

        if cacheid:
            cache = getattr(self.context, cacheid, None)
            if isinstance(cache, PlominoCache):
                return cache
            else:
                return None

        cacheList = self.context.getCacheFormulas()
        if len(cacheList) > 0:
            return cacheList[0]
        else:
            return None

    def getCacheProperties(self):
        """Returns properties of a cache formula, or, if no cache formula is given, properties filled with default values.
        """
        cache = self.getCacheFormula()
        if cache:
            return { 'formula': cache.Formula}
        else:
             return { 'formula': ''}

    def addCache(self):
        """ Add a cache to the form.
        """
        cacheid = self.request.get("cacheid", None)
        cacheformula = self.request.get("cacheformula", '')

        # self.context is the current form
        if cacheid:
            if not hasattr(self.context, cacheid):
                self.context.invokeFactory('PlominoCache', Title=cacheid, id=cacheid, Formula=cacheformula)
                cache = getattr(self.context.aq_inner, cacheid)
                cache.setTitle(cacheid)

                self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/valid_page?type=cache&value=" + cacheid)

            else:
                self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/error_page?error=object_exists")

        else:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/error_page?error=no_cache")


    def example_widget(self):
        """ Return html of a field, hidewhen etc for inserting into the layout"""
        widget_type = self.request.get('widget_type','field')
        id = self.request.get('id')
        widget = self.context.example_widget(widget_type, id)
        self.request.RESPONSE.setHeader('content-type', 'application/json')
        return json.dumps(widget)


class TinyAjax(object):
    """
    """

    def ajax_success(self):
        """ indicator to tinymcepopup that DX is was saved ok"""
        return "<div id='ajax_success'/>"

    def ajax_cancel(self):
        """ indicator to tinymcepopup that DX is cancelled"""
        return "<div id='ajax_cancelled'/>"

class PlominoFieldSettings(object):
    """
    """

    def __init__(self, context, request):
        """Initialize adapter."""
        self.context = context
        self.request = request

    def __call__(self):
        """
        """
        return self

    def setFieldProperties(self):
        """Set field properties to their new values.
        """

        fieldtype = self.request.get("fieldtype", 'TEXT')
        fieldmode = self.request.get("fieldmode", 'EDITABLE')
        fieldformula = self.request.get("fieldformula", '')

        # self.context is the current field
        self.context.field_type = fieldtype
        self.context.field_mode = fieldmode
        self.context.formula = fieldformula

        self.request.RESPONSE.redirect(self.context.absolute_url() + "/../@@tinymceplominoform/valid_page?type=field&value=" + self.context.id)


class PlominoHidewhenSettings(object):
    """
    """

    def __init__(self, context, request):
        """ Initialize adapter."""
        self.context = context
        self.request = request

    def __call__(self):
        """
        """
        return self

    def setHidewhenProperties(self):
        """Set hidewhen properties to their new values.
        """
        hidewhenformula = self.request.get("hidewhenformula", '')
        hidewhentype = self.request.get("hidewhentype", 'static')
        isdynamic = hidewhentype=='dynamic',

        # self.context is the current hidewhen
        self.context.formula = hidewhenformula
        self.context.isdynamic = isdynamic

        self.request.RESPONSE.redirect(self.context.absolute_url() + "/../@@tinymceplominoform/valid_page?type=hidewhen&value=" + self.context.id)


class PlominoActionSettings(object):
    """
    """

    def __init__(self, context, request):
        """Initialize adapter."""
        self.context = context
        self.request = request

    def __call__(self):
        """
        """
        return self

    def setActionProperties(self):
        """Set field properties to their new values.
        """

        title = self.request.get("actiontitle", self.context.id)
        actionType = self.request.get("actiontype", 'OPENFORM')
        actionDisplay = self.request.get("actiondisplay", 'LINK')
        content = self.request.get("actioncontent", '')
        hideWhen = self.request.get("actionhidewhen", '')
        inActionBar = self.request.get("actioninactionbar", None) == 'on'

        # self.context is the current field
        self.context.title = title
        self.context.action_type = actionType
        self.context.action_display = actionDisplay
        self.context.content = content
        self.context.hidewhen = hideWhen
        self.context.in_action_bar = inActionBar

        #self.context.aq_inner.at_post_edit_script()

        self.request.RESPONSE.redirect(self.context.absolute_url() + "/../@@tinymceplominoform/valid_page?type=action&value=" + self.context.id)


def ajax_iframe_redirect(obj, event):
    """ensure if we redirect we keep ajax_ arugments"""
    request = event.object.REQUEST
    view_url = request.response.getHeader('location')
    if not view_url:
        return
    if 'ajax_load' not in request.get('HTTP_REFERER'):
        pass
    elif 'ajax_include_head' not in request.get('HTTP_REFERER'):
        view_url = view_url+'?ajax_load=1'
    else:
        view_url = view_url+'?ajax_load=1&ajax_include_head=1'
    request.response.redirect(view_url)

def ajax_iframe_cancel(obj, event):
    """ensure if we redirect we keep ajax_ arugments"""
    request = event.object.REQUEST
    view_url = request.response.getHeader('location')
    if not view_url:
        return
    if not request.get('ajax_load'):
        return
    request.response.redirect(view_url+'/@@tinyajax/ajax_cancel')

def ajax_iframe_success(obj, event):
    """ensure if we redirect we keep ajax_ arugments"""
    request = event.object.REQUEST
    view_url = request.response.getHeader('location')
    # if not view_url:
    #     if '++add++' not in request.URL:
    #         return
    #     # special case for ObjectAddedEvent which doesn't redirect until after
    #     view_url = request.URL1
    if not request.get('ajax_load'):
        return
    if hasattr(event, 'newName'):
        # object added event
        request.response.redirect(event.newParent.absolute_url()+'/@@tinyajax/ajax_success?id='+event.newName)
    else:
        request.response.redirect(view_url+'/@@tinyajax/ajax_success')

@zope.interface.implementer_only(z3c.form.interfaces.ITextWidget)
class RequestWidget(TextWidget):
    """Special widget to ignore z3cform renaming it."""

    fixed_name = 'text'
    ignoreContext = True

    @property
    def name(self):
        return self.fixed_name

    @name.setter
    def name(self, value):
        pass



@provider(IFormFieldProvider)
class IAJAXHiddenFields(model.Schema):
    """Add hidden fields to carry the ajax made through form validation errors
    """

    directives.widget('ajax_load', RequestWidget, fixed_name="ajax_load")
    ajax_load = schema.TextLine(required=False)
    directives.widget('ajax_include_head', RequestWidget, fixed_name="ajax_include_head")
    ajax_include_head = schema.TextLine(required=False)
    directives.mode(ajax_load='hidden', ajax_include_head='hidden')


@implementer(IAJAXHiddenFields)
class AJAXHiddenFields(object):
    """Don't get or set any ajax values on the context"""

    def __init__(self, context):
        self.context = context

    @property
    def ajax_load(self):
        pass

    @ajax_load.setter
    def ajax_load(self, value):
        pass

    @property
    def ajax_include_head(self):
        pass

    @ajax_include_head.setter
    def ajax_include_head(self, value):
        pass

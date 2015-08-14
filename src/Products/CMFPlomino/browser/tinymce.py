from zope import component, interface

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.dexterity.utils import createContentInContainer

from Products.CMFPlomino.config import FIELD_MODES
from Products.CMFPlomino.contents.field import get_field_types
from Products.CMFPlomino.contents.action import ACTION_TYPES, ACTION_DISPLAY
from Products.CMFPlomino.contents.action import PlominoAction
from Products.CMFPlomino.contents.field import PlominoField
#from Products.CMFPlomino.PlominoHidewhen import PlominoHidewhen
#from Products.CMFPlomino.PlominoCache import PlominoCache


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
    
    #hidewhen_template = ViewPageTemplateFile('templates/tinymce/hidewhen.pt')
    def hidewhen_form(self, **params):
        """."""
        params = {}
        return self.hidewhen_template(**params)
    
    #subform_template = ViewPageTemplateFile('templates/tinymce/subform.pt')
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


class PlominoForm(object):
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

        fieldsList = self.context.getFormFields()
        if len(fieldsList) > 0:
            return fieldsList[0]
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
        fieldtype = self.request.get("fieldtype", "TEXT")
        fieldmode = self.request.get("fieldmode", "EDITABLE")
        fieldformula = self.request.get("fieldformula", "")

        # self.context is the current form
        if fieldid:
            if not hasattr(self.context, fieldid):
                field = createContentInContainer(
                    self.context,
                    'PlominoField',
                    title=fieldid,
                    id=fieldid,
                    field_type=fieldtype,
                    field_mode=fieldmode,
                    formula=fieldformula,
                )

                self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/valid_page?type=field&value=" + fieldid + "&fieldurl=" + "/".join(field.getPhysicalPath()))

            else:
                self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/error_page?error=object_exists")

        else:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/error_page?error=no_field")


    def getActions(self):
        """Returns a sorted list of actions
        """
        actions = self.context.aq_inner.getActions(None, False)
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

        actionsList = self.context.getActions(None, False)
        if len(actionsList) > 0:
            return actionsList[0][0]
        else:
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
        title = self.request.get("actiontitle", actionid)
        actionType = self.request.get("actiontype", 'OPENFORM')
        actionDisplay = self.request.get("actiondisplay", 'LINK')
        content = self.request.get("actioncontent", '')
        hideWhen = self.request.get("actionhidewhen", '')
        inActionBar = self.request.get("actioninactionbar", None) == 'on'

        # self.context is the current form
        if actionid:
            if not hasattr(self.context, actionid):
                action = createContentInContainer(
                    self.context,
                    'PlominoAction',
                    title=title,
                    id=actionid,
                    action_type=actionType,
                    action_display=actionDisplay,
                    contnet=content,
                    hidewhen=hideWhen,
                    in_action_bar=inActionBar,
                )

                self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/valid_page?type=action&value=" + actionid)

            else:
                self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/error_page?error=object_exists")

        else:
            self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/error_page?error=no_action")

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

        if self.request.get("create", False):
            return None

        if hidewhenid:
            hidewhen = getattr(self.context, hidewhenid, None)
            if isinstance(hidewhen, PlominoHidewhen):
                return hidewhen
            else:
                return None

        hidewhenList = self.context.getHidewhenFormulas()
        if len(hidewhenList) > 0:
            return hidewhenList[0]
        else:
            return None

    def getHidewhenProperties(self):
        """Returns properties of a hide-when formula, or, if no hide-when formula is given, properties filled with default values.
        """
        hidewhen = self.getHidewhen()
        if hidewhen:
            return { 'formula': hidewhen.Formula, 'isdynamichidewhen': hidewhen.isDynamicHidewhen }
        else:
             return { 'formula': '', 'isdynamichidewhen': False }

    def addHidewhen(self):
        """ Add a hide-when to the form.
        """
        hidewhenid = self.request.get("hidewhenid", None)
        hidewhenformula = self.request.get("hidewhenformula", '')
        hidewhentype = self.request.get("hidewhentype", 'static')

        # self.context is the current form
        if hidewhenid:
            if not hasattr(self.context, hidewhenid):
                self.context.invokeFactory('PlominoHidewhen', Title=hidewhenid, id=hidewhenid, Formula=hidewhenformula, isDynamicHidewhen=hidewhentype=='dynamic')
                hidewhen = getattr(self.context.aq_inner, hidewhenid)
                hidewhen.setTitle(hidewhenid)
#                hidewhen.at_post_edit_script()

                self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/valid_page?type=hidewhen&value=" + hidewhenid)

            else:
                self.request.RESPONSE.redirect(self.context.absolute_url() + "/@@tinymceplominoform/error_page?error=object_exists")

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


class PlominoField(object):
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


class PlominoAction(object):
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
        self.context.setTitle(title)
        self.context.setActionType(actionType)
        self.context.setActionDisplay(actionDisplay)
        self.context.setContent(content)
        self.context.setHidewhen(hideWhen)
        self.context.setInActionBar(inActionBar)

        self.context.aq_inner.at_post_edit_script()

        self.request.RESPONSE.redirect(self.context.absolute_url() + "/../@@tinymceplominoform/valid_page?type=action&value=" + self.context.id)

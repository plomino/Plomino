import json
from plone.app.widgets.base import InputWidget
from plone.app.z3cform.widget import BaseWidget
from plone.behavior.interfaces import IBehaviorAssignable
from z3c.form.browser.widget import HTMLInputWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IWidget, NO_VALUE, IDataManager
from z3c.form.widget import Widget
from zope import schema
from zope.component import adapts, getMultiAdapter
from zope.configuration.config import provides
from zope.interface import implementsOnly
from zope.schema.interfaces import IList
from Products.CMFPlomino.contents.action import IPlominoAction
from Products.CMFPlomino.contents.field import IPlominoField
from Products.CMFPlomino.contents.form import IPlominoForm
from Products.CMFPlomino.contents.hidewhen import IPlominoHidewhen
from Products.CMFPlomino.contents.view import IPlominoView
import re
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.schema import getFieldsInOrder
from Products.CMFPlomino.document import getTemporaryDocument

from Products.CMFCore.interfaces import IDublinCore
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


__author__ = 'dylanjay'

class ISubformWidget(IWidget):
    """ Widget for collecting data from a list of possible subforms
    """


class SubformWidgetConverter(BaseDataConverter):
    """Convert single json input into list"""

    adapts(IList, ISubformWidget)

    def toWidgetValue(self, value):
        """Converts from field value to widget.

        :param value: Field value.
        :type value: date

        :returns: Date in format `Y-m-d`
        :rtype: string
        """
        return value

    def toFieldValue(self, value):
        """Converts from widget value to field.

        :param value: Value inserted by date widget.
        :type value: string

        :returns: `date.date` object.
        :rtype: date
        """
        return value


class SubformWidget(Widget):
    """ datatable z3cform widget for multple kinds of subforms.
    uses a list of (id,formid,json) objects
    """

    _converter = SubformWidgetConverter

    implementsOnly(ISubformWidget)

    def update(self):
        super(SubformWidget, self).update()
        self.subform = 'send-to-mail'
        self.raw = json.dumps(self.value if self.value else [])
        self.columns = ["Title"]
        self.fields = ['title']

        # TODO: means helper has no access to local db. We probably needs to fix
        # this so it can introspect it
        OPEN_URL = "{path}/{formid}/OpenForm?ajax_load=1"+\
            "&Plomino_Parent_Field=__dummy__"+\
            "&Plomino_Parent_Form={formid}"+\
            "&Plomino_Macro_Context={curpath}"
        helpers = self.helper_forms()
        obj = self.context
        # if IPlominoForm.providedBy(obj):
        #     curform = obj
        #     curfieldid = ''
        # else:
        #     curfieldid = obj.id
        #     curform = obj.getParentNode()
        # curpath = '/'.join(curform.getParentNode().getPhysicalPath())
        curpath = '/'.join(obj.getPhysicalPath())
        self.form_urls = [dict(url=OPEN_URL.format(formid=id,
                                                   path=path,
                                                   curpath=curpath),
                               id=id,
                               title=title)
                          for title,id,path in helpers]
        self.form_urls = json.dumps(self.form_urls)

        self.rendered = []
        if self.value is not None:
            for row in self.value:
                self.rendered.append([row[c] for c in self.fields if c in row])
        self.rendered = json.dumps(self.rendered)
        # TODO: need to run through each form to get rendered values


    def extract(self, default=NO_VALUE):
        value = super(SubformWidget, self).extract(default)
        raw = json.loads(value) if value and value != default else default
        return raw

    def helper_forms(self):
        db = self.context.getParentDatabase()
        found = set()
        for path in db.import_macros:
            if path == ".":
                db_import = db
            else:
                db_import = db.restrictedTraverse(path)
            for form in db_import.getForms():
                typename = self.context.getPortalTypeName().lstrip("Plomino").lower()
                if form.id.startswith("helper_"+typename) or form.id.startswith("macro_"+typename):
                    if form.id in found:
                        continue
                    found.add(form.id)
                    yield (form.Title(), form.id, path)


@provider(IFormFieldProvider)
class IHelpers(model.Schema):
    """Add a helpers widget to plomino objects with formulas
    """

    directives.widget('helpers', SubformWidget)
    directives.order_after(helpers = 'IBasic.description')
    helpers = schema.List(value_type=schema.Dict(),
                          title=u"Formula Macros",
                          description=u"Macros can be applied from your macro library and will automate formulas for you.",
                          required=False
    )

@implementer(IHelpers)
#@adapter(IPlominoForm)
# @adapter(IPlominoField)
# @adapter(IPlominoHidewhen)
# @adapter(IPlominoAction)
# @adapter(IPlominoView)
class Helpers(object):
    """Add a field for storing helpers on
    """

    def __init__(self, context):
        self.context = context

    @property
    def helpers(self):
        return self.context.helpers

    @helpers.setter
    def helpers(self, value):
        if value is None:
            value = []
        self.context.helpers=value
        #TODO: only called if the value has changed. So won't regenerate on every save
        # update_helpers(self.context, None)



# Event handler
def update_helpers(obj, event):
    """Update all the formula fields based on our helpers
    """

    if not hasattr(obj, 'helpers'):
        return
    helpers = obj.helpers
    fields = getFieldsInOrder(obj.getTypeInfo().lookupSchema())
    fields += [field for behaviour in IBehaviorAssignable(obj).enumerateBehaviors()
               for field in getFieldsInOrder(behaviour.interface)]

    if helpers is None:
        return

    for helper in helpers:
        formid = helper.get('_datagrid_formid_', None)
        if formid is None:
            continue
        db = obj.getParentDatabase()
        # search other dbs for this form
        form = None
        db_import = None
        for db_path in db.import_macros:
            if db_path == '.':
                db_import = db
            else:
                db_import = db.restrictedTraverse(db_path)
            form = db_import.getForm(formid)
            if form is not None:
                break
        if form is None:
            # TODO: shouldn't silently fail
            continue
        helperid = 'blah'


        # if IPlominoForm.providedBy(obj):
        #     curform = obj
        #     curfieldid = ''
        # else:
        #     curfieldid = obj.id
        #     curform = obj.getParentNode()
        curpath = '/'.join(obj.getPhysicalPath())
        form.REQUEST['Plomino_Parent_Field'] = '__dummy__'
        form.REQUEST['Plomino_Parent_Form'] = formid
        form.REQUEST['Plomino_Macro_Context'] = curpath

        doc = getTemporaryDocument(db_import, form, helper).__of__(db_import)
        # has to be computed on save so it appears in the doc
        #TODO this can generate errors as fields calculated. Need to show this
        doc.save(form=form, creation=False, refresh_index=False, asAuthor=True, onSaveEvent=False)

        for id, field in fields:
            #value = getattr(getattr(self., key), 'output', getattr(obj, key)):

            #TODO: if its a formula then wipe any previous generated code
            #TODO: can work out whats a formula from the widget?

            value = None
            names = ['generate_%s'%id.lower(),
                     'generate_%s'%id,
                     '%s'%id,
                     '%s'%id.lower()]
            for name in names:
                if doc.hasItem(name):
                    value = doc.getItem(name)
                    break
            if value is None:
                continue
            dm = getMultiAdapter((obj, field), IDataManager)
            #code = getattr(obj, id)
            code = dm.get()
            #TODO: what if the id has changed. Should redo all gen code?
            fmt = '### START {id} ###{code}### END {id} ###'
            reg_code = re.compile(fmt.format(id=helperid, code='((.|\n|\r)+)'))
            if not code or not reg_code.search(code):
                code = (code + u'\n') if code else u''
                code += fmt.format(id=helperid, code="\n"+value+"\n")
            else:
                repl = fmt.format(id=helperid, code="\n"+value+"\n")
                code = reg_code.sub(repl, code)
            #setattr(obj, id, code)
            dm.set(code)

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
from Products.CMFPlomino.utils import asAscii

from Products.CMFCore.interfaces import IDublinCore
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from ..config import SCRIPT_ID_DELIMITER, FIELD_MODES, FIELD_TYPES

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
        typename = self.context.getPortalTypeName().lstrip("Plomino").lower()
        thistype = self.context.field_type if typename == 'field' else None
        prefixes = ["macro_%s_%s_"%(typename,f.lower()) for f in FIELD_TYPES.keys() if f != thistype]

        dbs = []
        for path in db.import_macros:
            ## restrictedTraverse only ascii path, can't be unicode
            path = asAscii(path)
            if path == '.':
                dbs.append(db)
            else:
                dbs.append(db.restrictedTraverse(path))

        for form in [form for db in dbs for form in db.getForms()]:
            if form.id in found:
                continue
            if not form.id.startswith("macro_%s_"%typename):
                continue
            if any([p for p in prefixes if form.id.startswith(p)]):
                # it's got a prefix for another field type
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

MACRO_FMT = '### START {id} ###{code}### END {id} ###'
CODE_REGEX = '(((?!###)(.|\n|\r))+)'

# Event handler
def update_helpers(obj, event):
    """Update all the formula fields based on our helpers
    """

    if not hasattr(obj, 'helpers'):
        return
    helpers = obj.helpers


    if helpers is None:
        return

    ids = {m['_macro_id_'] for m in helpers if '_macro_id_' in m}

    macros = []

    # TODO: Need to remove any code the user removed

    for helper in obj.helpers:
        formid = helper.get('Form', None)
        if formid is None:
            continue
        db = obj.getParentDatabase()
        # search other dbs for this form
        form = None
        db_import = None
        for db_path in db.import_macros:
            ## restrictedTraverse only ascii path, can't be unicode
            db_path = asAscii(db_path)
            if db_path == '.':
                db_import = db
            else:
                db_import = db.restrictedTraverse(db_path)
            form = db_import.getForm(formid)
            if form is not None:
                break

        # ensure the macros have unique ids so
        helperid = helper.get('_macro_id_')
        if not helperid:
            i = 1
            while not helperid or helperid in ids:
                helperid = "{formid}_{i}".format(formid=formid, i=i)
                i+=1
            helper['_macro_id_'] = helperid
            ids.add(helperid)

        if form is None:
            # means the macro used to create the code is no longer available
            # we will retain the code but it will no longer get updated
            macros.append( (helperid, None, None) )
            #obj.helpers = helpers
            continue


        curpath = '/'.join(obj.getPhysicalPath())
        form.REQUEST['Plomino_Parent_Field'] = '__dummy__'
        form.REQUEST['Plomino_Parent_Form'] = formid
        form.REQUEST['Plomino_Macro_Context'] = curpath

        doc = getTemporaryDocument(db_import, form, helper).__of__(db_import)
        # has to be computed on save so it appears in the doc
        #TODO this can generate errors as fields calculated. Need to show this
        doc.save(form=form, creation=False, refresh_index=False, asAuthor=True, onSaveEvent=False)
        macros.append( (helperid, form, doc) )

    fields = []
    behaviours = [b.interface for b in IBehaviorAssignable(obj).enumerateBehaviors()]
    for schema in [obj.getTypeInfo().lookupSchema()] + behaviours:
        hints = schema.queryTaggedValue(u'plone.autoform.widgets',{}).items()
        formulas = {id for id, hint in hints if hint.params.get('klass') == 'plomino-formula'}
        fields += [(id,field) for id, field in getFieldsInOrder(schema) if id in formulas]

    for id, field in fields:

        dm = getMultiAdapter((obj, field), IDataManager)
        code = dm.get()
        code = code if code else u''

        all_code = re.compile(MACRO_FMT.format(id='([^ #]+)',code=CODE_REGEX))
        old_codes = [(m[0],m[1]) for m in re.findall(all_code, code)]
        old_codes.reverse()


        names = ['generate_%s'%id.lower(),
                 'generate_%s'%id,
                 '%s'%id,
                 '%s'%id.lower()]
        new_code = {}
        for macro_id, form, doc in macros:
            if form is None:
                new_code[macro_id] = None
                continue
            value = None
            for value in (doc.getItem(name) for name in names if doc.hasItem(name)):
                break
            if value is None:
                continue
            new_code[macro_id] = value

        for macro_id, form, doc in macros:
            if macro_id not in new_code:
                continue
            code_id, old_code = old_codes[-1] if old_codes else (None,None)
            # 1. it's in right position. replace it
            if macro_id == code_id:
                old_codes.pop()
                if new_code[macro_id] is None:
                    # macro has gone missing. Leave the code alone
                    continue

                code = re.sub("(%s)"%MACRO_FMT.format(id=macro_id, code=CODE_REGEX),
                              MACRO_FMT.format(id=macro_id, code="\n"+new_code[macro_id]+"\n"),
                              code, 1)
            # 2. it's not in the list. remove it
            elif code_id and code_id not in new_code:
                code = re.sub("(%s)"%MACRO_FMT.format(id=code_id, code=CODE_REGEX),
                              "",
                              code)
                old_codes.pop()
            elif new_code[macro_id] is None:
                # macro has gone missing. leave it alone
                continue
            elif code_id is None:
                # reached end. insert code at the end
                code += '\n'+MACRO_FMT.format(id=macro_id, code="\n"+new_code[macro_id]+"\n")

            else:
                # 3. it's further down the list. remove it
                code = re.sub("(%s)"%MACRO_FMT.format(id=macro_id, code=CODE_REGEX),
                              "",
                              code)
                old_codes = [(oid, ocode) for oid,ocode in old_codes if macro_id != oid]
                # 4. The list one is new. insert it. or we are moving it
                # insert before the current one
                switched = MACRO_FMT.format(id=macro_id, code="\n"+new_code[macro_id]+"\n") + \
                    '\n' + \
                    MACRO_FMT.format(id=code_id, code=old_code)
                code = re.sub("(%s)"%MACRO_FMT.format(id=code_id, code=CODE_REGEX),
                              switched,
                              code, 1)

        for code_id, old_code in old_codes:
            # remove any code that's left
            code = re.sub(MACRO_FMT.format(id=code_id, code=CODE_REGEX),
                          "",
                          code)


        dm.set(code)
        obj.helpers = helpers

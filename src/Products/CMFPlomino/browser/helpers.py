import json
import logging
import re

from plone.behavior.interfaces import IBehaviorAssignable
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IWidget, NO_VALUE, IDataManager
from z3c.form.widget import Widget
from zope import schema
from zope.component import adapts, getMultiAdapter
from zope.interface import implementsOnly
from zope.schema.interfaces import IList

from zope.schema import getFieldsInOrder
from Products.CMFPlomino.document import getTemporaryDocument
from Products.CMFPlomino.utils import asAscii

from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import implementer
from zope.interface import provider
from ..config import SCRIPT_ID_DELIMITER, FIELD_MODES, FIELD_TYPES

logger = logging.getLogger('Plomino')

__author__ = 'dylanjay'


class IMacroWidget(IWidget):
    """ Widget for collecting data from a list of possible subforms
    """


class MacroWidgetConverter(BaseDataConverter):
    """Convert single json input into list"""

    adapts(IList, IMacroWidget)

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


class MacroWidget(Widget):
    """ datatable z3cform widget for multple kinds of subforms.
    uses a list of (id,formid,json) objects
    """

    _converter = MacroWidgetConverter

    implementsOnly(IMacroWidget)

    def update(self):
        logger.debug('Method: Widget update')
        super(MacroWidget, self).update()
        self.rules = json.dumps(self.value if self.value else [])

        # TODO: means helper has no access to local db. We probably needs to fix
        # this so it can introspect it
        OPEN_URL = "{path}/{formid}/OpenForm?ajax_load=1"+\
            "&Plomino_Parent_Field=__dummy__"+\
            "&Plomino_Parent_Form={formid}"+\
            "&Plomino_Macro_Context={curpath}"
        helpers = self.helper_forms()
        obj = self.context
        curpath = '/'.join(obj.getPhysicalPath())
        groups = {}
        macros = [dict(url=OPEN_URL.format(formid=id,
                                           path=path,
                                           curpath=curpath) if path[0]!= '#' else path,
                               id=id,
                               title=title,
                               group=group)
                          for title,id,path,group in helpers]
        for macro in macros:
            groups.setdefault(macro['group'],[]).append(macro)
        self.form_urls = json.dumps(groups)


    def extract(self, default=NO_VALUE):
        logger.debug('Method: Widget extract')
        value = super(MacroWidget, self).extract(default)
        if value == default:
            return default
        res = []
        for rule in value:
            # rule is a json encoded list of dicts or single dict
            if not rule.strip():
                continue
            rule = [json.loads(r) for r in rule.split('\t')]
            #rule = json.loads(u"[%s]"%rule)
            #TODO: strip out _authenticator and other gumf
            res.append(rule)
        return res

    def helper_forms(self):
        logger.debug('Method: Widget helper_forms')
        db = self.context.getParentDatabase()
        found = set()
        view = self.request.URL.rsplit('/',1)[-1]
        if view.startswith('++add++'):
            typename = view.lstrip('++add++Plomino').lower()
            thistype = None #TODO: we need to change it based on the currently selected type
        else:
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
                try:
                    dbs.append(db.restrictedTraverse(path))
                except KeyError:
                    #TODO: maybe improve import so bad macro imports aren't stored?
                    continue

        forms = []
        for _db in dbs:
            forms.extend(_db.getForms())

        for form in forms:
            if form.id in found:
                continue
            if not any([form.id.startswith(p) for p in ["macro_condition_", "macro_if_", "macro_%s_"%typename]]):
                continue
            if any([form.id.startswith(p) for p in prefixes]):
                # it's got a prefix for another field type
                continue
            found.add(form.id)
            group = 'if' if any([form.id.startswith(p) for p in ["macro_condition_", "macro_if_"]]) else 'do'
            yield (form.Title(), form.id, path, group)
        yield ('And', 'and', '#and', 'logic')
        yield ('Or', 'or', '#or', 'logic')
        yield ('Not', 'not', '#not', 'logic')


@provider(IFormFieldProvider)
class IHelpers(model.Schema):
    """Add a helpers widget to plomino objects with formulas
    """

    directives.widget('helpers', MacroWidget)
    directives.order_after(helpers = 'IBasic.description')
    helpers = schema.List(
        value_type=schema.List(
            value_type=schema.Dict(
                title=u"Macro Instance",
            ),
            title=u"Rule",
        ),
        title=u"Code Builder",
        description=u"Rules for Submission, validation, prepopulation",
        required=False
    )

@implementer(IHelpers)
class Helpers(object):
    """Add a field for storing helpers on
    """

    def __init__(self, context):
        logger.debug('Method: init helpers')
        self.context = context

    @property
    def helpers(self):
        logger.debug('Method: get helpers')
        return self.context.helpers

    @helpers.setter
    def helpers(self, value):
        logger.debug('Method: set helpers')
        if value is None:
            value = []
        self.context.helpers=value

MACRO_FMT = '### START {id} ###{code}### END {id} ###'
CODE_REGEX = '(((?!###)(.|\n|\r))+)'


def load_macro(formid, helper, db, ids, curpath):
    # search other dbs for this form
    form = None
    db_import = None
    for db_path in db.import_macros:
        # restrictedTraverse only ascii path, can't be unicode
        db_path = asAscii(db_path)
        if db_path == '.':
            db_import = db
        else:
            db_import = db.restrictedTraverse(db_path)
        form = db_import.getForm(formid)
        if form is not None:
            break

    # ensure the macros have '_macro_id_' is unique ids so
    helperid = helper.get('_macro_id_')
    if not helperid:
        i = 1
        while not helperid or helperid in ids:
            helperid = "{formid}_{i}".format(formid=formid, i=i)
            i += 1
        helper['_macro_id_'] = helperid
        ids.add(helperid)

    if not form:
        return (helperid, None, None)

    form.REQUEST['Plomino_Parent_Field'] = '__dummy__'
    form.REQUEST['Plomino_Parent_Form'] = formid
    form.REQUEST['Plomino_Macro_Context'] = curpath

    doc = getTemporaryDocument(db_import, form, helper).__of__(db_import)
    # has to be computed on save so it appears in the doc
    # make sure all the fields must be in the form layout
    # including hidden fields that contains macro code
    # TODO: this can generate errors as fields calculated. Need to show this
    doc.save(form=form, creation=False, refresh_index=False, asAuthor=True, onSaveEvent=False)
    logger.info(
        'helper id: %s generate temp doc with form: %s has items: %s' %
        (helperid, formid, doc.items))


    return (helperid, form, doc)

def get_formulas(obj):
    # list all the fields from this obj that can be inserted
    fields = []
    behaviours = [b.interface for b in IBehaviorAssignable(obj).enumerateBehaviors()]
    for schema in [obj.getTypeInfo().lookupSchema()] + behaviours:
        hints = schema.queryTaggedValue(u'plone.autoform.widgets', {}).items()
        formulas = {id for id, hint in hints if hint.params.get('klass') == 'plomino-formula'}
        fields += [(id, field) for id, field in getFieldsInOrder(schema) if
                   id in formulas]
    return fields

# Event handler
def update_helpers(obj, event):
    """Update all the formula fields based on our helpers
    """
    logger.debug('Method: update_helpers')

    if not hasattr(obj, 'helpers'):
        return

    # helpers is a list of rules and each rule is a list of macro dict that contains 'Form', 'title',
    # '_macro_id_' and all the field ids in that macro form.
    helpers = obj.helpers

    if helpers is None:
        return

    db = obj.getParentDatabase()
    curpath = '/'.join(obj.getPhysicalPath())

    # need to upgrade the data from the old structure if needed
    #TODO: only do set at the end if this has changed (or an id has been added)
    helpers = [[rule] if type(rule) == dict else rule for rule in helpers]


    # find all our ids so we can add unique ones later
    ids = {m['_macro_id_'] for rule in helpers for m in rule if '_macro_id_' in m}

    # TODO: Need to remove any code the user removed

    # This loop is mainly generate list of macros with
    # helper id, form obj and temp macro doc
    # need to do this first to determine which formulas a given macro wants to modify
    # rules = [([condition_macro,...),(action_macro,...),...]
    # and a macro is (helperid, form, doc)
    rules = []
    for rule in helpers:
        macros = []
        conditions = []
        rules.append( (conditions, macros) )
        for helper in rule:
            formid = helper.get('Form', None)
            if formid is None:
                continue
            if any([formid.lower() == p for p in ['or','and','not']]):
                conditions.append((formid, None, None))
                continue

            helperid, form, doc = load_macro(formid, helper, db, ids, curpath)

            if form is None:
                # means the macro used to create the code is no longer available
                # we will retain the code but it will no longer get updated
                macros.append((helperid, None, None))
                continue

            # TODO: should conditions be able to target form vs field?
            if any([formid.lower().startswith(p) for p in ['macro_condition_','macro_if_']]):
                conditions.append((helperid, form, doc))
            else:
                macros.append((helperid, form, doc))


    for id, field in get_formulas(obj):

        names = ['generate_%s' % id.lower(),
                 'generate_%s' % id,
                 '%s' % id,
                 '%s' % id.lower()]

        # find all ids in 'names' list in temp doc and
        # pull new macro code from that temp doc and
        # put into new_code dict
        new_code = {}
        for conditions, macros in rules:
            matched = False
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
                matched = True
            # if any macros then matched then we need to add the conditions
            if not (matched and conditions):
                continue

            for macro_id, form, doc in conditions:
                if doc is None:
                    # it's and.or,not
                    continue
                formula = doc.getItem('formula').strip()
                if not formula:
                    logger.warning('Macro condition id: %s has no value for "formula"' % macro_id)
                    continue
                code = "def {macro_id}():\n".format(macro_id=macro_id) #TODO: should use title or form.name to make it more readable?
                code += (' '*4)+('\n'+(' '*4)).join(doc.getItem('formula').split('\n')) #indent
                new_code[macro_id] = code + '\n'
            # adjust macros to use conditions
            for macro_id, form, doc in macros:
                if macro_id not in new_code:
                    continue
                last_cond = 'and'
                expression = []
                is_op = lambda id: id in ['and', 'or', 'not']
                for cond_id, _, _ in conditions:
                    if not is_op(cond_id) and is_op(last_cond):
                        expression.append('{id}()'.format(id=cond_id))
                    elif cond_id in ['and','or'] and not is_op(last_cond):
                        expression.append('{op}'.format(op=cond_id))
                    elif cond_id == 'not' and (not is_op(last_cond) or last_cond=='not') :
                        expression.append('not')
                    else:
                        # invalid statement
                        logger.warning('Macro expression invalid %s"' % ' '.join(expression+[cond_id]))
                    last_cond = cond_id

                if expression and is_op(expression[-1]):
                    logger.warning('Macro expression invalid %s"' % ' '.join(expression))
                    expression = expression[:-1]
                if len(expression) == 0:
                    continue

                new_code[macro_id] = "if {expression}:\n{code}\n".format(
                    expression = (' '.join(expression)),
                    code = (' '*4)+('\n'+(' '*4)).join(new_code[macro_id].split('\n')) #indent
                )
                #TODO: we should add the condition line just once at the first condition

        # replace old macro code with new macro code
        dm = getMultiAdapter((obj, field), IDataManager)
        # code is the current code from the field in that obj
        code = dm.get()
        code = code if code else u''

        # old_codes contains old macro code in the current code from the
        # field in that obj
        all_code = re.compile(MACRO_FMT.format(id='([^ #]+)', code=CODE_REGEX))
        old_codes = [(m[0], m[1]) for m in re.findall(all_code, code)]
        old_codes.reverse()
        for macro_id, form, doc in [m for conditions,macros in rules for m in conditions+macros]:
            if macro_id not in new_code: # doesn't gen code for this formula
                continue
            code_id, old_code = old_codes[-1] if old_codes else (None, None)
            # 1. it's in right position. replace it
            if macro_id == code_id:
                old_codes.pop()
                if new_code[macro_id] is None:
                    # macro has gone missing. Leave the code alone
                    continue

                code = re.sub(
                    "(%s)" % MACRO_FMT.format(id=macro_id, code=CODE_REGEX),
                    MACRO_FMT.format(id=macro_id, code="\n" + new_code[macro_id] + "\n"),
                    code,
                    1)
            # 2. it's not in the list. remove it
            elif code_id and code_id not in new_code:
                code = re.sub(
                    "(%s)" % MACRO_FMT.format(id=code_id, code=CODE_REGEX),
                    "",
                    code)
                old_codes.pop()
            elif new_code[macro_id] is None:
                # macro has gone missing. leave it alone
                continue
            elif code_id is None:
                # reached end. insert code at the end
                code += '\n'+MACRO_FMT.format(
                    id=macro_id,
                    code="\n"+str(new_code[macro_id])+"\n")
            else:
                # 3. it's further down the list. remove it
                code = re.sub(
                    "(%s)" % MACRO_FMT.format(id=macro_id, code=CODE_REGEX),
                    "",
                    code)
                old_codes = [(oid, ocode) for oid, ocode in old_codes if
                             macro_id != oid]
                # 4. The list one is new. insert it. or we are moving it
                # insert before the current one
                switched = MACRO_FMT.format(
                    id=macro_id,
                    code="\n"+str(new_code[macro_id])+"\n") + \
                    '\n' + \
                    MACRO_FMT.format(id=code_id, code=old_code)
                code = re.sub(
                    "(%s)" % MACRO_FMT.format(id=code_id, code=CODE_REGEX),
                    switched,
                    code,
                    1)

        for code_id, old_code in old_codes:
            # remove any code that's left
            code = re.sub(
                MACRO_FMT.format(id=code_id, code=CODE_REGEX),
                "",
                code)

        logger.info(
            'Macro code with id: %s is inserted in %s obj. Code: %s...' %
            (id, obj.id, code[:50]))
        # TODO: should not insert code that not changed or don't use macro
        dm.set(code)
        obj.helpers = helpers

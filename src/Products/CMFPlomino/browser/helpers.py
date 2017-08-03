import json
import logging
from Products.Five import BrowserView
from ZPublisher.Client import NotFound
import re

from plone.behavior.interfaces import IBehaviorAssignable
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IWidget, NO_VALUE, IDataManager
from z3c.form.widget import Widget
from zope import schema
from zope.component import adapts, getMultiAdapter
from zope.interface import implementsOnly, alsoProvides
from zope.schema.interfaces import IList

from zope.schema import getFieldsInOrder
from Products.CMFCore.utils import getToolByName
from Products.CMFPlomino.document import getTemporaryDocument
from Products.CMFPlomino.utils import asAscii

from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.interface import implementer
from zope.interface import provider
from ..config import SCRIPT_ID_DELIMITER, FIELD_MODES, FIELD_TYPES
import plone.api

logger = logging.getLogger('Plomino')

__author__ = 'dylanjay'




###########################################
# A multi line rule widget based on select2
###########################################

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
        rules = self.value if self.value is not None else []
        # have to deal with old style macors which and list of dicts, not list of list of dicts
        rule_as_input = lambda rule: '\t'.join([json.dumps(macro) for macro in rule])
        self.rules = [rule_as_input(rule if type(rule)==list else [rule]) for rule in rules]
        # We always need an empty rule at the end
        self.rules.append("")

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
            rule = [json.loads(r) for r in rule.split('\t') if r.strip() != ""]
            #rule = json.loads(u"[%s]"%rule)
            #TODO: strip out _authenticator and other gumf
            res.append(rule)
        return res

    def helper_forms(self):
        db = self.context.getParentDatabase()
        catalog = getToolByName(db, 'portal_catalog')
        found = set()
        view = self.request.URL.rsplit('/',1)[-1]
        if view.startswith('++add++'):
            typename = remove_prefix(view,'++add++Plomino').lower()
            thistype = None #TODO: we need to change it based on the currently selected type
        else:
            typename = remove_prefix(self.context.getPortalTypeName(),"Plomino").lower()
            thistype = self.context.field_type if typename == 'field' else None
        prefixes = ["macro_%s_%s_"%(typename,f.lower()) for f in FIELD_TYPES.keys() if f != thistype]

        dbs = []
        for path in db.getImportMacros():
            ## restrictedTraverse only ascii path, can't be unicode
            path = asAscii(path)
            if path == '.':
                dbs.append(db)
            elif '/' in path:
                # backward compatible to support path
                try:
                    dbs.append(db.restrictedTraverse(path))
                except KeyError:
                    #TODO: maybe improve import so bad macro imports aren't stored?
                    continue
            else:
                # only current db using '.', the rest is db id
                brains = catalog(getId=path)
                for brain in brains:
                    if brain.portal_type != 'PlominoDatabase':
                        continue
                    try:
                        db_brain = brain.getObject()
                        dbs.append(db_brain)
                    except KeyError:
                        # TODO: maybe improve import so bad macro imports aren't stored?
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
            form_path = form.getParentDatabase().absolute_url()
            yield (form.Title(), form.id, form_path, group)
        yield ('And', 'and', '#and', 'logic')
        yield ('Or', 'or', '#or', 'logic')
        yield ('Not', 'not', '#not', 'logic')


@provider(IFormFieldProvider)
class IHelpers(model.Schema):
    """Add a helpers widget to plomino objects with formulas
    """

    directives.widget('helpers', MacroWidget)
    directives.order_after(helpers = '*')
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
        self.context = context

    @property
    def helpers(self):
        return self.context.helpers

    @helpers.setter
    def helpers(self, value):
        if value is None:
            value = []
        self.context.helpers=value



#######################################################
# subscriber for updating formulas based on macro rules
#######################################################

MACRO_FMT = '### START {id} ###{code}### END {id} ###'
CODE_REGEX = '(((?!###)(.|\n|\r))+)'


def load_macro(formid, helper, db, ids, curpath):
    catalog = getToolByName(db, 'portal_catalog')
    # search other dbs for this form
    form = None
    db_import = None

    for db_path in db.getImportMacros():
        # restrictedTraverse only ascii path, can't be unicode
        db_path = asAscii(db_path)
        if db_path == '.':
            db_import = db
            form = db_import.getForm(formid)
        elif '/' in db_path:
            # backward compatible to support path
            db_import = db.restrictedTraverse(db_path)
            form = db_import.getForm(formid)
        else:
            # only current db using '.', the rest is db id
            brains = catalog(getId=db_path)
            for brain in brains:
                if brain.portal_type != 'PlominoDatabase':
                    continue
                db_import = brain.getObject()
                form = db_import.getForm(formid)
                if form is not None:
                    break
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
    #logger.info(
    #    'helper id: %s generate temp doc with form: %s has items: %s' %
    #    (helperid, formid, doc.items))


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


def generate_all_code(obj, helpers):
    """
    # This loop is mainly generate list of macros with
    # helper id, form obj and temp macro doc
    # need to do this first to determine which formulas a given macro wants to modify
    # return rules = [([condition_macro,...),(action_macro,...),...]
    # and a macro is (helperid, form, doc)
    """
    db = obj.getParentDatabase()

    # find all our ids so we can add unique ones later
    ids = {m['_macro_id_'] for rule in helpers for m in rule if '_macro_id_' in m}
    curpath = '/'.join(obj.getPhysicalPath())


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

            helperid, form, doc = load_macro(formid, helper, db, ids,
                                             curpath)

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

    return rules

def formulas_to_add_code(obj, rules):

    for id, field in get_formulas(obj):

        names = ['generate_%s' % id.lower(),
                 'generate_%s' % id,
                 '%s' % id,
                 '%s' % id.lower()]

        # find all ids in 'names' list in temp doc and
        # pull new macro code from that temp doc and
        # put into new_code dict
        new_code = {}
        matched_rules = []
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
                matched_rules.append( (conditions, macros) )
        yield id, field, matched_rules, new_code

def add_conditions_to_code(rules, new_code):
    for conditions, macros in rules:
        if not(conditions):
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
                elif not is_op(cond_id) and not is_op(last_cond):
                    # if no op then default to and
                    expression.append('and')
                    expression.append('{id}()'.format(id=cond_id))
                elif cond_id == 'not':
                    expression.append('not')
                else:
                    #TODO: need to warn the user
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
    return new_code

def update_macro_code(code, rules, new_code):

    # old_codes contains old macro code in the current code from the
    # field in that obj
    all_code = re.compile(MACRO_FMT.format(id='([^ #]+)', code=CODE_REGEX))
    old_codes = [(m[0], m[1]) for m in re.findall(all_code, code)]
    old_codes.reverse()
    new_codes = [m for conditions,macros in rules for m in conditions+macros]
    new_codes.reverse()
    changes_log = []

    while len(new_codes) > 0:

        macro_id, form, doc = new_codes[-1]

        if macro_id not in new_code: # doesn't gen code for this formula
            changes_log.append( (macro_id, "skipped: no code") )
            new_codes.pop()
            continue
        code_id, old_code = old_codes[-1] if old_codes else (None, None)
        # 1. it's in right position. replace it
        if macro_id == code_id:
            old_codes.pop()
            new_codes.pop()
            if new_code[macro_id] is None:
                # macro has gone missing. Leave the code alone
                changes_log.append( (macro_id, "skipped: no code") )
                continue

            code = re.sub(
                "(%s)" % MACRO_FMT.format(id=macro_id, code=CODE_REGEX),
                MACRO_FMT.format(id=macro_id, code="\n" + new_code[macro_id] + "\n"),
                code,
                1)
            changes_log.append( (macro_id, "replaced") )
        # 2. it's not in the list. remove it
        elif code_id and code_id not in new_code:
            changes_log.append( (code_id, "removed %s") )
            code = re.sub(
                "(%s)" % MACRO_FMT.format(id=code_id, code=CODE_REGEX),
                "",
                code)
            old_codes.pop()
        elif new_code[macro_id] is None:
            new_codes.pop()
            changes_log.append( (macro_id, "skipped: no code") )
            # macro has gone missing. leave it alone
            continue
        elif code_id is None:
            new_codes.pop()
            # reached end. insert code at the end
            changes_log.append( (macro_id, "inserting at end") )
            code += '\n'+MACRO_FMT.format(
                id=macro_id,
                code="\n"+str(new_code[macro_id])+"\n")
        else:
            new_codes.pop()
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
            changes_log.append( (macro_id, "insert before %s" % code_id) )

    for code_id, old_code in old_codes:
        # remove any code that's left
        code = re.sub(
            MACRO_FMT.format(id=code_id, code=CODE_REGEX),
            "",
            code)
        changes_log.append( (code_id, "removed") )
    logger.debug( str(changes_log) )

    return code


# Event handler
def update_helpers(obj, event):
    """Update all the formula fields based on our helpers
    """
    if not hasattr(obj, 'helpers'):
        return

    # helpers is a list of rules and each rule is a list of macro dict that contains 'Form', 'title',
    # '_macro_id_' and all the field ids in that macro form.
    helpers = obj.helpers

    if helpers is None:
        return

    # need to upgrade the data from the old structure if needed
    #TODO: only do set at the end if this has changed (or an id has been added)
    helpers = [[rule] if type(rule) != list else rule for rule in helpers]
    rules = generate_all_code(obj, helpers)

    for id, field, matched_rules, new_code in formulas_to_add_code(obj, rules):
        add_conditions_to_code(matched_rules, new_code)

        # replace old macro code with new macro code
        dm = getMultiAdapter((obj, field), IDataManager)
        # code is the current code from the field in that obj
        code = dm.get()
        code = code if code else u''

        code = update_macro_code(code, matched_rules, new_code)

        # TODO: should not insert code that not changed or don't use macro
        if dm.get() != code:
            #logger.debug(
            #    'Macro code with id: %s is inserted in %s obj. Code: %s..., old: %s...' %
            #    (id, obj.id, code[:50], dm.get()[:50] if dm.get() else dm.get()))
            dm.set(code)
        obj.helpers = helpers

######################################
# View for template handling REST api
######################################

class MacroTemplateView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.form = self.context

    def listTemplates(self):
        db = self.context.getParentDatabase()
        found = set()

        dbs = []
        for path in db.getImportMacros():
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
            forms.extend(_db.getForms(sortbyid=False))

        res = []
        for form in forms:
            if form.id in found:
                continue
            if not any([form.id.startswith(p) for p in ["template_"]]):
                continue
            found.add(form.id)
            group = '' # not sure if we will use groups in the palette

            contents = []
            for id in set(form.objectIds()):
                item = form[id]
                example = form.example_widget(id=id)
                contents.append({'id':id, 'old_id':id, 'title':item.title,
                                 'layout': example})

            res.append( {'title':form.Title(),
                         'id':form.id,
#                         'path':path,
                         'group':group,
                         'description':form.description,
                         'layout': form.form_layout, # Used while dragging
                         'group_contents': contents
                    }
            )
        self.request.RESPONSE.setHeader(
            'content-type', 'text/plain; charset=utf-8')
        return json.dumps(res)

    def addTemplate(self):
        """ api to insert a template into the form.
        """
        self.request.RESPONSE.setHeader(
            'content-type', 'text/plain; charset=utf-8')
        #if self.request.method != "POST":
        #    raise BadRequest("Must be a POST")

        alsoProvides(
            self.request, plone.protect.interfaces.IDisableCSRFProtection)
        templateid = self.request.id
        #data = json.loads(self.request.BODY)

        db = self.context.getParentDatabase()
        curpath = '/'.join(self.context.getPhysicalPath())

        # take the id of the template. prefix it to every contained object.
        # see if any fields already exist
        # if exists, add a number
        # make a copy of each object
        # return the html (replacing with the new ids).
        ids = set([])
        helperid, form, doc = load_macro(templateid, {}, db, ids, curpath)
        if form is None:
            raise NotFound #("No template found for %s"%templateid)
        res = self._renameGroup(form,
                                groupid=remove_prefix(templateid,'template_'),
                                ids=form.objectIds())
        res['layout'] = form.form_layout
        return json.dumps(res)

    def renameGroup(self):
        self.request.RESPONSE.setHeader(
            'content-type', 'text/plain; charset=utf-8')
        #if self.request.method != "POST":
        #    raise BadRequest("Must be a POST")

        alsoProvides(
            self.request, plone.protect.interfaces.IDisableCSRFProtection)
        id = self.request.id
        newid = self.request.newid
        group_contents = self.request.group_contents
        return json.dumps(self._renameGroup(self.form, newid, group_contents))

    def _renameGroup(self, form, groupid, ids):
        # if form is None it's a rename

        context_ids = set(self.form.objectIds())
        def new_id(gid, id, oldgroupid=groupid):
            # if the id is 'text' and the newgroupid is 'text' and then the new id should be
            # 'text_1' etc, not 'text_1_text'
            id = remove_prefix(id, oldgroupid+'_') if id.startswith(oldgroupid+'_') else remove_prefix(id, oldgroupid)
            return (gid+'_'+id).rstrip('_')

        # find a prefix for all the subitems that is unique
        newgroupid = groupid
        i = 1
        while any(new_id(newgroupid,id) in context_ids for id in ids ):
            newgroupid = "%s_%i" % (groupid, i)
            i += 1

        # now we have a unique prefix. Copy or move all the items
        if form == self.form:
            action = plone.api.content.move
        else:
            action = plone.api.content.copy
        new_contents = []
        for id in ids:
            item = form[id]
            newid = new_id(newgroupid,item.id)
            action(item, self.form, id=newid if newid != id else None)
            example = form.example_widget(id=id)
            new_contents.append({'id':newid, 'old_id':id, 'title':item.title,
                                 'layout':example})


        # TODO now adjust the html of the layout with the new ids and return it

        return {'groupid': newgroupid, 'group_contents':new_contents}


def remove_prefix(s, prefix):
    return s[len(prefix):] if s.startswith(prefix) else s

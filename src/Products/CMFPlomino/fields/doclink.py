# -*- coding: utf-8 -*-

from jsonutil import jsonutil as json
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider, ORDER_KEY
from plone.supermodel import directives, model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from .. import _
from ..config import SCRIPT_ID_DELIMITER
from ..exceptions import PlominoScriptException
from ..utils import asUnicode
from base import BaseField


@provider(IFormFieldProvider)
class IDoclinkField(model.Schema):
    """ Selection field schema
    """

    widget = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Selection list", "SELECT"),
            ("Multi-selection list", "MULTISELECT"),
            ("Embedded view", "VIEW"),
            ("Datagrid","DATAGRID"),
        ]),
        title=u'Widget',
        description=u'Field rendering',
        default="SELECT",
        required=True)

    sourceview = schema.Choice(
        vocabulary='Products.CMFPlomino.fields.vocabularies.get_views',
        title=u'Source view',
        description=u'View containing the linkable documents',
        required=False)

    labelcolumn = schema.TextLine(
        title=u'Label column',
        description=u'View column used as label',
        required=False)

    associated_form = schema.Choice(
        vocabulary='Products.CMFPlomino.fields.vocabularies.get_forms',
        title=u'Associated form',
        description=u'If you want to allow adding documents inplace, select the Form to use (only works for the datagrid widget)',
        required=False)

    form.widget('documentslistformula', klass='plomino-formula')
    documentslistformula = schema.Text(
        title=u'Documents list formula',
        description=u"Formula to compute the linkable documents list "
        "(must return a list of 'label|docid_or_path')",
        required=False)

    separator = schema.TextLine(
        title=u'Separator',
        description=u'Only apply if multiple values will be displayed',
        required=False)

# bug in plone.autoform means order_after doesn't moves correctly
IDoclinkField.setTaggedValue(ORDER_KEY,
                               [('widget', 'after', 'field_type'),
                                ('sourceview', 'after', ".widget"),
                                ('associated_form', 'after', ".sourceview"),
                                ('labelcolumn', 'after', ".associated_form"),
                                ('documentslistformula', 'after', ".labelcolumn"),
                                ('separator', 'after', ".documentslistformula"),
                               ]
)


# really hacky way to get the docid but plomino doesn't have nice api to return it
# or could create empty doc and then save on it?
class fake_response(object):
    docid = None

    def redirect(self, url):
        self.docid = url.split('/')[-1].split('?')[0]

    def getHeader(self, header):
        return None


class fake_request(dict):
    RESPONSE = fake_response()


@implementer(IDoclinkField)
class DoclinkField(BaseField):
    """
    """

    read_template = PageTemplateFile('doclink_read.pt')
    edit_template = PageTemplateFile('doclink_edit.pt')

    def getSelectionList(self, doc):
        """ Return the documents list, format: label|docid_or_path, use
        value is used as label if no label.
        """

        #TODO: Selection for when its a datagrid could be hard. Options
        # 1. Use existing select2 but load json with data from docs.
        #    - on select load the json into the datagrid. (don't remove it from select?)
        #    - combine with add so if search returns none you can still add a new one (last option?)
        #    - make part of datagrid.js so can be used in normal datagrids too
        # 2. Somehow load the data on selection. maybe by using openform popup?
        # 3. Make search work dynamically so only load all the data when selected

        db = self.context.getParentDatabase()

        # if formula available, use formula, else use view entries
        f = self.context.documentslistformula
        if f:
            # if no doc provided (if OpenForm action), we use the PlominoForm
            if doc is None:
                obj = self.context.getParentNode()
            else:
                obj = doc
            try:
                s = self.context.runFormulaScript(
                    SCRIPT_ID_DELIMITER.join(['field',
                        self.context.getParentNode().id,
                        self.context.id,
                        'documentslistformula']),
                    obj,
                    f)
            except PlominoScriptException, e:
                p = self.context.absolute_url_path()
                e.reportError(
                    '%s doclink field selection list formula failed' %
                    self.context.id,
                    path=p + '/getSettings?key=documentslistformula')
                s = None
            if s is None:
                s = []

            # if values not specified, use label as value
            proper = []
            for v in s:
                l = v.split('|')
                if len(l) == 2:
                    proper.append(v)
                else:
                    proper.append(v + '|' + v)
            return proper
        elif self.context.sourceview and self.context.labelcolumn:
            #TODO: should just pick first col as default
            v = self.context.getParentDatabase().getView(self.context.sourceview)
            if not v:
                return []
            label_key = v.getIndexKey(self.context.labelcolumn)
            if not label_key:
                return []
            result = []
            for b in v.getAllDocuments(getObject=False):
                val = getattr(b, label_key, '')
                if not val:
                    val = ''
                result.append(asUnicode(val) + "|" + b.id)
            return result
        else:
            # We will select all documents (with limit)
            result = []
            # TODO: add limit
            query = dict(limit=50) #TODO: not sure if this works
            if self.context.associated_form:
                query['Form'] = self.context.associated_form
            for b in db.getAllDocuments(getObject=False, request_query=query):
                result.append(asUnicode(b.id) + "|" + b.id)
            return result

    def processInput(self, submittedValue):
        """
        """

        #TODO: need to make select widget able to add documents too

        db = self.context.getParentDatabase()


        #TODO should be less hacky way of doing this
        if submittedValue and submittedValue.startswith('['):
            # Assume its json from datagrid.
            submittedValue = json.loads(submittedValue)

        if "|" in submittedValue:
            return submittedValue.split("|")
        else:
            return submittedValue


    def updateDocs(self, value):
        """ find any dicts and either create or update the existing documents accordingly """
        db = self.context.getParentDatabase()
        new_value = []
        if not value:
            return value

        fields,_ = self.getColumns()
        for row in value if isinstance(value, list) else [value]:
            if type(row) != dict:
                # Should be a string with the docid or path
                # TODO: do we need to test it exists?
                new_value.append(row)
            elif 'getId' in row:
                # existing document. update it
                form = db.getForm(row['Form'])
                id  = row['getId']
                db.getDocument(id).saveDocument(fake_request(row))
                new_value.append(id)
            else:
                form = db.getForm(row['Form'])

                request = fake_request(row)
                #TODO What happens if the data is invalid?
                # TODO: more robust way of getting docid
                form.createDocument(request)
                assert request.RESPONSE.docid

                new_value.append(request.RESPONSE.docid)
        # Ensure we return it without a list if the original was not a list
        return new_value if isinstance(value, list) else value[0]


    def tojson(self, datatable, rendered=False):
        "just used for the datagrid to produce a json version for template. Rendered means lists"
        if datatable is None:
            return json.dumps([])
        if rendered:
            fields, _ = self.getColumns()
            return json.dumps([[row[f] for f in fields] for row in datatable])
        return json.dumps(datatable)

    def getDatagrid(self, value):
        """ return a list of dicts which have the field info just for the columns we care about.
        This will be used to render the datagrid and also to will be submitted back as json as the vable
        """

        if value is None:
            return []

        paths = value
        fields,_ = self.getColumns()
        db = self.context.getParentDatabase()



        if getattr(self.context,'sourceview'):
            sourceview = self.context.getParentDatabase().getView(
                self.context.sourceview)
            # Lets reduce down to our paths
            #TODO: this is going to filter by access permissions? if so some might be missing
            if not paths:
                return []
            brains = sourceview.getAllDocuments(getObject=False, only_allowed=True,
                                                request_query={'path':paths})

            datatable = []
            for b in brains:
                doc = b.getObject() #TODO: should be able to get Form without waking up object?
                row = dict(Form=doc.getItem('Form',None), getId=b.id)
                #TODO: we need to return all the data in the doc, for the associated form. Otherwise will get reset.
                # as well as the view metadata.
                for col in fields:
                    key = sourceview.getIndexKey(col)
                    if not key:
                        continue
                    v = getattr(b, key)
                    if not isinstance(v, str):
                        v = unicode(v).encode('utf-8').replace('\r', '')
                    row[col] = (v or '&nbsp;')
                datatable.append(row)
            return datatable

        form = self.getAssociatedForm()

        datatable = []
        for path in paths:
            # HACK just get last part as id. Should do proper traverse. Could be other DB?
            doc = db.getDocument(path.split('/')[-1])
            if doc is None:
                # skip row and save will remove the reference
                continue
            row = dict(Form=doc.getItem('Form', None), getId=doc.getId())
            for key in doc.getItems():
                row[key] = doc.getItem(key)
            datatable.append(row)
        return datatable

        #TODO: handle a datatable when formula (with and without associated_form)

        return []

    def getAssociatedForm(self):
        child_form_id = self.context.associated_form
        if child_form_id:
            db = self.context.getParentDatabase()
            return db.getForm(child_form_id)




    def getColumns(self):
        """ work out which fields to display. Either based on sourceview, or associatedform, or
        based on the formula. return tuple of ([fieldid,..],[label,..])
         """
        #
        field_ids = None
        lists = (['getId'], ['ID'])

        f = self.context.documentslistformula
        if f:
            # TODO: get first result of formula and return fields based on this? but need to cache so not run twice
            # or maybe just rely on associate form and show its fields?
            # or maybe just show the label?
            return lists

        if self.context.sourceview:
            #TODO: for now just show the cols that are based on fields.
            # later we can show calculated cols but have to work out how to show when new row added dynamically
            # col.formula returns a caludated value and will be stored in metadata

            sourceview = self.context.getParentDatabase().getView(
                self.context.sourceview)
            columns = [col for col in sourceview.getColumns()
                    if not col.hidden_column and col.displayed_field]
            _lists =  zip(*[(col.displayed_field, col.title) for col in columns])
            if _lists != []:
                lists = _lists
            return lists

        if self.context.associated_form:

            child_form_id = self.context.associated_form
            if not child_form_id:
                return ""

            db = self.context.getParentDatabase()
            child_form = db.getForm(child_form_id)
            _lists = zip(*[(f.id, f.title) for f in child_form.getFormFields(includesubforms=True)])
            if _lists != []:
                lists = _lists

        # TODO: need some better result if not settings. Should be all data? or just a id?
        return lists


    def getFieldMapping(self):
        fields,_ = self.getColumns()
        return ','.join(fields)

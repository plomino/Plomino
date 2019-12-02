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
from ..utils import PlominoTranslate


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
        title=u'Display Fields',
        description=u'A comma separated list of values to be displayed. '
        u'The first value in this list will be used for search when editng the doclink',
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

    def _getSelectionList(self, doc):
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
        # If not dynamic rendering, then enable caching
        cache_key = "getSelectionList_%s" % (
            hash(self.context))
        if not self.context.isDynamicField:
            cache = db.getRequestCache(cache_key)
            if cache:
                return cache
        result = []

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
            for v in s:
                l = v.split('|')
                if len(l) == 2:
                    result.append(v)
                else:
                    result.append(v + '|' + v)

        # Save to cache if not dynamic rendering
        if not self.context.isDynamicField:
            db.setRequestCache(cache_key, result)
        return result

    def getDocumentDisplay(self,docId):
        db = self.context.getParentDatabase()
        doc = db.getDocument(docId)
        if not doc:
            return ''
        if self.context.sourceview and self.context.labelcolumn:
            v = db.getView(self.context.sourceview)
            label_key = v.getIndexKey(self._getLabelColumnFilterByValue())
            if not label_key:
                return docId
            return getattr(doc, label_key, '')
        elif self.context.labelcolumn:
            label_field_id = self._getLabelColumnFilterByValue()
            return doc.getItem(label_field_id, docId)
        else:
            return docId

    def getFilteredDocuments(self, filter):
        """ Return a JSON list of documents, filtered by id or name.
        """
        if not filter:
            return json.dumps({'results': [], 'total': 0})
        
        MAX_ITEM = 50
        filterDocs = []
        db = self.context.getParentDatabase()

        # If documentlistformula is available, search in that formula
        if self.context.documentslistformula:
            for doc_link in self._getSelectionList(self.context)[:MAX_ITEM]:
                parts = doc_link.split('|')
                if filter in parts[0]:
                    doc = json.loads(parts[1])
                    filterDocs.append({'id': doc['getId'], 'text': parts[0], 'object': doc})
        # If associate form is available, seach in catalog for related documents
        elif self.context.associated_form:
            def getMetadata(brain, prop):
                if prop in brain:
                    return brain[prop]
                doc = brain.getObject()
                return getattr(doc, prop, '')
            index = db.getIndex()
            query = {'SearchableText': '%s*' % filter, 'Form':  self.context.associated_form}
            for brain in index.dbsearch(query,limit=MAX_ITEM):
                if self.context.labelcolumn:
                    val = getMetadata(brain, self._getLabelColumnFilterByValue())
                    if not val:
                        val = brain.id
                else:
                    val = brain.id
                columns, _ = self.getColumns()    
                row = {col:getMetadata(brain, col)  for col in columns}
                row['getId'] =  brain.id
                row['Form'] =  self.context.associated_form
                filterDocs.append({'id':brain.id,'text':val,'object':row} )
        # Otherwise, get result from the view
        elif self.context.sourceview:
            v = self.context.getParentDatabase().getView(self.context.sourceview)
            label_key = v.getIndexKey(self._getLabelColumnFilterByValue())
            if not label_key:
                return []
            for doc in v.getAllDocuments(getObject=False):
                val = getattr(doc, label_key, '')
                if val and filter in val:
                    fields, _ = v.getColumns()
                    row = {col.id:getattr(doc, v.getIndexKey(col)) for col in fields}
                    filterDocs.append({'id': doc.id, 'text': val, 'object':row})

        widget = getattr(self.context, 'widget', None)
        if widget == 'DATAGRID':
            filterDocs.append({'id': 'NEW_DOC','Form': self.context.associated_form, 'text': PlominoTranslate('Add new document', self.context)})
        return json.dumps(
            {'results': filterDocs, 'total': len(filterDocs)})

    def getSelectionIds(self, doc):
        lists = self._getSelectionList(doc)
        rselection = lists.split('|')[-1]
        return [f["getId"] for f in rselection]

    def valueForSelect2(self,doc):
        doc_json = json.loads(doc.tojson())
        doc_json["getId"] = doc.id
        return json.dumps(doc_json)

    def processInput(self, submittedValue):
        """
        """
        # Datagrid widget input: JSON-string of list of document object
        # Selection list input: A single string or list of string, each is a JSON-string of document object
        # Embeded view input: A single string or list of string, each is a path to document
        if submittedValue:
            if isinstance(submittedValue, list):
                rows  = []
                for row in submittedValue:
                    try:
                        row = json.loads(row)
                    except Exception as exc:
                        # 'Input from source view, wchich map to document path
                        pass
                    rows.append(row)
                return rows
            else:
                try:
                    submittedValue = json.loads(submittedValue)
                except Exception as exc:
                    # 'Input from source view, wchich map to document path
                    pass
                return submittedValue
        else:
            return []


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
                new_value.append((row.split('/')[-1]))
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
        return new_value if isinstance(value, list) else new_value[0]

    def fromjson(self, datatable):
        return json.loads(datatable)

    def tojson(self, datatable, rendered=False):
        "just used for the datagrid to produce a json version for template. Rendered means lists"
        if not datatable:
            return json.dumps([])
        if rendered:
            fields, _ = self.getColumns()
            return json.dumps([[row[f] for f in fields if f in row] for row in datatable])
        return json.dumps(datatable)

    def getDatagrid(self, value):
        """ return a list of dicts which have the field info just for the columns we care about.
        This will be used to render the datagrid and also to will be submitted back as json as the vable
        """
        if value is None:
            return []
        # In case of multi page-form, the value is a dictionary
        if type(value)==list and type(value[0]) == dict:
            return value
        paths = (hasattr(value,'split') and [value]) or value
        fields, _ = self.getColumns()
        db = self.context.getParentDatabase()
        datatable = []
        for path in paths:
            # HACK just get last part as id. Should do proper traverse. Could be other DB?
            doc = db.getDocument(path.split('/')[-1])
            if doc is None:
                # skip row and save will remove the reference
                continue
            row = dict(Form=doc.getItem('Form', None), getId=doc.getId())
            for key in fields:
                row[key] = doc.getItem(key)
            datatable.append(row)
        if getattr(self.context, 'sourceview'):
            sourceview = self.context.getParentDatabase().getView(
                self.context.sourceview)
            # Lets reduce down to our paths
            # TODO: this is going to filter by access permissions? if so some might be missing
            brains = sourceview.getAllDocuments(getObject=False, only_allowed=True,
                                                request_query={'paths': paths})
            for b in brains:
                doc = b.getObject()  # TODO: should be able to get Form without waking up object?
                for row in datatable:
                    if row['getId'] == b.id:
                        # TODO: we need to return all the data in the doc, for the associated form. Otherwise will get reset.
                        # as well as the view metadata.
                        for col in fields:
                            key = sourceview.getIndexKey(col)
                            if not key:
                                continue
                            v = getattr(b, key)
                            if not isinstance(v, str):
                                v = unicode(v).encode('utf-8').replace('\r', '')
                            row[col] = (v or '&nbsp;')
        return datatable

        # TODO: handle a datatable when formula (with and without associated_form)


    def getAssociatedForm(self):
        child_form_id = self.context.associated_form
        if child_form_id:
            db = self.context.getParentDatabase()
            f =  db.getForm(child_form_id)
            return db.getForm(child_form_id)


    def getColumns(self):
        """ work out which fields to display. Either based on sourceview, or associatedform, or
        based on the formula. return tuple of ([fieldid,..],[label,..])
         """
        #
        field_ids = None
        lists = [['getId'], ['ID']]

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

        if self.context.associated_form:
            child_form_id = self.context.associated_form
            if not child_form_id:
                return ""

            db = self.context.getParentDatabase()
            child_form = db.getForm(child_form_id)
            _lists = zip(*[(f.id, f.title) for f in child_form.getFormFields(includesubforms=True)])
            if _lists != []:
                # Add form field together with view column
                if self.context.sourceview:
                    lists =  lists[0]+ _lists[0],lists[1]+ _lists[1]
                else:
                    lists = _lists
        # TODO: need some better result if not settings. Should be all data? or just a id?

        # If labelcolumn is a list of comma separated values, use the list to define the columns
        # TODO: Sourceview returns formid/fieldid. Sourceview did not work at time of coding
        #         so lable filtering doesn't work for sourceviews
        if self.context.labelcolumn and "," in self.context.labelcolumn:
            label_column_field_ids = [label.strip() for label in self.context.labelcolumn.split(",")]
            all_field_ids = lists[0]
            all_field_titles = lists[1]
            filtered_field_ids = ()
            filtered_field_titles = ()

            for field_id in label_column_field_ids:
                if field_id in all_field_ids:
                    field_index = all_field_ids.index(field_id)
                    filtered_field_ids = filtered_field_ids + (field_id,)        
                    filtered_field_titles = filtered_field_titles + (all_field_titles[field_index],)

            lists = [filtered_field_ids, filtered_field_titles]

        return lists

    def getSourceView(self):
        view_id =  self.context.sourceview
        if view_id:
            sourceview = self.context.getParentDatabase().getView(view_id)
            return sourceview

    def getFieldMapping(self):
        fields,_ = self.getColumns()
        return ','.join(fields)

    def _getLabelColumnFilterByValue(self):
        label_field_id = self.context.labelcolumn

        if "," not in label_field_id:
            return label_field_id

        label_column_field_ids = [label.strip() for label in self.context.labelcolumn.split(",")]
        return label_column_field_ids[0]
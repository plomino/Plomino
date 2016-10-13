from collective.instancebehavior import IInstanceBehaviorAssignableContent
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.supermodel import directives as supermodel_directives
from plone.supermodel import model
from zope import component
from zope import schema
from zope.interface import directlyProvides, implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from ZPublisher.HTTPRequest import FileUpload

from .. import _, plomino_profiler
from ..config import SCRIPT_ID_DELIMITER, FIELD_MODES, FIELD_TYPES
from ..utils import asList, asUnicode
from .. import fields

field_types = SimpleVocabulary([
    SimpleTerm(value=key, title=_(FIELD_TYPES[key][0])) for key in FIELD_TYPES
])
field_modes = SimpleVocabulary([
    SimpleTerm(value=mode[0], title=_(mode[1])) for mode in FIELD_MODES
])
index_types = SimpleVocabulary([])


def get_field_types():
    field_types = FIELD_TYPES
    for plugin_field in component.getUtilitiesFor(IPlominoField):
        params = plugin_field[1].plomino_field_parameters
        field_types[str(plugin_field[0])] = [
            params['label'],
            params['index_type']
        ]
    return field_types


def get_fields(obj):
    """ Get a list of all the fields in the database
    """
    fields = []
    counter = 1
    for form in obj.getParentDatabase().getForms():
        fields.append(
            ['=== ' + form.id + ' ===', 'PlominoPlaceholder%s' % counter])
        counter += 1
        fields += [(form.id + '/' + field.id, form.id + '/' + field.id)
            for field in form.getFormFields()]
    return SimpleVocabulary.fromItems(fields)
directlyProvides(get_fields, IContextSourceBinder)


def get_index_types(obj):
    """ Vocabulary for the 'Index type' dropdown.
    """
    types = get_field_types()
    if isinstance(obj, PlominoField):
        default_index = types[obj.field_type][1]
        indexes = [('Default (%s)' % default_index, 'DEFAULT'), ]
    else:
        indexes = [('Default', 'DEFAULT'), ]
    db = obj.getParentDatabase()
    idx = db.getIndex()
    index_ids = [i['name'] for i in idx.Indexes.filtered_meta_types()]
    for i in index_ids:
        if i in ['GopipIndex', 'UUIDIndex']:
            # Index types internal to Plone
            continue
        label = "%s%s" % (
            i, {
                "FieldIndex": " (match exact value)",
                "ZCTextIndex": " (match any contained words)",
                "KeywordIndex": " (match list elements)"
            }.get(i, '')
        )
        indexes.append((label, i))
    return SimpleVocabulary.fromItems(indexes)
directlyProvides(get_index_types, IContextSourceBinder)


class IPlominoField(model.Schema):
    """ Plomino field schema
    """

    #directives.widget('field_type', onchange=u'this.form.submit()')
    field_type = schema.Choice(
        title=_('CMFPlomino_label_FieldType', default="Field type"),
        description=_('CMFPlomino_label_FieldType', default="Field type"),
        required=True,
        default='TEXT',
        vocabulary=field_types,
    )

    mandatory = schema.Bool(
        title=_('CMFPlomino_label_FieldMandatory', default="Mandatory"),
        description=_('CMFPlomino_help_FieldMandatory',
            default='Is this field mandatory? (empty value will not be '
                'allowed)'),
        default=False,
        required=True,
    )

    directives.widget('validation_formula', klass='plomino-formula')
    validation_formula = schema.Text(
        title=_('CMFPlomino_label_FieldValidation',
            default="Validation formula"),
        description=_('CMFPlomino_help_FieldValidation',
            default='Evaluate the input validation'),
        required=False,
    )

    field_mode = schema.Choice(
        title=_('CMFPlomino_label_FieldMode', default="Field mode"),
        description=_('CMFPlomino_label_FieldMode', default="Field mode"),
        required=True,
        default='EDITABLE',
        vocabulary=field_modes,
    )

    isDynamicField = schema.Bool(
        title=_('CMFPlomino_label_isDynamicField',
            default="Dynamic rendering"),
        description=_('CMFPlomino_help_isDynamicField',
            default="The field will be rendered dynamically "
                    "when the user enters information"),
        required=False,
        default=False,
    )

    directives.widget('formula', klass='plomino-formula')
    formula = schema.Text(
        title=_('CMFPlomino_label_FieldFormula', default="Formula"),
        description=_('CMFPlomino_help_FieldFormula',
            default='How to calculate field content'),
        required=False,
    )

    to_be_indexed = schema.Bool(
        title=_('CMFPlomino_label_FieldIndex', default="Add to index"),
        description=_('CMFPlomino_help_FieldIndex',
            default='The field will be searchable'),
        default=False,
        required=True,
    )

    index_type = schema.Choice(
        title=_('CMFPlomino_label_FieldIndexType', default="Index type"),
        description=_('CMFPlomino_help_FieldIndexType',
            default='The way the field values will be indexed'),
        required=True,
        default="DEFAULT",
        source=get_index_types,
    )

    directives.widget('html_attributes_formula', klass='plomino-formula')
    html_attributes_formula = schema.Text(
        title=_('CMFPlomino_label_HTMLAttributesFormula',
            default="HTML attributes formula"),
        description=_('CMFPlomino_help_HTMLAttributesFormula',
            default='Inject DOM attributes in the field tag'),
        required=False,
    )

    read_template = schema.TextLine(
        title=_('CMFPlomino_label_FieldReadTemplate',
            default="Field read template"),
        description=_('CMFPlomino_help_FieldReadTemplate',
            default='Custom rendering template in read mode'),
        required=False,
    )

    edit_template = schema.TextLine(
        title=_('CMFPlomino_label_FieldEditTemplate',
            default="Field edit template"),
        description=_('CMFPlomino_help_FieldEditTemplate',
            default='Custom rendering template in edit mode'),
        required=False,
    )

    # ADVANCED
    supermodel_directives.fieldset(
        'advanced',
        label=_(u'Advanced'),
        fields=(
            'to_be_indexed',
            'index_type',
            'html_attributes_formula',
            'read_template',
            'edit_template',
        ),
    )


class PlominoField(Item):
    implements(IPlominoField, IInstanceBehaviorAssignableContent)

    def validateFormat(self, submittedValue):
        """check if submitted value match the field expected format
        """
        adapt = self.getSettings()
        return adapt.validate(submittedValue)

    def processInput(
        self, submittedValue, doc, process_attachments, validation_mode=False
    ):
        """process submitted value according the field type
        """

        fieldtype = self.field_type
        fieldname = self.id
        adapt = self.getSettings()

        if fieldtype == "ATTACHMENT" and process_attachments:

            if isinstance(submittedValue, FileUpload):
                submittedValue = asList(submittedValue)

            current_files = doc.getItem(fieldname)
            if not current_files:
                current_files = {}

            if submittedValue is not None:
                for fl in submittedValue:
                    (new_file, contenttype) = doc.setfile(fl)
                    if new_file is not None:
                        if self.single_or_multiple == "SINGLE":
                            for filename in current_files.keys():
                                if filename != new_file:
                                    doc.deletefile(filename)
                            current_files = {}
                        current_files[new_file] = contenttype

            v = current_files

        else:
            try:
                v = adapt.processInput(submittedValue)
            except Exception, e:
                # TODO: Log exception
                if validation_mode:
                    # when validating, submitted values are potentially bad
                    # but it must not break getHideWhens, getFormFields, etc.
                    v = submittedValue
                else:
                    raise e

        return v

    @plomino_profiler('fields')
    def getFieldRender(
            self, form, doc, editmode, creation=False, request=None):
        """ Rendering the field
        """
        if doc is None:
            target = form
        else:
            target = doc

        adapt = self.getSettings()
        fieldvalue = adapt.getFieldValue(
            form, doc, editmode, creation, request)

        return self.getRenderedValue(fieldvalue, editmode, target)

    def getRenderedValue(self, fieldvalue, editmode, target):
        """
        """
        mode = self.field_mode
        adapt = self.getSettings()
        if mode == "EDITABLE" and editmode:
            renderer = adapt.render_edit
        else:
            renderer = adapt.render_read

        selection = self.getSelectionList(target)

        try:
            html = renderer(
                field=self,
                fieldvalue=fieldvalue,
                selection=selection,
                doc=target,
            )

            injection_zone = 'name="%s"' % self.id
            if (injection_zone in html
            and self.html_attributes_formula):
                injection_position = html.index(injection_zone)
                html_attributes = self.runFormulaScript(
                    SCRIPT_ID_DELIMITER.join([
                        'field', self.getParentNode().id, self.id,
                        'attributes']),
                    target,
                    self.html_attributes_formula
                )
                html = ' '.join([
                    html[:injection_position],
                    asUnicode(html_attributes),
                    html[injection_position:],
                ])
            return html

        except Exception, e:
            self.traceRenderingErr(e, self)
            return str(e)

    def getSettings(self):
        """
        """
        fieldfactory = getattr(
            getattr(fields, self.field_type.lower()),
            "%sField" % self.field_type.capitalize())

        return fieldfactory(self)

    def getSelectionList(self, doc):
        """
        """
        settings = self.getSettings()
        return settings.getSelectionList(doc)

    def getSchema(self):
        """
        """
        schema = getattr(
            getattr(fields, self.field_type.lower()),
            "I%sField" % self.field_type.capitalize())
        return schema

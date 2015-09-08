from zope.interface import alsoProvides
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory

from .field import get_field_types, PlominoField


def get_fields(obj):
    """ Get a list of all the fields in the database
    """
    fields = []
    counter = 1
    for form in obj.getParentDatabase().getForms():
        fields.append(
            ['=== ' + form.id + ' ===', 'PlominoPlaceholder%s' % counter])
        counter += 1
        fields += [(field.id, form.id + '/' + field.id)
            for field in form.getFormFields()]
    return SimpleVocabulary.fromItems(fields)
alsoProvides(get_fields, IVocabularyFactory)


def get_columns(obj):
    """ Get a list of current view's columns
    """
    columns = [(c.id, c.id) for c in obj.getColumns()]
    return SimpleVocabulary.fromItems(columns)
alsoProvides(get_columns, IVocabularyFactory)


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
alsoProvides(get_index_types, IVocabularyFactory)

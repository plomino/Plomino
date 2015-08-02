from zope.interface import alsoProvides
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory


def field_from_context(obj):
    if hasattr(obj, 'getParentDatabase'):
        return obj
    else:
        return obj.context


def get_forms(obj):
    db = field_from_context(obj).getParentDatabase()
    if not db:
        return []
    forms = db.getForms()
    return SimpleVocabulary.fromItems([(form.id, form.id) for form in forms])
alsoProvides(get_forms, IVocabularyFactory)


def get_views(obj):
    db = field_from_context(obj).getParentDatabase()
    if not db:
        return []
    views = db.getViews()
    return SimpleVocabulary.fromItems([(view.id, view.id) for view in views])
alsoProvides(get_views, IVocabularyFactory)

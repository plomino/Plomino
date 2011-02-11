from Products.validation import validation

try:
    # Plone 4 and higher
    import plone.app.upgrade
    from Products.validation.interfaces.IValidator import IValidator
    USE_BBB_VALIDATORS = False
except ImportError:
    # BBB Plone 3
    from Products.validation.interfaces import ivalidator
    USE_BBB_VALIDATORS = True
    
from zope.interface import implements

class PlominoIdValidator:
    if USE_BBB_VALIDATORS:
        __implements__ = (ivalidator,)
    else:
        implements(IValidator)
    
    def __init__(self, name, title='', description=''):
        self.name = name
        self.title = title or name
        self.description = description
        
    def __call__(self, value, *args, **kwargs):
        if '_' in value:
            return ("The character _ is not allowed here.")
        return True

isValidPlominoId = PlominoIdValidator('isValidPlominoId', title='Plomino ids',
    description='Views and columns ids must not contains _.')
from Products.validation import validation
from Products.validation.interfaces.IValidator import IValidator
from zope.interface import implements

class PlominoIdValidator:
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
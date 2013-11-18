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

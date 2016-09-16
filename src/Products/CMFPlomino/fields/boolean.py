# -*- coding: utf-8 -*-

from plone.autoform.interfaces import IFormFieldProvider, ORDER_KEY
from plone.supermodel import directives, model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from .. import _
from base import BaseField


@provider(IFormFieldProvider)
class IBooleanField(model.Schema):
    """
    """

    widget = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Single checkbox", "CHECKBOX")
        ]),
        title=u'Widget',
        description=u'Field rendering',
        default="CHECKBOX",
        required=True)

# bug in plone.autoform means order_after doesn't moves correctly
IBooleanField.setTaggedValue(ORDER_KEY,
                               [('widget', 'after', 'field_type'),
                               ]
)

@implementer(IBooleanField)
class BooleanField(BaseField):
    """
    """

    read_template = PageTemplateFile('boolean_read.pt')
    edit_template = PageTemplateFile('boolean_edit.pt')

    def processInput(self, strValue):
        """
        """
        if type(strValue) is bool:
            return strValue
        if strValue == "1":
            return True
        else:
            return False

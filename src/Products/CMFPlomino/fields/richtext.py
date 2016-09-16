# -*- coding: utf-8 -*-

from plone.autoform.interfaces import IFormFieldProvider, ORDER_KEY
from plone.supermodel import directives, model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema

from .. import _
from base import BaseField


@provider(IFormFieldProvider)
class IRichtextField(model.Schema):
    """ Rich text field schema
    """

    height = schema.TextLine(
        title=u'Height',
        description=u'Height in pixels',
        required=False)

# bug in plone.autoform means order_after doesn't moves correctly
IRichtextField.setTaggedValue(ORDER_KEY,
                               [('height', 'after', 'field_type')]
)

@implementer(IRichtextField)
class RichtextField(BaseField):
    """
    """

    read_template = PageTemplateFile('richtext_read.pt')
    edit_template = PageTemplateFile('richtext_edit.pt')

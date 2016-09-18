# -*- coding: utf-8 -*-

from plone.autoform.interfaces import IFormFieldProvider, ORDER_KEY
from plone.supermodel import directives, model
from Products.CMFPlone.utils import normalizeString
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from .. import _
from base import BaseField


@provider(IFormFieldProvider)
class IAttachmentField(model.Schema):
    """ Attachment field schema
    """

    single_or_multiple = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems(
            [("Single file", "SINGLE"), ("Multiple files", "MULTI")]),
        title=u'Type',
        description=u'Single or multiple file(s)',
        default="MULTI",
        required=True)

# bug in plone.autoform means order_after doesn't moves correctly
IAttachmentField.setTaggedValue(ORDER_KEY,
                               [('single_or_multiple', 'after', 'field_type'),
                               ]
)


@implementer(IAttachmentField)
class AttachmentField(BaseField):
    """
    """

    read_template = PageTemplateFile('attachment_read.pt')
    edit_template = PageTemplateFile('attachment_edit.pt')

    def processInput(self, strValue):
        """
        """
        # only called in during validation
        if not strValue:
            return None
        strValue = normalizeString(strValue)
        return {strValue: 'application/unknown'}

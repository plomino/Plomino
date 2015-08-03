# -*- coding: utf-8 -*-

from plone.autoform.interfaces import IFormFieldProvider
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

    directives.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=('height', ),
    )

    height = schema.TextLine(
        title=u'Height',
        description=u'Height in pixels',
        required=False)


@implementer(IRichtextField)
class RichtextField(BaseField):
    """
    """

    read_template = PageTemplateFile('richtext_read.pt')
    edit_template = PageTemplateFile('richtext_edit.pt')

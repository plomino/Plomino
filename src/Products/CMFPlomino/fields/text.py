# -*- coding: utf-8 -*-

from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import directives
from plone.supermodel import model
from zope.interface import implementer
from zope.interface import provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope.schema import TextLine, Choice
from zope.schema.vocabulary import SimpleVocabulary

from .. import _
from base import BaseField


@provider(IFormFieldProvider)
class ITextField(model.Schema):
    """
    """

    directives.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=('widget', 'size', ),
    )

    widget = Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Text", "TEXT"),
            ("Long text", "TEXTAREA"),
            ("Hidden", "HIDDEN")
        ]),
        title=u'Widget',
        description=u'Field rendering',
        default="TEXT",
        required=True)
    size = TextLine(
        title=u'Size',
        description=u'Length or rows (depending on the widget)',
        required=False)


@implementer(ITextField)
class TextField(BaseField):
    """
    """

    read_template = PageTemplateFile('text_read.pt')
    edit_template = PageTemplateFile('text_edit.pt')

    def __init__(self, context):
        self.context = context

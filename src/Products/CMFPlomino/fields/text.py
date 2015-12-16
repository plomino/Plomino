# -*- coding: utf-8 -*-

from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import directives, model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
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
        fields=('widget', 'size', 'preserve_carriage_returns'),
    )

    widget = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Text", "TEXT"),
            ("Long text", "TEXTAREA"),
            ("Hidden", "HIDDEN")
        ]),
        title=u'Widget',
        description=u'Field rendering',
        default="TEXT",
        required=True)

    size = schema.TextLine(
        title=u'Size',
        description=u'Length or rows (depending on the widget)',
        required=False)

    preserve_carriage_returns = schema.Bool(
        title=_('CMFPlomino_label_preserve_carriage_returns',
            default='Preserve carriage returns'),
        description=_('CMFPlomino_help_preserve_carriage_returns',
            default='Render carriage returns in HTML'),
        default=False,
        required=False,
    )


@implementer(ITextField)
class TextField(BaseField):
    """
    """

    read_template = PageTemplateFile('text_read.pt')
    edit_template = PageTemplateFile('text_edit.pt')

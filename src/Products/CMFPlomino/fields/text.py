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
class ITextField(model.Schema):
    """
    """
    #
    # directives.fieldset(
    #     'settings',
    #     label=_(u'Settings'),
    #     fields=('widget', 'size', 'preserve_carriage_returns'),
    # )

    widget = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems([
            (_("Text"), "TEXT"),
            (_("Long text"), "TEXTAREA"),
            (_("Hidden"), "HIDDEN")
        ]),
        title=_('CMFPlomino_label_widget',
            default='Widget'),
        description=_('CMFPlomino_help_widget',
            default='Field rendering'),
        default="TEXT",
        required=True)

    size = schema.TextLine(
        title=_('CMFPlomino_label_size',
            default='Size'),
        description=_('CMFPlomino_help_size',
            default='Length or rows (depending on the widget)'),
        required=False)

    preserve_carriage_returns = schema.Bool(
        title=_('CMFPlomino_label_preserve_carriage_returns',
            default='Preserve carriage returns'),
        description=_('CMFPlomino_help_preserve_carriage_returns',
            default='Render carriage returns in HTML'),
        default=False,
        required=False,
    )

# bug in plone.autoform means order_after doesn't moves correctly
ITextField.setTaggedValue(ORDER_KEY,
                               [('widget', 'after', 'field_type'),
                                ('size', 'after', ".widget"),
                                ('preserve_carriage_returns', 'after', ".size")]
)

@implementer(ITextField)
class TextField(BaseField):
    """
    """

    read_template = PageTemplateFile('text_read.pt')
    edit_template = PageTemplateFile('text_edit.pt')

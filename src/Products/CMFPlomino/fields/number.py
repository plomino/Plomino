# -*- coding: utf-8 -*-

from decimal import Decimal
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import directives, model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from .. import _
from ..utils import PlominoTranslate
from base import BaseField


@provider(IFormFieldProvider)
class INumberField(model.Schema):
    """ Number field schema
    """

    directives.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=('number_type', 'size', 'format', ),
    )

    number_type = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Integer", "INTEGER"),
            ("Float", "FLOAT"),
            ("Decimal", "DECIMAL"),
        ]),
        title=u'Type',
        description=u'Number type',
        default="INTEGER",
        required=True)

    size = schema.TextLine(
        title=u'Size',
        description=u'Length',
        required=False)

    format = schema.TextLine(
        title=u'Format',
        description=u'Number formatting (example: %1.2f)',
        required=False)


@implementer(INumberField)
class NumberField(BaseField):
    """
    """

    read_template = PageTemplateFile('number_read.pt')
    edit_template = PageTemplateFile('number_edit.pt')

    def validate(self, submittedValue):
        """
        """
        errors = []
        fieldname = self.context.id
        if self.context.number_type == "INTEGER":
            try:
                long(submittedValue)
            except:
                errors.append(
                    fieldname +
                    PlominoTranslate(
                        _(" must be an integer (submitted value was: "),
                        self.context) +
                    submittedValue + ")")
        elif self.context.number_type == "FLOAT":
            try:
                float(submittedValue)
            except:
                errors.append(
                    fieldname +
                    PlominoTranslate(
                        _(" must be a float (submitted value was: "),
                        self.context) +
                    submittedValue + ")")
        elif self.context.number_type == "DECIMAL":
            try:
                Decimal(str(submittedValue))
            except:
                errors.append(
                    fieldname +
                    PlominoTranslate(
                        _(" must be a decimal (submitted value was: "),
                        self.context) +
                    submittedValue + ")")

        return errors

    def processInput(self, submittedValue):
        """
        """
        if self.context.number_type == "INTEGER":
            return long(submittedValue)
        elif self.context.number_type == "FLOAT":
            return float(submittedValue)
        elif self.context.number_type == "DECIMAL":
            return Decimal(str(submittedValue))
        else:
            return submittedValue

    def format_value(self, v):
        """
        """
        str_v = ""
        if v not in (None, "") and self.context.format:
            try:
                str_v = self.format % v
            except TypeError:
                str_v = "Formatting error"
        else:
            str_v = str(v)
        return str_v

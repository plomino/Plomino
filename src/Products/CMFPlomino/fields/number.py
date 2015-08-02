# -*- coding: utf-8 -*-

from decimal import Decimal
from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields
from zope.schema import TextLine, Choice
from zope.schema.vocabulary import SimpleVocabulary

from .. import _
from ..utils import PlominoTranslate
from base import IBaseField, BaseField, BaseForm
from dictionaryproperty import DictionaryProperty


class INumberField(IBaseField):
    """ Number field schema
    """
    type = Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Integer", "INTEGER"),
            ("Float", "FLOAT"),
            ("Decimal", "DECIMAL"),
        ]),
        title=u'Type',
        description=u'Number type',
        default="INTEGER",
        required=True)
    size = TextLine(
        title=u'Size',
        description=u'Length',
        required=False)
    format = TextLine(
        title=u'Format',
        description=u'Number formatting (example: %1.2f)',
        required=False)


class NumberField(BaseField):
    """
    """
    implements(INumberField)

    def validate(self, submittedValue):
        """
        """
        errors = []
        fieldname = self.context.id
        if self.type == "INTEGER":
            try:
                long(submittedValue)
            except:
                errors.append(
                    fieldname +
                    PlominoTranslate(
                        _(" must be an integer (submitted value was: "),
                        self.context) +
                    submittedValue + ")")
        elif self.type == "FLOAT":
            try:
                float(submittedValue)
            except:
                errors.append(
                    fieldname +
                    PlominoTranslate(
                        _(" must be a float (submitted value was: "),
                        self.context) +
                    submittedValue + ")")
        elif self.type == "DECIMAL":
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
        if self.type == "INTEGER":
            return long(submittedValue)
        elif self.type == "FLOAT":
            return float(submittedValue)
        elif self.type == "DECIMAL":
            return Decimal(str(submittedValue))
        else:
            return submittedValue

    def format_value(self, v):
        """
        """
        str_v = ""
        if v not in (None, "") and self.format:
            try:
                str_v = self.format % v
            except TypeError:
                str_v = "Formatting error"
        else:
            str_v = str(v)
        return str_v

for f in getFields(INumberField).values():
    setattr(NumberField, f.getName(), DictionaryProperty(f, 'parameters'))


class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(INumberField)

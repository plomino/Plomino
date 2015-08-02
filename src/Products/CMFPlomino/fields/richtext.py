# -*- coding: utf-8 -*-

from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields
from zope.schema import TextLine

from base import IBaseField, BaseField, BaseForm
from dictionaryproperty import DictionaryProperty


class IRichtextField(IBaseField):
    """ Text field schema
    """
    height = TextLine(
        title=u'Height',
        description=u'Height in pixels',
        required=False)


class RichtextField(BaseField):
    """
    """
    implements(IRichtextField)

for f in getFields(IRichtextField).values():
    setattr(RichtextField,
            f.getName(),
            DictionaryProperty(f, 'parameters'))


class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IRichtextField)

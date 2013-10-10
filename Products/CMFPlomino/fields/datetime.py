# -*- coding: utf-8 -*-
#
# File: datetime.py
#
# Copyright (c) 2009 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

# Standard
import logging
logger = logging.getLogger('Plomino')

# Zope
from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields
from zope.schema import TextLine

# Plomino
from base import IBaseField, BaseField, BaseForm
from dictionaryproperty import DictionaryProperty
from Products.CMFPlomino.PlominoUtils import StringToDate


class IDatetimeField(IBaseField):
    """
    DateTime field schema
    """
    format = TextLine(
            title=u'Format',
            description=u"Date/time format (if different than "
                    "database default format)",
            required=False)
    startingyear = TextLine(
            title=u"Starting year",
            description=u"Oldest year selectable in the calendar widget",
            required=False)


class DatetimeField(BaseField):
    """
    """
    implements(IDatetimeField)

    def validate(self, submittedValue):
        """
        """
        errors = []
        fieldname = self.context.id
        submittedValue = submittedValue.strip()
        try:
            # check if date only:
            if len(submittedValue) == 10:
                v = StringToDate(submittedValue, '%Y-%m-%d')
            else:
                # calendar widget default format is '%Y-%m-%d %H:%M' and
                # might use the AM/PM format
                if submittedValue[-2:] in ['AM', 'PM']:
                    v = StringToDate(submittedValue, '%Y-%m-%d %I:%M %p')
                else:
                    v = StringToDate(submittedValue, '%Y-%m-%d %H:%M')
        except:
            errors.append(
                    "%s must be a date/time (submitted value was: %s)" % (
                        fieldname,
                        submittedValue))
        return errors

    def processInput(self, submittedValue):
        """
        """
        submittedValue = submittedValue.strip()
        try:
            # check if date only:
            if len(submittedValue) == 10:
                d = StringToDate(submittedValue, '%Y-%m-%d')
            else:
                # calendar widget default format is '%Y-%m-%d %H:%M' and
                # might use the AM/PM format
                if submittedValue[-2:] in ['AM', 'PM']:
                    d = StringToDate(submittedValue, '%Y-%m-%d %I:%M %p')
                else:
                    d = StringToDate(submittedValue, '%Y-%m-%d %H:%M')
            return d
        except:
            # with datagrid, we might get dates formatted differently than
            # using calendar widget default format
            fmt = self.format
            if not fmt:
                fmt = self.context.getParentDatabase().getDateTimeFormat()
            return StringToDate(submittedValue, fmt)

    def getFieldValue(self, form, doc=None, editmode_obsolete=False,
            creation=False, request=None):
        """
        """
        fieldValue = BaseField.getFieldValue(
                self, form, doc, editmode_obsolete, creation, request)

        mode = self.context.getFieldMode()
        if mode == "EDITABLE" and request:
            if ((doc is None and not(creation)) or 
                    request.has_key('Plomino_datagrid_rowdata')):
                fieldname = self.context.id
                fieldValue = request.get(fieldname, fieldValue)
                if fieldValue:
                    fmt = self.format
                    if not fmt:
                        fmt = form.getParentDatabase().getDateTimeFormat()
                    fieldValue = StringToDate(fieldValue, fmt)
        return fieldValue

for f in getFields(IDatetimeField).values():
    setattr(DatetimeField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IDatetimeField)


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
from zope.schema import TextLine, Choice
from zope.schema.vocabulary import SimpleVocabulary

# Plomino
from base import IBaseField, BaseField, BaseForm
from dictionaryproperty import DictionaryProperty
from Products.CMFPlomino.PlominoUtils import StringToDate
from Products.CMFPlomino.PlominoUtils import PlominoTranslate


class IDatetimeField(IBaseField):
    """
    DateTime field schema
    """
    widget = Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Default", "SERVER"),
            ("JQuery datetime widget", "JQUERY")
        ]),
        title=u'Widget',
        description=u'Field rendering',
        default="SERVER",
        required=True)
    format = TextLine(
            title=u'Format',
            description=u"Date/time format (if different than "
                    "database default format)",
            required=False)
    startingyear = TextLine(
            title=u"Starting year",
            description=u"Oldest year selectable in the calendar widget",
            required=False)
    endingyear = TextLine(
            title=u"Ending year",
            description=u"Newest year selectable in the calendar widget",
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
        if isinstance(submittedValue, basestring):
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
        else:
            # it is instance type when no js is detected
            # submittedValue = ampm: , day: 09, hour: 00, minute: 00, month: 03, year: 1993
            try:
                submitted_string = ''
                if not('year' in submittedValue and
                   'month' in submittedValue and
                   'day' in submittedValue and
                   'hour' in submittedValue and
                   'minute' in submittedValue and
                   'ampm' in submittedValue):
                    errors.append(
                        "%s must be a date/time format" % (
                            fieldname))
                if not(submittedValue.year.isdigit() and
                   submittedValue.month.isdigit() and
                   submittedValue.day.isdigit() and
                   submittedValue.hour.isdigit() and
                   submittedValue.minute.isdigit()):
                    errors.append(
                        "%s must be a digit format" % (
                            fieldname))

                if not(submittedValue.ampm == '' or
                   submittedValue.ampm.upper() == 'AM' or
                   submittedValue.ampm.upper() == 'PM'):
                    errors.append(
                        "%s must be a AM/PM format." % (
                            fieldname))
                # should not raise any error if date is empty or half filled
                if submittedValue.year == '0000' and \
                   submittedValue.month == '00' and \
                   submittedValue.day == '00':
                    if self.context.getMandatory():
                       errors.append("%s %s" % (
                           self.context.Title(),
                           PlominoTranslate("is mandatory", self.context)))
                    return errors

                date_input = self.recordToDate(submittedValue)
            except:
                errors.append(
                        "%s must be a valid date/time (submitted value was: %s)" % (
                            fieldname,
                            submitted_string))

        return errors

    def processInput(self, submittedValue):
        """
        """
        if isinstance(submittedValue, basestring):
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
        # it is instance type when no js is detected
        # submittedValue = ampm: , day: 09, hour: 00, minute: 00, month: 03, year: 1993
        if submittedValue.year == '0000' and \
           submittedValue.month == '00' and \
           submittedValue.day == '00':
            return None

        date_input = self.recordToDate(submittedValue)

        return date_input


    def getFieldValue(self, form, doc=None, editmode_obsolete=False,
            creation=False, request=None):
        """
        """
        fieldValue = BaseField.getFieldValue(
                self, form, doc, editmode_obsolete, creation, request)

        mode = self.context.getFieldMode()
        if (mode == "EDITABLE" and
            request and
            ((doc is None and not(creation)) or
             request.has_key('Plomino_datagrid_rowdata'))):
            fieldname = self.context.id
            fieldValue = request.get(fieldname, fieldValue)

        try:
            if fieldValue and isinstance(fieldValue, basestring):
                fmt = self.format
                if not fmt:
                    fmt = form.getParentDatabase().getDateTimeFormat()
                fieldValue = StringToDate(fieldValue, fmt)
            elif "year" in fieldValue and "month" in fieldValue and \
                 "day" in fieldValue and "ampm" in fieldValue and \
                 "hour" in fieldValue and "minute" in fieldValue:
               fieldValue = self.recordToDate(fieldValue)
        except TypeError:
            # fieldValue could be DateTime type
            pass

        return fieldValue

    def recordToDate(self, record):
        if record.ampm.upper() == 'AM' or record.ampm.upper() == 'PM':
            submitted_string = "{v.year}-{v.month}-{v.day} {v.hour}:{v.minute} {v.ampm}".format(v=record)
            date_input = StringToDate(submitted_string, '%Y-%m-%d %I:%M %p')
        else:
            submitted_string = "{v.year}-{v.month}-{v.day} {v.hour}:{v.minute}".format(v=record)
            date_input = StringToDate(submitted_string, '%Y-%m-%d %H:%M')

        return date_input

for f in getFields(IDatetimeField).values():
    setattr(DatetimeField, f.getName(), DictionaryProperty(f, 'parameters'))


class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IDatetimeField)

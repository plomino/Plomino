# -*- coding: utf-8 -*-
import json
import logging

from base import BaseField
from DateTime import DateTime
from plone.autoform.interfaces import IFormFieldProvider
from plone.autoform.interfaces import ORDER_KEY
from plone.supermodel import model
from zope.interface import implementer
from zope.interface import provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from ZPublisher.HTTPRequest import record

from Products.CMFPlomino.utils import DatetimeToJS
from Products.CMFPlomino.utils import StringToDate

logger = logging.getLogger('Plomino')


@provider(IFormFieldProvider)
class IDatetimeField(model.Schema):
    """DateTime field schema"""

    widget = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Default", "SERVER"),
            ("Combination", "COMBO"),
            ("JQuery datetime widget", "JQUERY")
        ]),
        title=u'Widget',
        description=u'Field rendering',
        default="SERVER",
        required=True)

    format = schema.TextLine(
        title=u'Format',
        description=u"Date/time format (if different than "
        "database default format)",
        required=False)

    startingyear = schema.TextLine(
        title=u"Starting year",
        description=u"Oldest year selectable in the calendar widget",
        default=u"1975",
        required=False)

# bug in plone.autoform means order_after doesn't moves correctly
IDatetimeField.setTaggedValue(ORDER_KEY,
                              [('widget', 'after', 'field_type'),
                               ('format', 'after', ".widget"),
                               ('startingyear', 'after', ".format")])


class RecordException(Exception):
    """ Raise if there's a problem with the :record values """


@implementer(IDatetimeField)
class DatetimeField(BaseField):
    """Date time field"""

    read_template = PageTemplateFile('datetime_read.pt')
    edit_template = PageTemplateFile('datetime_edit.pt')

    def validate(self, submittedValue):
        """Validate date time value"""
        if type(submittedValue) is DateTime:
            return []
        errors = []
        # instead of checking not record, should check string type
        if isinstance(submittedValue, basestring):
            submittedValue = submittedValue.strip()
        try:
            # Check for a record
            if isinstance(submittedValue, record):
                year = submittedValue.get('year', '')
                month = submittedValue.get('month', '')
                day = submittedValue.get('day', '')
                hour = submittedValue.get('hour', '')
                minute = submittedValue.get('minute', '')
                second = submittedValue.get('second', '')

                format = self.context.format
                if not format:
                    format = self.context.getParentDatabase().datetime_format
                show_ymd = False
                show_hm = False
                show_sec = False
                convertedValue = []

                # Check for year, hour and second. Raise an exception
                # if the required values haven't been submitted
                if '%Y' in format or '%y' in format:
                    if year and month and day:
                        convertedValue.append('%s-%s-%s' % (year, month, day))
                        show_ymd = True
                    else:
                        raise Exception

                if '%H' in format:
                    if hour and minute:
                        if '%S' in format:
                            if second:
                                convertedValue.append('%s:%s:%s' % (hour, minute, second))
                                show_hm = True
                                show_sec = True
                            else:
                                raise Exception
                        else:
                            convertedValue.append('%s:%s' % (hour, minute))
                            show_hm = True
                    else:
                        raise Exception

                submittedValue = ' '.join(convertedValue)

                if (show_ymd and show_hm and show_sec):
                    # Don't allow StringToDate to guess the format
                    StringToDate(
                        submittedValue, '%Y-%m-%d %H:%M:%S', guess=False, tozone=False)
                elif (show_ymd and show_hm):
                    StringToDate(
                        submittedValue, '%Y-%m-%d %H:%M', guess=False, tozone=False)
                elif (show_ymd):
                    StringToDate(
                        submittedValue, '%Y-%m-%d', guess=False, tozone=False)
                elif (show_hm and show_sec):
                    StringToDate(
                        submittedValue, '%H:%M:%S', guess=False, tozone=False)
                elif (show_hm):
                    StringToDate(
                        submittedValue, '%H:%M', guess=False, tozone=False)
                else:
                    # The record instance isn't valid
                    raise Exception
            # submittedValue could be dict from tojson
            # {u'<datetime>': True, u'datetime': u'2016-12-12T00:00:00'}
            elif isinstance(
                    submittedValue, dict) and '<datetime>' in submittedValue:
                StringToDate(submittedValue['datetime'], format=None)
            # check if date only:
            elif len(submittedValue) == 10:
                StringToDate(submittedValue, '%Y-%m-%d')
            else:
                # calendar widget default format is '%Y-%m-%d %H:%M' and
                # might use the AM/PM format
                if submittedValue[-2:] in ['AM', 'PM']:
                    StringToDate(submittedValue, '%Y-%m-%d %I:%M %p')
                else:
                    StringToDate(submittedValue, '%Y-%m-%d %H:%M')
        except Exception:
            fieldname = self.context.id
            errors.append(
                "%s must be a date/time (submitted value was: %s)" % (
                    fieldname,
                    submittedValue))
        return errors

    def processInput(self, submittedValue):
        """Process date time value input"""
        if type(submittedValue) is DateTime:
            return submittedValue
        # instead of checking not record, should check string type
        if isinstance(submittedValue, basestring):
            submittedValue = submittedValue.strip()
        try:
            # Check for a record
            if isinstance(submittedValue, record):
                year = submittedValue.get('year', '')
                month = submittedValue.get('month', '')
                day = submittedValue.get('day', '')
                hour = submittedValue.get('hour', '')
                minute = submittedValue.get('minute', '')
                second = submittedValue.get('second', '')

                format = self.context.format
                if not format:
                    format = self.context.getParentDatabase().datetime_format
                show_ymd = False
                show_hm = False
                show_sec = False
                convertedValue = []

                # Check for year, hour and second. Raise an exception
                # if the required values haven't been submitted
                if '%Y' in format or '%y' in format:
                    if year and month and day:
                        convertedValue.append('%s-%s-%s' % (year, month, day))
                        show_ymd = True
                    else:
                        raise RecordException

                if '%H' in format:
                    if hour and minute:
                        if '%S' in format:
                            if second:
                                convertedValue.append('%s:%s:%s' % (hour, minute, second))
                                show_hm = True
                                show_sec = True
                            else:
                                raise RecordException
                        else:
                            convertedValue.append('%s:%s' % (hour, minute))
                            show_hm = True
                    else:
                        raise RecordException

                submittedValue = ' '.join(convertedValue)

                if (show_ymd and show_hm and show_sec):
                    # Don't allow StringToDate to guess the format
                    d = StringToDate(
                        submittedValue, '%Y-%m-%d %H:%M:%S', guess=False, tozone=False)
                elif (show_ymd and show_hm):
                    d = StringToDate(
                        submittedValue, '%Y-%m-%d %H:%M', guess=False, tozone=False)
                elif (show_ymd):
                    d = StringToDate(
                        submittedValue, '%Y-%m-%d', guess=False, tozone=False)
                elif (show_hm and show_sec):
                    d = StringToDate(
                        submittedValue, '%H:%M:%S', guess=False, tozone=False)
                elif (show_hm):
                    d = StringToDate(
                        submittedValue, '%H:%M', guess=False, tozone=False)
                else:
                    # The record instance isn't valid
                    raise RecordException

            # submittedValue could be dict from tojson
            # {u'<datetime>': True, u'datetime': u'2016-12-12T00:00:00'}
            elif isinstance(
                    submittedValue, dict) and '<datetime>' in submittedValue:
                d = StringToDate(submittedValue['datetime'], format=None)
            # check if date only:
            elif len(submittedValue) == 10:
                d = StringToDate(submittedValue, '%Y-%m-%d')
            else:
                # calendar widget default format is '%Y-%m-%d %H:%M' and
                # might use the AM/PM format
                if submittedValue[-2:] in ['AM', 'PM']:
                    d = StringToDate(submittedValue, '%Y-%m-%d %I:%M %p')
                else:
                    d = StringToDate(submittedValue, '%Y-%m-%d %H:%M')
            return d
        except RecordException:
            # We don't have a valid record, so we can't process anything
            return None
        except Exception:
            # with datagrid, we might get dates formatted differently than
            # using calendar widget default format
            return StringToDate(submittedValue[:16], '%Y-%m-%dT%H:%M')

    def getFieldValue(self, form, doc=None, editmode_obsolete=False,
                      creation=False, request=None):
        """Get date time field value"""
        fieldValue = BaseField.getFieldValue(
            self, form, doc, editmode_obsolete, creation, request)
        logger.debug('Method: datetime getFieldValue value {}'.format(
            fieldValue))

        mode = self.context.field_mode
        if (mode == "EDITABLE" and
            request and
            ((doc is None and not(creation)) or
                'Plomino_datagrid_rowdata' in request)):
            fieldname = self.context.id
            fieldValue = request.get(fieldname, fieldValue)

        if fieldValue and isinstance(fieldValue, basestring):
            fmt = self.context.format
            if not fmt:
                fmt = form.getParentDatabase().datetime_format
            fieldValue = StringToDate(fieldValue, fmt)

        return fieldValue

    def getJSFormat(self):
        """Get the current python datetime format and convert to js format.

        Need to split to two data and time formats.
        Example js format is
        {"time": false, "date": {"format": "dd mmmm yyyy" }}

        :return: js format string that used in data-pat-pickadate
        """
        fmt = self.context.format
        if not fmt:
            fmt = self.context.getParentDatabase().datetime_format
        if not fmt:
            return ''

        date_format, time_format = DatetimeToJS(fmt, split=True)
        datetime_pattern = dict([('time', False), ('date', False)])
        if date_format:
            js_pattern = dict([('format', date_format)])
            datetime_pattern['date'] = js_pattern
        if time_format:
            js_pattern = dict([('format', time_format)])
            datetime_pattern['time'] = js_pattern

        return json.dumps(datetime_pattern)

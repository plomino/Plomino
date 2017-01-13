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
            ("Single input", "SERVER"),
            ("Split input", "COMBO"),
            ("Calendar", "JQUERY"),
            ("Native", "HTML5")
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


def _datetime_record(submitted_value, value_format):
    year = submitted_value.get('year', '')
    month = submitted_value.get('month', '')
    day = submitted_value.get('day', '')
    hour = submitted_value.get('hour', '')
    minute = submitted_value.get('minute', '')
    second = submitted_value.get('second', '')
    show_ymd = False
    show_hm = False
    show_sec = False
    converted_value = []

    # Check for year, hour and second. Raise an exception
    # if the required values haven't been submitted
    if '%Y' in value_format or '%y' in value_format:
        if year and month and day:
            converted_value.append('%s-%s-%s' % (year, month, day))
            show_ymd = True
        else:
            raise RecordException

    if '%H' in value_format or '%I' in value_format:
        if hour and minute:
            if '%S' in value_format:
                if second:
                    converted_value.append('%s:%s:%s' % (hour, minute, second))
                    show_hm = True
                    show_sec = True
                else:
                    raise RecordException
            else:
                converted_value.append('%s:%s' % (hour, minute))
                show_hm = True
        else:
            raise RecordException

    submitted_value = ' '.join(converted_value)

    try:
        if show_ymd and show_hm and show_sec:
            # Don't allow StringToDate to guess the format
            result = StringToDate(submitted_value,
                '%Y-%m-%d %H:%M:%S', guess=False, tozone=False)
        elif show_ymd and show_hm:
            result = StringToDate(submitted_value,
                '%Y-%m-%d %H:%M', guess=False, tozone=False)
        elif show_ymd:
            result = StringToDate(submitted_value,
                '%Y-%m-%d', guess=False, tozone=False)
        elif show_hm and show_sec:
            result = StringToDate(submitted_value,
                '%H:%M:%S', guess=False, tozone=False)
        elif show_hm:
            result = StringToDate(submitted_value,
                '%H:%M', guess=False, tozone=False)
        else:
            # The record instance isn't valid
            raise RecordException
    except ValueError:
        raise RecordException
    return result


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
        field_title = self.context.title

        # instead of checking not record, should check string type
        if isinstance(submittedValue, basestring):
            submittedValue = submittedValue.strip()
        try:
            # Check for a record
            # Only widget == 'COMBO', submittedValue is record
            if isinstance(submittedValue, record):
                input_format = self.context.format
                if not input_format:
                    input_format = self.context.getParentDatabase().datetime_format
                _datetime_record(submittedValue, input_format)

            # submittedValue could be dict from tojson
            # {u'<datetime>': True, u'datetime': u'2016-12-12T00:00:00'}
            elif isinstance(
                    submittedValue, dict) and '<datetime>' in submittedValue:
                StringToDate(submittedValue['datetime'], format=None)
            # on 'SERVER' widget, the datetime format must match
            # the field or db format
            elif self.context.field_mode == 'EDITABLE' and \
                            self.context.widget == 'SERVER':
                logger.debug('Method: datetime validate id {} value {}'.format(
                    self.context.id, submittedValue))
                field_format = self.context.format
                if not field_format:
                    db = self.context.getParentDatabase()
                    field_format = db.datetime_format
                if not field_format:
                    errors.append(
                        "{} does not have date/time format".format(
                            self.context.id))
                    return errors
                # it will raise ValueError, when guess is False
                # it won't guess the format
                StringToDate(submittedValue, field_format, guess=False)
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
        except ValueError:
            field_format = self.context.format
            if not field_format:
                db = self.context.getParentDatabase()
                field_format = db.datetime_format
            errors.append(
                "Field '{}': '{}' does not match the format '{}'".format(
                field_title, submittedValue, field_format))
        except (RecordException, Exception):
            errors.append(
                "Field '%s' must be a valid date/time (submitted value was: "
                "%s)" % (
                    field_title,
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
            # Only widget == 'COMBO', submittedValue is record
            if isinstance(submittedValue, record):
                input_format = self.context.format
                if not input_format:
                    input_format = self.context.getParentDatabase().datetime_format
                input_value = _datetime_record(submittedValue, input_format)

            # submittedValue could be dict from tojson
            # {u'<datetime>': True, u'datetime': u'2016-12-12T00:00:00'}
            elif isinstance(
                    submittedValue, dict) and '<datetime>' in submittedValue:
                input_value = StringToDate(submittedValue['datetime'], format=None)
            # check if date only:
            elif len(submittedValue) == 10:
                input_value = StringToDate(submittedValue, '%Y-%m-%d')
            else:
                # calendar widget default format is '%Y-%m-%d %H:%M' and
                # might use the AM/PM format
                if submittedValue[-2:] in ['AM', 'PM']:
                    input_value = StringToDate(submittedValue, '%Y-%m-%d %I:%M %p')
                else:
                    input_value = StringToDate(submittedValue, '%Y-%m-%d %H:%M')
            return input_value
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
            try:
                if self.context.widget == 'SERVER':
                    # widget == 'SERVER' have a fix format, can't guess it
                    fieldValue = StringToDate(fieldValue, fmt, guess=False)
                else:
                    fieldValue = StringToDate(fieldValue, fmt)
            except ValueError:
                # fieldValue could be not valid datetime string
                return fieldValue

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

# -*- coding: utf-8 -*-
import json

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

from Products.CMFPlomino.utils import DatetimeToJS
from Products.CMFPlomino.utils import StringToDate


@provider(IFormFieldProvider)
class IDatetimeField(model.Schema):
    """DateTime field schema"""

    widget = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Default", "SERVER"),
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
        required=False)

# bug in plone.autoform means order_after doesn't moves correctly
IDatetimeField.setTaggedValue(ORDER_KEY,
                              [('widget', 'after', 'field_type'),
                               ('format', 'after', ".widget"),
                               ('startingyear', 'after', ".format")])


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
        submittedValue = submittedValue.strip()
        try:
            # check if date only:
            if len(submittedValue) == 10:
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
        except Exception:
            # with datagrid, we might get dates formatted differently than
            # using calendar widget default format
            return StringToDate(submittedValue[:16], '%Y-%m-%dT%H:%M')

    def getFieldValue(self, form, doc=None, editmode_obsolete=False,
                      creation=False, request=None):
        """Get date time field value"""
        fieldValue = BaseField.getFieldValue(
            self, form, doc, editmode_obsolete, creation, request)

        mode = self.context.field_mode
        if (mode == "EDITABLE" and
            request and
            ((doc is None and not(creation)) or
                'Plomino_datagrid_rowdata' in request)):
            fieldname = self.context.id
            fieldValue = request.get(fieldname, fieldValue)

        if fieldValue and isinstance(fieldValue, basestring):
            fmt = self.format
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

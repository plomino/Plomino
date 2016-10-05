# -*- coding: utf-8 -*-

from DateTime import DateTime
from plone.autoform.interfaces import IFormFieldProvider, ORDER_KEY
from plone.supermodel import directives, model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary
from ZPublisher.HTTPRequest import record

from .. import _
from ..utils import StringToDate
from base import BaseField

import logging

logger = logging.getLogger('Plomino')

@provider(IFormFieldProvider)
class IDatetimeField(model.Schema):
    """ DateTime field schema
    """

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
                                ('startingyear', 'after', ".format"),
                               ]
)


@implementer(IDatetimeField)
class DatetimeField(BaseField):
    """
    """

    read_template = PageTemplateFile('datetime_read.pt')
    edit_template = PageTemplateFile('datetime_edit.pt')

    def validate(self, submittedValue):
        """
        """
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
                submittedValue = '%s-%s-%s' % (year, month, day)
                if year and month and day:
                    # Don't allow StringToDate to guess the format
                    StringToDate(submittedValue, '%Y-%m-%d', guess=False, tozone=False)
                else:
                    # The record instance isn't valid
                    raise
            # submittedValue could be dict from tojson
            # {u'<datetime>': True, u'datetime': u'2016-12-12T00:00:00'}
            elif isinstance(submittedValue, dict) and '<datetime>' in submittedValue:
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
        except:
            fieldname = self.context.id
            errors.append(
                "%s must be a date/time (submitted value was: %s)" % (
                    fieldname,
                    submittedValue))
        return errors

    def processInput(self, submittedValue):
        """
        """
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
                submittedValue = '%s-%s-%s' % (year, month, day)
                if year and month and day:
                    # Don't allow StringToDate to guess the format
                    d = StringToDate(submittedValue, '%Y-%m-%d', guess=False, tozone=False)
                else:
                    # The record instance isn't valid
                    raise
            # submittedValue could be dict from tojson
            # {u'<datetime>': True, u'datetime': u'2016-12-12T00:00:00'}
            elif isinstance(submittedValue, dict) and '<datetime>' in submittedValue:
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
        except:
            # with datagrid, we might get dates formatted differently than
            # using calendar widget default format
            return StringToDate(submittedValue[:16], '%Y-%m-%dT%H:%M')

    def getFieldValue(self, form, doc=None, editmode_obsolete=False,
            creation=False, request=None):
        """
        """
        fieldValue = BaseField.getFieldValue(
            self, form, doc, editmode_obsolete, creation, request)

        mode = self.context.field_mode
        if (mode == "EDITABLE" and
            request and
            ((doc is None and not(creation)) or
                'Plomino_datagrid_rowdata' in request)):
            fieldname = self.context.id
            fieldValue = request.get(fieldname, fieldValue)

        if not fieldValue and doc.id == "TEMPDOC":
            # need to special handle datetime in macro pop up dialog
            # the request value is from json format
            # fieldName[<datetime>]:"true"
            # fieldName[datetime]:"1999-12-30T23:00:00+10:00"
            fieldName = self.context.id
            is_fieldNameDatetime = "{}[<datetime>]".format(fieldName)
            logger.info('Method: getFieldValue guess')
            if request.get(is_fieldNameDatetime, "").lower() == "true":
                fieldNameDatetime = "{}[datetime]".format(fieldName)
                logger.info('Method: getFieldValue guess {}'.format(
                    fieldName))
                fieldValue = StringToDate(
                    request.get(fieldNameDatetime), format=None)
                logger.info('Method: getFieldValue value {}'.format(
                    fieldValue))

        if fieldValue and isinstance(fieldValue, basestring):
            fmt = self.context.format
            if not fmt:
                fmt = form.getParentDatabase().datetime_format
            fieldValue = StringToDate(fieldValue, fmt)

        return fieldValue

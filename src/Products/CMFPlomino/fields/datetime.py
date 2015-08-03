# -*- coding: utf-8 -*-

from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import directives, model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from .. import _
from ..utils import StringToDate
from base import BaseField


@provider(IFormFieldProvider)
class IDatetimeField(model.Schema):
    """ DateTime field schema
    """

    directives.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=('widget', 'format', 'startingyear'),
    )

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


@implementer(IDatetimeField)
class DatetimeField(BaseField):
    """
    """

    read_template = PageTemplateFile('datetime_read.pt')
    edit_template = PageTemplateFile('datetime_edit.pt')

    def validate(self, submittedValue):
        """
        """
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
                fmt = self.context.getParentDatabase().datetime_format
            return StringToDate(submittedValue, fmt)

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

        if fieldValue and isinstance(fieldValue, basestring):
            fmt = self.format
            if not fmt:
                fmt = form.getParentDatabase().datetime_format
            fieldValue = StringToDate(fieldValue, fmt)
        return fieldValue

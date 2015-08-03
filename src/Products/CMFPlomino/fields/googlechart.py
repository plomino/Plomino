# -*- coding: utf-8 -*-

from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import directives, model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from .. import _
from base import BaseField


@provider(IFormFieldProvider)
class IGooglechartField(model.Schema):
    """ Google chart field schema
    """

    directives.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=('editrows', ),
    )

    editrows = schema.TextLine(
        title=u'Rows',
        description=u'Size of the editable text area',
        default=u"6",
        required=False)


@implementer(IGooglechartField)
class GooglechartField(BaseField):
    """
    """

    read_template = PageTemplateFile('googlechart_read.pt')
    edit_template = PageTemplateFile('googlechart_edit.pt')

    def validate(self, submittedValue):
        """
        """
        errors = []
        # no validation needed (we do not want to parse the GoogleChart
        # param)
        return errors

    def processInput(self, submittedValue):
        """
        """
        lines = submittedValue.replace('\r', '').split('\n')
        params = {}
        for l in lines:
            if "=" in l:
                (key, value) = l.split('=')
            else:
                key = l
                value = ''
            params[key] = value
        return params

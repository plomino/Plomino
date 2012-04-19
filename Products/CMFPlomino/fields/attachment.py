# -*- coding: utf-8 -*-
#
# File: attachment.py
#
# Copyright (c) 2009 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields, Choice
from zope.schema.vocabulary import SimpleVocabulary
from dictionaryproperty import DictionaryProperty

from base import IBaseField, BaseField, BaseForm

class IAttachmentField(IBaseField):
    """ Attachment field schema
    """
    type = Choice(vocabulary=SimpleVocabulary.fromItems([("Single file", "SINGLE"),
                                                           ("Multiple files", "MULTI")
                                                           ]),
                    title=u'Type',
                    description=u'Single or multiple file(s)',
                    default="MULTI",
                    required=True)
    
class AttachmentField(BaseField):
    """
    """
    implements(IAttachmentField)


for f in getFields(IAttachmentField).values():
    setattr(AttachmentField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IAttachmentField)
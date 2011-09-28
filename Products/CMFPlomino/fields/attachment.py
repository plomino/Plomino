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
from zope.schema import getFields

from dictionaryproperty import DictionaryProperty


from base import IBaseField, BaseField

class IAttachmentField(IBaseField):
    """
    Number field schema
    """

class AttachmentField(BaseField):
    """
    """
    implements(IAttachmentField)


for f in getFields(IAttachmentField).values():
    setattr(AttachmentField, f.getName(), DictionaryProperty(f, 'parameters'))

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

# Zope
from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields, Choice
from zope.schema.vocabulary import SimpleVocabulary

# CMF / Archetypes / Plone
from Products.CMFPlone.utils import normalizeString

# Plomino
from base import IBaseField, BaseField, BaseForm
from dictionaryproperty import DictionaryProperty


class IAttachmentField(IBaseField):
    """ Attachment field schema
    """
    type = Choice(
            vocabulary=SimpleVocabulary.fromItems(
                [("Single file", "SINGLE"), ("Multiple files", "MULTI") ]),
                title=u'Type',
                description=u'Single or multiple file(s)',
                default="MULTI",
                required=True)


class AttachmentField(BaseField):
    """
    """
    implements(IAttachmentField)

    def processInput(self, strValue):
        """
        """
        # only called in during validation
        if not strValue:
            return None
        strValue = normalizeString(strValue)
        return {strValue: 'application/unknown'}

    def getFieldValue(self, form, doc=None, editmode_obsolete=False,
            creation=False, request=None):
        "XXX TODO I expected to be able to return the data here"
        usable_request = request or self.context.REQUEST
        if '_has_session_uploads' in usable_request:
            formfield_name = '_uploaded_in_session_' + self.context.id
            import pdb; pdb.set_trace()
            file_ids = usable_request.form[formfield_name]
            if not isinstance(file_ids, list):
                file_ids = [file_ids]
            files_info = []
            for file_id in file_ids:
                file_data = usable_request.SESSION[file_id]['data']
                filename = usable_request.SESSION[file_id]['filename']
                content_type = 'text/plain' # XXX TODO find file content type
                doc.setItem(self.context.id, file_data)
                files_info.append({filename: content_type})
            return files_info
        value = super(AttachmentField, self).getFieldValue(form, doc, editmode_obsolete, creation, request)
        return value


for f in getFields(IAttachmentField).values():
    setattr(AttachmentField,
            f.getName(),
            DictionaryProperty(f, 'parameters'))


class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IAttachmentField)

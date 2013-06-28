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

from StringIO import StringIO

# Zope
from ZPublisher.HTTPRequest import FileUpload
from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields, Choice
from zope.schema.vocabulary import SimpleVocabulary

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

    def store_file(self, doc, filecontents, filename):
        current_files = doc.getItem(self.context.id) or {}
        fileobj = StringIO(filecontents)
        fileobj.filename = filename
        new_filename, content_type = doc.setfile(fileobj)
        if self.type == "SINGLE":
            for old_filename in doc.getItem(self.context.id):
                if old_filename != filename:
                    doc.deletefile(filename)
        current_files[new_filename] = content_type
        doc.setItem(self.context.id, current_files)
        return current_files

    def process_value(self, doc, value):
        """ Process `value` and calls store_file as appropriate
        Figures out if `value` is a field or a reference to a file earlier
        stored in user session.
        """
        current_files = doc.getItem(self.context.id) or {}
        if isinstance(value, FileUpload) and value.filename:
            current_files = self.store_file(doc, value.read(), value.filename)
        else:
            # Either no file was passed or we have some stored in SESSION
            if '_has_session_uploads' in self.context.REQUEST.form:
                fileid_fieldname = '_uploaded_in_session_' + self.context.id
                sessionid = self.context.REQUEST.form[fileid_fieldname]
                filecontents = self.context.REQUEST.SESSION[sessionid]['data']
                filename = self.context.REQUEST.SESSION[sessionid]['filename']
                current_files = self.store_file(doc, filecontents, filename)
        return current_files


for f in getFields(IAttachmentField).values():
    setattr(AttachmentField,
            f.getName(),
            DictionaryProperty(f, 'parameters'))


class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(IAttachmentField)

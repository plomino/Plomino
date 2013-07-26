# -*- coding: utf-8 -*-
#
# File: base.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'

# stdlib
from urllib import unquote

# 3rd party
from jsonutil import jsonutil as json

# Zope
from zope.interface import Interface, implements
from zope.annotation.interfaces import IAnnotations
from Acquisition import aq_base
try:
    from five.formlib.formbase import EditForm
except:
    #PLONE 3
    from Products.Five.formlib.formbase import EditForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

# Plomino
from Products.CMFPlomino.PlominoUtils import asUnicode
from Products.CMFPlomino.PlominoDocument import TemporaryDocument


class IBaseField(Interface):
    """
    """


class BaseField(object):
    """
    """
    implements(IBaseField)

    def __init__(self, context):
        """Initialize adapter."""
        self.context = context
        # get annotation to store param values
        annotations = IAnnotations(context)
        self.parameters = annotations.get("PLOMINOFIELDCONFIG", None)
        # allow access
        self.__allow_access_to_unprotected_subobjects__ = True

    def validate(self, strValue):
        """
        """
        errors = []
        return errors

    def processInput(self, strValue):
        """
        """
        if type(strValue) == str:
            strValue = strValue.decode('utf-8')
        return strValue

    def getSelectionList(self, doc):
        """
        """
        return None

    def getFieldValue(self, form, doc=None, editmode_obsolete=False,
            creation=False, request=None):
        """ Return the field as rendered by ``form`` on ``doc``.

        """
        # XXX: The editmode_obsolete parameter is unused.
        fieldName = self.context.id
        mode = self.context.getFieldMode()

        db = self.context.getParentDatabase()
        if doc is None:
            target = form
        else:
            target = doc

        fieldValue = None
        # XXX This is super-ugly, sorry. The reason I do this is that
        # I changed some logic upper in the call chain to give a
        # properly populated TemporaryDocument to hideWhens
        # to avoid users coding defensively with unneeded
        # try: catch blocks.
        # A proper solution would probably be to factor out the logic
        # that finds a field value and use that logic to populate
        # the TemporaryDocument.
        # But *right now* (that is better than never) I see this solution
        # works without breaking any test.
        temporary_doc_in_overlay = (
            isinstance(aq_base(doc), TemporaryDocument) and
            hasattr(self.context, 'REQUEST') and
            'Plomino_Parent_Form' in self.context.REQUEST.form and not
            self.context.REQUEST.get('ACTUAL_URL').endswith('/createDocument')
            )
        if temporary_doc_in_overlay:
            request = self.context.REQUEST
        if mode == "EDITABLE":
            if doc is None or creation or temporary_doc_in_overlay:
                # The aforementioned ugliness ends here
                if self.context.Formula():
                    fieldValue = form.computeFieldValue(fieldName, target)
                elif request is None:
                    fieldValue = ""
                else:
                    row_data_json = request.get("Plomino_datagrid_rowdata", None)
                    if row_data_json is not None:
                        # datagrid form case
                        parent_form = request.get(
                                "Plomino_Parent_Form", None)
                        parent_field = request.get(
                                "Plomino_Parent_Field", None)
                        data = json.loads(
                                unquote(
                                    row_data_json).decode(
                                        'raw_unicode_escape'))
                        datagrid_fields = (
                                db.getForm(parent_form)
                                .getFormField(parent_field)
                                .getSettings()
                                .field_mapping.split(','))
                        if fieldName in datagrid_fields:
                            fieldValue = data[
                                    datagrid_fields.index(fieldName)]
                        else:
                            fieldValue = ""
                    else:
                        # if no doc context and no default formula, we accept
                        # value passed in the REQUEST so we look for 'fieldName'
                        # but also for 'fieldName_querystring' which allows to
                        # pass value via the querystring without messing the
                        # POST content
                        request_value = request.get(fieldName, '')
                        if not request_value:
                            request_value = request.get(
                                fieldName + '_querystring',
                                ''
                            )
                        fieldValue = asUnicode(request_value)
            else:
                fieldValue = doc.getItem(fieldName)

        elif mode in ["DISPLAY", "COMPUTED"]:
            if mode == "DISPLAY" and not self.context.Formula() and doc:
                fieldValue = doc.getItem(fieldName)
            else:
                fieldValue = form.computeFieldValue(fieldName, target)

        elif mode == "CREATION":
            if creation:
                # Note: on creation, there is no doc, we use form as target
                # in formula
                fieldValue = form.computeFieldValue(fieldName, form)
            else:
                fieldValue = doc.getItem(fieldName)

        elif mode == "COMPUTEDONSAVE" and doc:
            fieldValue = doc.getItem(fieldName)

        if fieldValue is None:
            fieldValue = ""

        return fieldValue


class BaseForm(EditForm):
    """
    """

    template = ViewPageTemplateFile('settings_edit.pt')

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

from zope.interface import Interface, implements
from zope.annotation.interfaces import IAnnotations
from Acquisition import aq_base

from Products.CMFPlomino.PlominoUtils import asUnicode
from Products.CMFPlomino.PlominoDocument import TemporaryDocument
try:
    from five.formlib.formbase import EditForm
except:
    #PLONE 3
    from Products.Five.formlib.formbase import EditForm

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from jsonutil import jsonutil as json

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
        errors=[]
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

    def getFieldValue(self, form, doc, editmode, creation, request):
        """
        """
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
            'Plomino_Parent_Form' in self.context.REQUEST.form
        )
        if temporary_doc_in_overlay:
            request = self.context.REQUEST
        if mode=="EDITABLE":
            if doc is None or temporary_doc_in_overlay:
                # The aforemntioned ugliness ends here
                if creation and self.context.Formula():
                    fieldValue = form.computeFieldValue(fieldName, target)
                elif request is None:
                    fieldValue = ""
                else:
                    row_data_json = request.get("Plomino_datagrid_rowdata", None)
                    if row_data_json is not None:
                        # datagrid form case
                        parent_form = request.get("Plomino_Parent_Form", None)
                        parent_field = request.get("Plomino_Parent_Field", None)
                        data = json.loads(row_data_json)
                        datagrid_fields = db.getForm(parent_form).getFormField(parent_field).getSettings().field_mapping.split(',')
                        if fieldName in datagrid_fields:
                            fieldValue = data[datagrid_fields.index(fieldName)]
                        else:
                            fieldValue = ""
                    else:
                        fieldValue = asUnicode(request.get(fieldName, ''))
            else:
                fieldValue = doc.getItem(fieldName)

        if mode=="DISPLAY" or mode=="COMPUTED":
            fieldValue = form.computeFieldValue(fieldName, target)

        if mode=="CREATION":
            if creation:
                # Note: on creation, there is no doc, we use form as target
                # in formula
                fieldValue = form.computeFieldValue(fieldName, form)
            else:
                fieldValue = doc.getItem(fieldName)

        if mode=="COMPUTEDONSAVE" and doc:
            fieldValue = doc.getItem(fieldName)

        if fieldValue is None:
            fieldValue = ""
        return fieldValue

class BaseForm(EditForm):
    """
    """

    template = ViewPageTemplateFile('settings_edit.pt')
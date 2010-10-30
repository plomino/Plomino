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
from persistent.dict import PersistentDict

import simplejson as json

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
        if not self.parameters:
            annotations["PLOMINOFIELDCONFIG"] = PersistentDict()
            self.parameters = annotations["PLOMINOFIELDCONFIG"]
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
        if mode=="EDITABLE":
            if doc is None:
                if creation and not self.context.Formula()=="":
                    fieldValue = db.runFormulaScript("field_"+form.id+"_"+fieldName+"_formula", target, self.context.Formula)
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
                        fieldValue = data[datagrid_fields.index(fieldName)]
                    else: 
                        fieldValue = request.get(fieldName, '')
            else:
                fieldValue = doc.getItem(fieldName)

        if mode=="DISPLAY" or mode=="COMPUTED":
            fieldValue = db.runFormulaScript("field_"+form.id+"_"+fieldName+"_formula", target, self.context.Formula)

        if mode=="CREATION":
            if creation:
                # Note: on creation, there is no doc, we use self as param
                # in formula
                fieldValue = db.runFormulaScript("field_"+form.id+"_"+fieldName+"_formula", form, self.context.Formula)
            else:
                fieldValue = doc.getItem(fieldName)
        
        if fieldValue is None:
            fieldValue = ""
        return fieldValue
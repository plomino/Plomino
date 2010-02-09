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
        return strValue
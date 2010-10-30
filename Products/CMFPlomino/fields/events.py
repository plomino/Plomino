# -*- coding: utf-8 -*-
#
# File: datetime.py
#
# Copyright (c) 2009 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'


def afterFieldModified(obj, event):
    """
    """
    obj.cleanFormulaScripts("field_"+obj.getPhysicalPath()[-2]+"_"+obj.id)
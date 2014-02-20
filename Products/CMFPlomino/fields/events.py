# -*- coding: utf-8 -*-
#
# File: events.py
#
# Copyright (c) 2009 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from Products.CMFPlomino.AppConfig import SCRIPT_ID_DELIMITER

def afterFieldModified(obj, event):
    """
    """
    obj.cleanFormulaScripts(SCRIPT_ID_DELIMITER.join(["field", obj.getPhysicalPath()[-2], obj.id]))

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

from Products.CMFPlomino.AppConfig import SCRIPTID_DELIMITER

def afterFieldModified(obj, event):
    """
    """
    obj.cleanFormulaScripts(SCRIPTID_DELIMITER.join(["field", obj.getPhysicalPath()[-2], obj.id]))

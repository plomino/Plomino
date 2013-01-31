# -*- coding: utf-8 -*-
#
# File: events.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Xavier PERROT <xavier.perrot@makina-corpus.com>"""
__docformat__ = 'plaintext'


def PlominoDocumentRemoveEventHandler(obj, event):
    """ Remove event handler for Plomino documents.
    Comments from plone/app/linkintegrity/handlers.py
    """
    # if the object the event was fired on doesn't have a `REQUEST` attribute
    # we can safely assume no direct user action was involved and therefore
    # never raise a link integrity exception...
    # (this should also fix http://plone.org/products/cachefu/issues/86)
    #if not hasattr(obj, 'REQUEST'):
    #    return

    # since the event gets called for every subobject before it's
    # called for the item deleted directly via _delObject (event.object)
    # itself, but we do not want to present the user with a confirmation
    # form for every (referred) subobject, so we remember and skip them...
    #if obj is not event.object:
    #    return

    #TODO : test if deletion confirmation has been done, and unindex document
    #TODO : find how to know if confirmation has been done
    #return
    pass

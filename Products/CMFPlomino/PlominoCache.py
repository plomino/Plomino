# -*- coding: utf-8 -*-
#
# File: PlominoCache.py
#
# Copyright (c) 2011 by ['Eric BREHAULT']
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.CMFPlomino.config import *

schema = Schema((

    StringField(
        name='id',
        widget=StringField._properties['widget'](
            label="Id",
            description="The cache fragment id",
            label_msgid='CMFPlomino_label_cache_id',
            description_msgid='CMFPlomino_help_cache_id',
            i18n_domain='CMFPlomino',
        ),
    ),
    TextField(
        name='Formula',
        widget=TextAreaWidget(
            label="Formula",
            description="Returns the cache key (if None, no cache)",
            label_msgid='CMFPlomino_label_CacheFormula',
            description_msgid='CMFPlomino_help_CacheFormula',
            i18n_domain='CMFPlomino',
        ),
    ),
),
)

PlominoCache_schema = BaseSchema.copy() + \
    schema.copy()

class PlominoCache(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoCache)

    meta_type = 'PlominoCache'
    _at_rename_after_creation = False

    schema = PlominoCache_schema

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        """
        """
        self.cleanFormulaScripts("cache_"+self.getParentNode().id+"_"+self.id)


registerType(PlominoCache, PROJECTNAME)
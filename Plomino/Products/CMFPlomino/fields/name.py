# -*- coding: utf-8 -*-
#
# File: name.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT <eric.brehault@makina-corpus.com>"""
__docformat__ = 'plaintext'

from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields
from zope.schema import TextLine, Text, List, Choice
from zope.schema.vocabulary import SimpleVocabulary
from dictionaryproperty import DictionaryProperty

from Products.Five.formlib.formbase import EditForm
from Products.CMFCore.utils import getToolByName

from base import IBaseField, BaseField

class INameField(IBaseField):
    """
    Name field schema
    """
    type = Choice(vocabulary=SimpleVocabulary.fromItems([("Single valued", "SINGLE"),
                                                           ("Multi valued", "MULTI")
                                                           ]),
                    title=u'Type',
                    description=u'Single or multi valued name field',
                    default="SINGLE",
                    required=True)
    restricttogroup = TextLine(title=u'Restrict to group',
                      description=u'The field will only display member of the following group. Empty = no group restriction.',
                      required=False)
    separator = TextLine(title=u'Separator',
                      description=u'Only apply if multi-valued',
                      required=False)
    
class NameField(BaseField):
    """
    """
    implements(INameField)
    
    def getNamesList(self):
        """return a list, format: fullname|userid
        """
        if self.restricttogroup and self.restricttogroup != '':
            group = self.context.portal_groups.getGroupById(self.restricttogroup)
            if group is not None:
                all = [(m.getProperty('id'), m.getProperty("fullname")) for m in group.getGroupMembers()]
            else:
                all = []
        elif not(self.context.getParentDatabase().getDoNotListUsers()):
            all = [(m.getId(), m.getProperty("fullname")) for m in self.context.getPortalMembers()]
        else:
            return None
        s=['|']
        for m in all:
            if m[1]=='':
                s.append(m[0]+'|'+m[0])
            else:
                s.append(m[1]+'|'+m[0])
        return s
    
    def getFullname(self, userid):
        """ return member fullname if available
        """
        if userid is None or userid == "":
            return ''
        user=getToolByName(self.context, 'portal_membership').getMemberById(userid)
        if not(user is None):
            fullname=user.getProperty('fullname')
            if fullname=='':
                return userid
            else:
                return fullname
        else:
            return userid
        
for f in getFields(INameField).values():
    setattr(NameField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(EditForm):
    """
    """
    form_fields = form.Fields(INameField)
    
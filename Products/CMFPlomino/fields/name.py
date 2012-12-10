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

# stdlib
import logging
logger = logging.getLogger('Plomino')

# Zope
from zope.formlib import form
from zope.interface import implements
from zope.schema import getFields
from zope.schema import TextLine, Text, List, Choice
from zope.schema.vocabulary import SimpleVocabulary

# 3rd party
from jsonutil import jsonutil as json

# CMF
from Products.CMFCore.utils import getToolByName

# Plomino
from base import IBaseField, BaseField, BaseForm
from dictionaryproperty import DictionaryProperty

class INameField(IBaseField):
    """ Name field schema
    """
    type = Choice(
            vocabulary=SimpleVocabulary.fromItems(
                [("Single valued", "SINGLE"),
                    ("Multi valued", "MULTI")]),
                title=u'Type',
                description=u'Single or multi-valued name field',
                default="SINGLE",
                required=True)
    selector = Choice(
            vocabulary=SimpleVocabulary.fromItems(
                [("Select in a list", "LIST"),
                    ("Fill a field", "FIELD"),
                    ("Search", "SEARCH")]),
                title=u'Selection mode',
                description=u'How the name is selected',
                default="LIST",
                required=True)
    restricttogroup = TextLine(
                title=u'Restrict to group',
                description=u'The field will only display members of the specified group (empty = no group restriction)',
                required=False)
    separator = TextLine(
                title=u'Separator',
                description=u'Only apply if multiple values will be displayed',
                required=False)

class NameField(BaseField):
    """ Field representing a Plomino user's name.
    """
    implements(INameField)

    def _getNamesIds(self):
        """ Return Plone members as [(name, userid), ...]

        Honor the restricttogroup field and the portal's DoNotListUsers
        property.
        """
        if self.restricttogroup:
            group = self.context.portal_groups.getGroupById(self.restricttogroup)
            if group:
                names_ids = [(m.getProperty("fullname"), m.getProperty('id')) for m in group.getGroupMembers()]
            else:
                return []
        elif self.context.getParentDatabase().getDoNotListUsers():
            return None
        else:
            names_ids = [(m.getProperty("fullname"), m.getId()) for m in self.context.getPortalMembers()]

        names_ids.sort(key=lambda (username, userid): username.lower())
        return names_ids

    def getSelectionList(self, doc=None):
        """ Fullname/ID list in selectionlist format: fullname|userid
        """
        names_ids = self._getNamesIds()
        s=['|']
        for username, userid in names_ids:
            if not username:
                s.append(userid+'|'+userid)
            else:
                s.append(username+'|'+userid)
        return s

    def getFullname(self, userid):
        """ Return member fullname if available
        """
        if not userid:
            return ''

        mt = getToolByName(self.context, 'portal_membership')
        user = mt.getMemberById(userid)
        if user:
            fullname = user.getProperty('fullname')
            if fullname:
                return fullname
            else:
                return userid
        else:
            logger.debug("Looking up full name for nonexistent member.")
            return userid

    def getFilteredNames(self, filter):
        """ Return a JSON list of users, filtered by id or name.
        """
        names_ids = self._getNamesIds()
        if filter:
            names_ids = [
                    (username, userid) for (username, userid) in names_ids
                    if filter in username or filter in userid]

        return json.dumps(names_ids)

for f in getFields(INameField).values():
    setattr(NameField, f.getName(), DictionaryProperty(f, 'parameters'))

class SettingForm(BaseForm):
    """
    """
    form_fields = form.Fields(INameField)


# -*- coding: utf-8 -*-

from jsonutil import jsonutil as json
from plone import api
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import directives, model
from zope.interface import implementer, provider
from zope.pagetemplate.pagetemplatefile import PageTemplateFile
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary

from .. import _
from base import BaseField


@provider(IFormFieldProvider)
class INameField(model.Schema):
    """ Name field schema
    """

    directives.fieldset(
        'settings',
        label=_(u'Settings'),
        fields=('type', 'selector', 'restricttogroup', 'separator', ),
    )

    type = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Single valued", "SINGLE"),
            ("Multi valued", "MULTI")
        ]),
        title=u'Type',
        description=u'Single or multi-valued name field',
        default="SINGLE",
        required=True)

    selector = schema.Choice(
        vocabulary=SimpleVocabulary.fromItems([
            ("Select in a list", "LIST"),
            ("Fill a field", "FIELD"),
        ]),
        title=u'Selection mode',
        description=u'How the name is selected',
        default="LIST",
        required=True)

    restricttogroup = schema.TextLine(
        title=u'Restrict to group',
        description=u'The field will only display members of the specified'
        ' group (empty = no group restriction)',
        required=False)

    separator = schema.TextLine(
        title=u'Separator',
        description=u'Only apply if multiple values will be displayed',
        required=False)


@implementer(INameField)
class NameField(BaseField):
    """
    """

    read_template = PageTemplateFile('name_read.pt')
    edit_template = PageTemplateFile('name_edit.pt')

    def _getNamesIds(self):
        """ Return Plone members as [(name, userid), ...]

        Honor the restricttogroup field and the portal's do_not_list_users
        property.
        """
        if self.context.restricttogroup:
            group = self.context.portal_groups.getGroupById(
                self.context.restricttogroup)
            if group:
                names_ids = [
                    (m.getProperty("fullname"), m.getProperty('id'))
                    for m in group.getGroupMembers()]
            else:
                return []
        elif self.context.getParentDatabase().do_not_list_users:
            return None
        else:
            names_ids = [
                (m.getProperty("fullname"), m.getId())
                for m in self.context.getPortalMembers()]

        names_ids.sort(key=lambda (username, userid): username.lower())
        return names_ids

    def getSelectionList(self, doc=None):
        """ Fullname/ID list in selectionlist format: fullname|userid
        """
        names_ids = self._getNamesIds()
        if not names_ids:
            return None
        s = ['|']
        for username, userid in names_ids:
            if not username:
                s.append("%s|%s" % (userid, userid))
            else:
                s.append("%s|%s" % (username, userid))
        return s

    def getFullname(self, userid):
        """ Return member fullname if available
        """
        if not userid:
            return ''

        mt = api.portal.get().portal_membership
        user = mt.getMemberById(userid)
        if user:
            fullname = user.getProperty('fullname')
            if fullname:
                return fullname
            else:
                return userid
        else:
            return userid

    def getFilteredNames(self, filter):
        """ Return a JSON list of users, filtered by id or name.
        """
        names_ids = self._getNamesIds()
        if filter:
            names_ids = [
                {'id': userid, 'text': username}
                for (username, userid) in names_ids[:20]
                if filter.lower() in username.lower()
                or filter.lower() in userid.lower()]

        return json.dumps(
            {'results': names_ids, 'total': len(names_ids)})

    def getCurrent(self, values):
        if isinstance(values, basestring):
            values = [values]
        return ["%s:%s" % (id, self.getFullname(id)) for id in values]

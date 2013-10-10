# -*- coding: utf-8 -*-
#
# File: PlominoAgent.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# Zope Public License (ZPL)
#

__author__ = """Eric BREHAULT and Xavier PERROT <eric.brehault@makina-corpus.org>"""
__docformat__ = 'plaintext'

# Standard

# Third party
try:
    from plone.app.async.interfaces import IAsyncService
    ASYNC = True
except:
    ASYNC = False

# Zope
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import newSecurityManager
from zope.component import getUtility
from zope.interface import implements

# CMF / Archetypes / Plone
from Products.Archetypes.atapi import *
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

# Plomino
from exceptions import PlominoScriptException
from Products.CMFPlomino.config import *
from Products.CMFPlomino.browser import PlominoMessageFactory as _
import interfaces

schema = Schema((
    StringField(
        name='id',
        widget=StringField._properties['widget'](
            label="Id",
            description="The agent id",
            label_msgid=_('CMFPlomino_label_agent_id', default="Id"),
            description_msgid=_('CMFPlomino_help_agent_id', default="The agent id"),
            i18n_domain='CMFPlomino',
        ),
    ),
    TextField(
        name='Content',
        widget=TextAreaWidget(
            label="Code",
            description="Code to execute",
            label_msgid=_("CMFPlomino_label_AgentContent", default="Code to execute"),
            description_msgid=_("CMFPlomino_help_AgentContent", default='Code to execute'),
            i18n_domain='CMFPlomino',
            rows=25,
        ),
    ),
    StringField(
        name='RunAs',
        default="CURRENT",
        widget=SelectionWidget(
            label="Run as",
            description="Run the agent using current user access rights, or using the developer access rights.",
            label_msgid=_('CMFPlomino_label_AgentRunAs', default="Run as"),
            description_msgid=_('CMFPlomino_help_AgentRunAs', default='Run the agent using current user access rights, or using the developer access rights.'),
            i18n_domain='CMFPlomino',
        ),
        vocabulary=[
            ["CURRENT", "Current user"],
            ["OWNER", "Agent owner"]],
    ),
),
)

PlominoAgent_schema = BaseSchema.copy() + schema.copy()


def run_async(context, *args, **kwargs):
    # for async call
    context.runAgent(*args, **kwargs)


class PlominoAgent(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoAgent)

    meta_type = 'PlominoAgent'
    _at_rename_after_creation = False

    schema = PlominoAgent_schema

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        """
        """
        self.cleanFormulaScripts("agent_" + self.id)

    def __call__(self, *args):
        """
        """
        plominoContext = self
        try:
            if self.getRunAs() == "OWNER":

                # Remember the current user
                member = self.getCurrentMember()
                if member.__class__.__name__ == "SpecialUser":
                    user = member
                else:
                    user = member.getUser()

                # Switch to the agent's owner
                owner = self.getOwner()
                newSecurityManager(None, owner)

            result = self.runFormulaScript(
                    "agent_"+self.id,
                    plominoContext,
                    self.Content,
                    True,
                    *args)

            # Switch back to the original user
            if self.getRunAs() == "OWNER":
                newSecurityManager(None, user)

        except PlominoScriptException, e:
            e.reportError('Agent failed')
            result = None

        return result

    security.declarePublic('runAgent')
    def runAgent(self, *args, **kwargs):
        """ Execute the agent formula.
        """
        plominoContext = self
        plominoReturnURL = self.getParentDatabase().absolute_url()
        request = getattr(self, 'REQUEST', None)
        try:
            if self.getRunAs() == "OWNER":
                # Remember the current user
                member = self.getCurrentMember()
                if member.__class__.__name__ == "SpecialUser":
                    user = member
                else:
                    user = member.getUser()

                # Switch to the agent's owner
                owner = self.getOwner()
                newSecurityManager(None, owner)

            plominoReturnURL = self.runFormulaScript(
                    "agent_"+self.id,
                    plominoContext,
                    self.Content,
                    True,
                    *args)

            # Switch back to the original user
            if self.getRunAs() == "OWNER":
                newSecurityManager(None, user)

            if request and request.get('REDIRECT', False):
                request.RESPONSE.redirect(plominoReturnURL)

        except PlominoScriptException, e:
            # Exception logged already in runFormulaScript
            if request and request.get('RESPONSE'):
                request.RESPONSE.setHeader(
                        'content-type',
                        'text/plain; charset=utf-8')
            return e.message

    security.declarePublic('runAgent_async')
    def runAgent_async(context, *args, **kwargs):
        """ Run the agent in asynchronous mode.
        Pass a dictionary based on the current request.
        """
        request = dict(getattr(context, 'REQUEST', {}))
        if request:
            for k, v in request.items():
                if type(v) not in [str, unicode]:
                    del request[k]

        async = getUtility(IAsyncService)
        async.queueJob(
                run_async,
                context,
                original_request=request,
                *args,
                **kwargs)


registerType(PlominoAgent, PROJECTNAME)
# end of class PlominoAgent

##code-section module-footer #fill in your manual code here
##/code-section module-footer

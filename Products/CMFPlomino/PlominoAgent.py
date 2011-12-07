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

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import newSecurityManager
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces
from zope.component import getUtility
try:
    from plone.app.async.interfaces import IAsyncService
    ASYNC = True
except:
    ASYNC = False
    
from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from exceptions import PlominoScriptException
from Products.CMFPlomino.config import *

schema = Schema((

    StringField(
        name='id',
        widget=StringField._properties['widget'](
            label="Id",
            description="The agent id",
            label_msgid='CMFPlomino_label_agent_id',
            description_msgid='CMFPlomino_help_agent_id',
            i18n_domain='CMFPlomino',
        ),
    ),
    TextField(
        name='Content',
        widget=TextAreaWidget(
            label="Code",
            description="Code to execute",
            label_msgid="CMFPlomino_label_AgentContent",
            description_msgid="CMFPlomino_help_AgentContent",
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
            label_msgid='CMFPlomino_label_AgentRunAs',
            description_msgid='CMFPlomino_help_AgentRunAs',
            i18n_domain='CMFPlomino',
        ),
        vocabulary= [["CURRENT", "Current user"], ["OWNER", "Agent owner"]],
    ),
),
)

PlominoAgent_schema = BaseSchema.copy() + \
    schema.copy()
    
def run_async(context):
    # for async call
    context.runAgent()

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
        self.cleanFormulaScripts("agent_"+self.id)

    def __call__(self, *args):
        """
        """
        plominoContext = self
        try:
            if self.getRunAs() == "OWNER":
                owner = self.getOwner()
                # user = self.getCurrentUser()
                newSecurityManager(None, owner)

            result = self.runFormulaScript("agent_"+self.id, plominoContext, self.Content, True, *args)
            # if self.getRunAs() == "OWNER":
            #     newSecurityManager(None, user)
        except PlominoScriptException, e:
            e.reportError('Agent failed')
            result = None

        return result

    security.declarePublic('runAgent')
    def runAgent(self, REQUEST=None):
        """ Execute the agent formula.
        """
        plominoContext = self
        plominoReturnURL = self.getParentDatabase().absolute_url()
        if not REQUEST:
            REQUEST = getattr(self, 'REQUEST', None)
        try:
            if self.getRunAs() == "OWNER":
                user = self.getOwner()
                newSecurityManager(None, user)

            r=self.runFormulaScript("agent_"+self.id, plominoContext, self.Content)
            if (REQUEST != None) and (REQUEST.get('REDIRECT', None)== "True"):
                if r is not None:
                    plominoReturnURL=r
                REQUEST.RESPONSE.redirect(plominoReturnURL)
        except PlominoScriptException, e:
            if REQUEST:
                REQUEST.RESPONSE.setHeader('content-type', 'text/plain; charset=utf-8')
            return e.message

    security.declarePublic('runAgent_async')
    def runAgent_async(self):
        """run the agent in asynchronous mode
        """
        async = getUtility(IAsyncService)
        job = async.queueJob(run_async, self)
        
registerType(PlominoAgent, PROJECTNAME)
# end of class PlominoAgent

##code-section module-footer #fill in your manual code here
##/code-section module-footer




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
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.CMFPlomino.config import *

##code-section module-header #fill in your manual code here
from Products.Archetypes.public import *
from AccessControl.SecurityManagement import getSecurityManager, setSecurityManager, newSecurityManager
import transaction
##/code-section module-header

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
        ),
    ),
    BooleanField(
        name='Scheduled',
        widget=BooleanField._properties['widget'](
            label="Scheduled",
            description="Scheduled agent",
            label_msgid='CMFPlomino_label_Scheduled',
            description_msgid='CMFPlomino_help_Scheduled',
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='AgentUser',
        widget=StringField._properties['widget'](
            label="Agent user",
            description="Effective user used to run the agent",
            label_msgid='CMFPlomino_label_AgentUser',
            description_msgid='CMFPlomino_help_AgentUser',
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='Cron',
        default='* 1 * * *',
        widget=StringField._properties['widget'](
            label="Cron configuration",
            description="Format : crontab UNIX",
            label_msgid='CMFPlomino_label_Cron',
            description_msgid='CMFPlomino_help_Cron',
            i18n_domain='CMFPlomino',
        ),
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoAgent_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoAgent(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoAgent)

    meta_type = 'PlominoAgent'
    _at_rename_after_creation = True

    schema = PlominoAgent_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('at_post_create_script')
    def at_post_create_script(self):
        """
        """
        db = self.getParentDatabase()
        db.managePlominoCronTab()

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        """
        """
        self.cleanFormulaScripts("agent_"+self.id)
        #cron tab
        db = self.getParentDatabase()
        db.managePlominoCronTab()

    security.declarePublic('manage_beforeDelete')
    def manage_beforeDelete(self,item,container):
        """
        """
        #cron tab
        db = self.getParentDatabase()
        db.managePlominoCronTab(True)

    security.declarePublic('getParentDatabase')
    def getParentDatabase(self):
        """
        """
        return self.getParentNode()

    def __call__(self, *args):
        """
        """
        txn = transaction.get()
        plominoContext = self
        return self.runFormulaScript("agent_"+self.id, plominoContext, self.Content, True, *args)
        
    security.declarePublic('runAgent')
    def runAgent(self,REQUEST=None):
        """execute the python code
        """

        #acl = self.acl_users
        #newSecurityManager(None, acl.getUserById(str(self.AgentUser), None))
        txn = transaction.get()
        plominoContext = self
        plominoReturnURL = self.getParentDatabase().absolute_url()
        try:
            #RunFormula(plominoContext, "agent_"+self.id, self.Content())
            r=self.runFormulaScript("agent_"+self.id, plominoContext, self.Content)
            txn.commit()
            if (REQUEST != None) and (REQUEST.get('REDIRECT', None)== "True"):
                if r is not None:
                    plominoReturnURL=r
                REQUEST.RESPONSE.redirect(plominoReturnURL)
        except Exception, e:
            txn.abort()
            return "Error: %s \nCode->\n%s" % (e, self.Content())


registerType(PlominoAgent, PROJECTNAME)
# end of class PlominoAgent

##code-section module-footer #fill in your manual code here
##/code-section module-footer




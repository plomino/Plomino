# -*- coding: utf-8 -*-
#
# File: PlominoAction.py
#
# Copyright (c) 2008 by ['Eric BREHAULT']
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
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
from exceptions import PlominoScriptException

##code-section module-header #fill in your manual code here
from Products.Archetypes.public import *

ACTION_TYPES = [["OPENFORM", "Open form"], ["OPENVIEW", "Open view"], ["CLOSE", "Close"], ["SAVE", "Save"], ["PYTHON", "Python script"], ["REDIRECT", "Redirect formula"]]
ACTION_DISPLAY = [["LINK", "Link"], ["SUBMIT", "Submit button"], ["BUTTON", "Button"]]
##/code-section module-header

schema = Schema((

    StringField(
        name='id',
        widget=StringField._properties['widget'](
            label="Id",
            description="The action id",
            label_msgid='CMFPlomino_label_action_id',
            description_msgid='CMFPlomino_help_action_id',
            i18n_domain='CMFPlomino',
        ),
    ),
    StringField(
        name='ActionType',
        widget=SelectionWidget(
            label="Action type",
            description="Select the type for this action",
            label_msgid='CMFPlomino_label_ActionType',
            description_msgid='CMFPlomino_help_ActionType',
            i18n_domain='CMFPlomino',
        ),
        vocabulary=ACTION_TYPES,
    ),
    StringField(
        name='ActionDisplay',
        widget=SelectionWidget(
            label="Action display",
            description="How the action is shown",
            label_msgid='CMFPlomino_label_ActionDisplay',
            description_msgid='CMFPlomino_help_ActionDisplay',
            i18n_domain='CMFPlomino',
        ),
        vocabulary=ACTION_DISPLAY,
    ),
    TextField(
        name='Content',
        widget=TextAreaWidget(
            label="Parameter or code",
            description="Code or parameter depending on the action type",
            label_msgid='CMFPlomino_label_ActionContent',
            description_msgid='CMFPlomino_help_ActionContent',
            i18n_domain='CMFPlomino',
        ),
    ),
    TextField(
        name='Hidewhen',
        widget=TextAreaWidget(
            label="Hide-when formula",
            description="Action is hidden if formula return True",
            label_msgid='CMFPlomino_label_ActionHidewhen',
            description_msgid='CMFPlomino_help_ActionHidewhen',
            i18n_domain='CMFPlomino',
        ),
    ),
    BooleanField(
        name='InActionBar',
        default="1",
        widget=BooleanField._properties['widget'](
            label="Display action in action bar",
            description="Display action in action bar (yes/no)",
            label_msgid='CMFPlomino_label_ActionInActionBar',
            description_msgid='CMFPlomino_help_ActionInActionBar',
            i18n_domain='CMFPlomino',
        ),
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PlominoAction_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PlominoAction(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IPlominoAction)

    meta_type = 'PlominoAction'
    _at_rename_after_creation = False

    schema = PlominoAction_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declareProtected(READ_PERMISSION, 'executeAction')
    def executeAction(self, target, form_id):
        """return the action resulting url
        """
        db = self.getParentDatabase()
        if self.ActionType == "OPENFORM":
            formid = self.Content()
            return db.absolute_url() + '/' + formid + '/OpenForm'
        elif self.ActionType == "OPENVIEW":
            viewid = self.Content()
            return db.absolute_url() + '/' + viewid + '/OpenView'
        elif self.ActionType == "CLOSE":
            return db.absolute_url() + '/checkBeforeOpenDatabase'
        elif self.ActionType == "PYTHON":
            if target is None:
                targetid="None"
            else:
                targetid=target.id
            return self.absolute_url() + '/runScript?target=%s&form_id=%s'%(targetid, form_id)
        elif self.ActionType == "REDIRECT":
            try:
                redirecturl=self.runFormulaScript("action_"+self.getParentNode().id+"_"+self.id+"_script", target, self.Content, True, form_id)
                return str(redirecturl)
            except PlominoScriptException, e:
                return "javascript:alert(\"Error: %s\")" % ('formula error in redirect action ' + self.Title())
        else:
            return '.'

    security.declareProtected(READ_PERMISSION, 'runScript')
    def runScript(self, REQUEST):
        """execute the python code
        """
        db = self.getParentDatabase()
        target = REQUEST.get('target')
        form_id = REQUEST.get('form_id')
        if target == "None":
            plominoContext = db
        else:
            plominoContext = db.getDocument(target)
            if plominoContext is None:
                plominoContext = getattr(db, target, db)

        plominoReturnURL = plominoContext.absolute_url()
        try:
            #RunFormula(plominoContext, "action_"+self.getParentNode().id+"_"+self.id, self.Content())
            returnurl=self.runFormulaScript("action_"+self.getParentNode().id+"_"+self.id+"_script", plominoContext, self.Content, True, form_id)
            if returnurl is None or returnurl=='':
                returnurl=plominoReturnURL
            REQUEST.RESPONSE.redirect(returnurl)
        except PlominoScriptException, e:
            e.reportError('"%s" action failed' % self.Title())
            REQUEST.RESPONSE.redirect(plominoReturnURL)

    security.declarePublic('at_post_edit_script')
    def at_post_edit_script(self):
        """post edit
        """
        self.cleanFormulaScripts("action_"+self.getParentNode().id+"_"+self.id)


registerType(PlominoAction, PROJECTNAME)
# end of class PlominoAction

##code-section module-footer #fill in your manual code here
##/code-section module-footer




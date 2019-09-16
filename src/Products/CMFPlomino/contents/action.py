from AccessControl import ClassSecurityInfo
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.supermodel import directives as supermodel_directives
from plone.supermodel import model
from z3c.form.interfaces import NOT_CHANGED
from zope import schema
from zope.interface import implements
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from .. import _
from ..config import (
    ACTION_DISPLAY,
    ACTION_TYPES,
    READ_PERMISSION,
    SCRIPT_ID_DELIMITER,
)
from ..exceptions import PlominoScriptException

action_types = SimpleVocabulary([
    SimpleTerm(value=mode[0], title=_(mode[1])) for mode in ACTION_TYPES
])
action_displays = SimpleVocabulary([
    SimpleTerm(value=mode[0], title=_(mode[1])) for mode in ACTION_DISPLAY
])


class IPlominoAction(model.Schema):
    """ Plomino action schema
    """

    action_type = schema.Choice(
        title=_('CMFPlomino_label_ActionType',
            default="Select the type for this action"),
        description=_('CMFPlomino_help_ActionType',
            default='Select the type for this action'),
        required=True,
        vocabulary=action_types,
    )

    action_display = schema.Choice(
        title=_('CMFPlomino_label_ActionDisplay', default="Action display"),
        description=_('CMFPlomino_help_ActionDisplay',
            default="How the action is shown"),
        required=True,
        default='BUTTON',
        vocabulary=action_displays,
    )

    directives.widget('content', klass='plomino-formula')
    content = schema.Text(
        title=_('CMFPlomino_label_ActionContent', default='Parameter or code'),
        description=_('CMFPlomino_help_ActionContent',
            default='Code or parameter depending on the action type'),
        required=False,
        missing_value=NOT_CHANGED, # So settings won't nuke formulas in IDE
        default=u'',
    )

    directives.widget('hidewhen', klass='plomino-formula')
    hidewhen = schema.Text(
        title=_('CMFPlomino_label_ActionHidewhen',
            default="Action is hidden if formula returns True"),
        description=_('CMFPlomino_help_ActionHidewhen',
            default='Action is hidden if formula returns True'),
        required=False,
        missing_value=NOT_CHANGED, # So settings won't nuke formulas in IDE
        default=u'',
    )

    in_action_bar = schema.Bool(
        title=_('CMFPlomino_label_ActionInActionBar',
            default='Display action in action bar (yes/no)'),
        description=_('CMFPlomino_help_ActionInActionBar',
            default='Display action in action bar (yes/no)'),
        default=True,
        required=True,
    )

    directives.widget('html_attributes_formula', klass='plomino-formula')
    html_attributes_formula = schema.Text(
        title=_('CMFPlomino_label_HTMLAttributesFormula',
            default="HTML attributes formula"),
        description=_('CMFPlomino_help_HTMLAttributesFormula',
            default='Inject DOM attributes in the action tag'),
        required=False,
        missing_value=NOT_CHANGED, # So settings won't nuke formulas in IDE
        default=u'',
    )

    # ADVANCED
    supermodel_directives.fieldset(
        'advanced',
        label=_(u'Advanced'),
        fields=(
            'content',
            'hidewhen',
            'html_attributes_formula'
        ),
    )


class PlominoAction(Item):
    implements(IPlominoAction)

    security = ClassSecurityInfo()

    security.declarePublic('action_id')

    def action_id(self):
        """
        Return the value of the action.
        This will normally be the id of the action
        """
        if self.action_type in ['PREVIOUS', 'NEXT']:
            return 'plomino_%s' % self.action_type.lower()
        else:
            return self.id

    security.declarePublic('isHidden')

    def isHidden(self, target, context):
        """ Return True if an action is hidden for a target and context.

        Target may be view/page/document.
        """

        # Handle Previous/Next buttons if we're on a form.
        if context.__class__.__name__ == 'PlominoForm':
            form = context.getForm()
            multi = form.getIsMulti()
            if self.action_type in ['PREVIOUS', 'NEXT'] and multi:
                paging_info = form.paging_info()
                if self.action_type == 'PREVIOUS' and paging_info['is_first']:
                    return True
                if self.action_type == 'NEXT' and paging_info['is_last']:
                    return True

        if self.hidewhen:
            try:
                result = self.runFormulaScript(
                    SCRIPT_ID_DELIMITER.join(
                        ['action', context.id, self.id, 'hidewhen']),
                    target,
                    self.hidewhen,
                    True,
                    context.id)
            except PlominoScriptException, e:
                e.reportError(
                    '"%s" self hide-when failed' % self.Title())
                # if error, we hide anyway
                result = True
            return result
        else:
            return False

    security.declareProtected(READ_PERMISSION, 'executeAction')

    def executeAction(self, target, form_id):
        """ Return the URL for this action.
        """
        content = self.content.rstrip()
        db = self.getParentDatabase()
        if self.action_type == "OPENFORM":
            formid = content
            if not formid:
                return ""
            return db.absolute_url() + '/' + formid + '/OpenForm'
        elif self.action_type == "OPENVIEW":
            viewid = content
            if not viewid:
                return ""
            return db.absolute_url() + '/' + viewid + '/OpenView'
        elif self.action_type == "PYTHON":
            if target is None:
                targetid = "None"
            else:
                targetid = target.id
            return '%s/runScript?target=%s&form_id=%s' % (
                self.absolute_url(),
                targetid,
                form_id)
        elif self.action_type == "REDIRECT":
            try:
                redirecturl = self.runFormulaScript(
                    SCRIPT_ID_DELIMITER.join([
                        'action', self.getParentNode().id, self.id,
                        'script']),
                    target,
                    content,
                    True,
                    form_id)
                return str(redirecturl)
            except PlominoScriptException:
                # TODO: why not use e.reportError here?
                return ('javascript:alert('
                        '"Error: formula error in redirect action %s")' %
                        self.Title())
        else:  # "CLOSE", "SAVE", "NEXT", "PREVIOUS"
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
            returnurl = self.runFormulaScript(
                SCRIPT_ID_DELIMITER.join([
                    'action', self.getParentNode().id, self.id,
                    'script']),
                plominoContext,
                self.content,
                True,
                form_id)
            if not returnurl:
                returnurl = plominoReturnURL
            REQUEST.RESPONSE.redirect(returnurl)
        except PlominoScriptException, e:
            e.reportError('"%s" action failed' % self.Title())
            REQUEST.RESPONSE.redirect(plominoReturnURL)

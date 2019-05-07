from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import newSecurityManager
from jsonutil import jsonutil as json
from plone.autoform import directives
from plone.dexterity.content import Item
from plone.protect.interfaces import IDisableCSRFProtection
from plone.supermodel import directives as supermodel_directives
from plone.supermodel import model
from zope import schema
from zope.interface import implements, alsoProvides
from zope.schema.vocabulary import SimpleVocabulary

from .. import _
from ..config import SCRIPT_ID_DELIMITER
from ..exceptions import PlominoScriptException


class IPlominoAgent(model.Schema):
    """ Plomino agent schema
    """

    directives.widget('content', klass='plomino-formula')
    content = schema.Text(
        title=_("CMFPlomino_label_AgentContent", default="Code to execute"),
        description=_("CMFPlomino_help_AgentContent",
            default='Code to execute'),
        required=True,
    )

    run_as = schema.Choice(
        title=_('CMFPlomino_label_AgentRunAs', default="Run as"),
        description=_('CMFPlomino_help_AgentRunAs',
            default='Run the agent using current user access rights, or using '
            'the developer access rights.'),
        required=True,
        default='CURRENT',
        vocabulary=SimpleVocabulary.fromItems([
            ("Current user", "CURRENT"),
            ("Agent owner", "OWNER"),
        ]),
    )

    # ADVANCED
    supermodel_directives.fieldset(
        'advanced',
        label=_(u'Advanced'),
        fields=(
            'content',
        ),
    )


class PlominoAgent(Item):
    implements(IPlominoAgent)

    security = ClassSecurityInfo()

    def __call__(self, *args):
        """
        """
        plominoContext = self
        try:
            if self.run_as == "OWNER":

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
                SCRIPT_ID_DELIMITER.join(["agent", self.id, "content"]),
                plominoContext,
                self.content,
                True,
                *args
            )

            # Switch back to the original user
            if self.run_as == "OWNER":
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
        if request:
            #TODO: this is too general. shouldn't be here
            alsoProvides(request, IDisableCSRFProtection)
        if self.run_as == "OWNER":
            # Remember the current user
            member = self.getCurrentMember()
            if member.__class__.__name__ == "SpecialUser":
                user = member
            else:
                user = member.getUser()

            # Switch to the agent's owner
            owner = self.getOwner()
            newSecurityManager(None, owner)
        try:
            result = self.runFormulaScript(
                SCRIPT_ID_DELIMITER.join(["agent", self.id,"content"]),
                plominoContext,
                self.content,
                True,
                *args,
                **kwargs
            )
        except PlominoScriptException, e:
            # Exception logged already in runFormulaScript
            if request and request.get('RESPONSE'):
                request.RESPONSE.setHeader(
                    'content-type',
                    'text/plain; charset=utf-8')
                return e.message
            else:
                raise
        finally:
            # Switch back to the original user
            if self.run_as == "OWNER":
                newSecurityManager(None, user)

        if request:
            if request.get('REDIRECT', False):
                # result is supposed to be an URL
                plominoReturnURL = result or plominoReturnURL
                request.RESPONSE.redirect(plominoReturnURL)

            if "application/json" in request.getHeader('Accept', ''):
                # result will be serialized in JSON
                return json.dumps(result)
        else:
            return result


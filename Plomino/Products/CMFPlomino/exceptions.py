import traceback

from PlominoUtils import asUnicode
from Products.CMFCore.utils import getToolByName

import logging
logger = logging.getLogger('Plomino')

class PlominoScriptException(Exception):

    def __init__(self, context, exception_obj, formula, script_id):
        """
        """
        self.context = context
        self.context_url = context.absolute_url_path()
        self.formula = formula
        self.script_id = script_id
        self.message = self.traceErr()

    def __str__(self):
        """
        """
        msg = self.message
        return msg

    def traceErr(self):
        """trace errors from Scripts
        """
        msg = []

        formatted_lines = traceback.format_exc().splitlines()
        if not "line" in formatted_lines[-3]:
            msg = formatted_lines[-2:]
        else:
            msg = formatted_lines[-3:]
        msg.append("Context is <%s> %s" % (self.context.__class__.__name__, self.context_url))
        if self.context.getParentDatabase().debugMode:
            msg.append("Code : ")
            line_number = 4
            for l in self.formula().replace('\r', '').split('\n'):
                msg.append("%d: %s\r\n" % (line_number, l))
                line_number += 1
            logger.error('\n'.join(msg))
            
        return "\r\n".join(msg)

    def reportError(self, label, path=None, request=None):
        """
        """
        report = asUnicode(label)
        if not request:
            request = getattr(self.context, 'REQUEST', None)
        if request:
            if not path:
                if self.formula and hasattr(self.formula, 'absolute_url_path'):
                    path = self.formula.absolute_url_path()
            if path:
                report += " - Plomino formula %s" % path

            traceback = self.message.replace("<", "&lt;").replace(">", "&gt;")
            report += " - Plomino traceback " + traceback.replace('\n', '\n<br/>')
            plone_tools = getToolByName(self.context.getParentDatabase().aq_inner, 'plone_utils')
            plone_tools.addPortalMessage(report, 'error', request)
            
class PlominoRenderingException(Exception):
    pass

class PlominoReplicationException(Exception):
    pass


class PlominoDesignException(Exception):
    pass
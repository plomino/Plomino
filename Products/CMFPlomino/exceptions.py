import traceback
import re
from PlominoUtils import asUnicode
from Products.CMFCore.utils import getToolByName

import logging
logger = logging.getLogger('Plomino')


class PlominoScriptException(Exception):

    def __init__(self, context, exception_obj, formula, script_id, compilation_errors):
        """
        """
        self.context = context
        self.context_url = context.absolute_url_path()
        self.formula = formula
        self.script_id = script_id
        self.compilation_errors = compilation_errors
        self.message = asUnicode(self.traceErr())

    def __str__(self):
        """
        """
        msg = self.message.encode('utf-8')
        return msg

    def traceErr(self):
        """trace errors from Scripts
        """
        msg = []
        formatted_lines = traceback.format_exc().splitlines()
        for (i, line) in enumerate(formatted_lines):
            if ("Script (Python)" in line
                    and i < len(formatted_lines) - 1):
                msg.append(line[line.index(',') + 1:])
        msg.append(formatted_lines[-1])
        msg = msg + list(self.compilation_errors)
        msg.append("Context is <%s> %s" % (
            self.context.__class__.__name__,
            self.context_url))
        if self.context.getParentDatabase().debugMode:
            code = ["Code : "]
            line_number = 4
            formula = self.formula()
            r = re.compile('#Plomino import (.+)[\r\n]')
            for i in r.findall(formula):
                scriptname = i.strip()
                script_code = self.context.getParentDatabase().resources._getOb(scriptname, None)
                if script_code:
                    try:
                        script_code = script_code.read()
                    except:
                        msg = "#ALERT: " + scriptname + " invalid"
                        logger.error(msg, exc_info=True)
                        script_code = msg
                else:
                    script_code = "#ALERT: " + scriptname + " not found in resources"
                formula = formula.replace('#Plomino import ' + scriptname, script_code)
            for l in formula.replace('\r', '').split('\n'):
                code.append("%d: %s" % (line_number, l))
                line_number += 1
            logger.error('\n'.join(msg + code))

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


class PlominoCacheException(Exception):
    pass


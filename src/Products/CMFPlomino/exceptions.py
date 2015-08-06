import logging
from plone import api
import traceback

from .utils import asUnicode, _expandIncludes

logger = logging.getLogger('Plomino')


class PlominoScriptException(Exception):
    def __init__(
        self, context, exception_obj, formula, script_id, compilation_errors
    ):
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
        """ Trace errors from Scripts
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
            line_number = 6
            formula = _expandIncludes(self.context, self.formula)
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
                if (self.formula and
                        hasattr(self.formula, 'absolute_url_path')):
                    path = self.formula.absolute_url_path()
            if path:
                report += " - Plomino formula %s" % path

            traceback = self.message.replace("<", "&lt;").replace(">", "&gt;")
            report += " - Plomino traceback " + traceback.replace(
                '\n', '\n<br/>')
            api.portal.show_message(
                message=report,
                request=request,
                type='error'
            )


class PlominoRenderingException(Exception):
    pass


class PlominoReplicationException(Exception):
    pass


class PlominoDesignException(Exception):
    pass


class PlominoCacheException(Exception):
    pass

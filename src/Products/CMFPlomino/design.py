import logging
import traceback

logger = logging.getLogger('Plomino')


class DesignManager:

    def cleanFormulaScripts(self, script_id_pattern=None):
        if 'scripts' not in self:
            return
        for script_id in self.scripts.objectIds():
            if not script_id_pattern or script_id_pattern in script_id:
                self.scripts._delObject(script_id)

    def traceRenderingErr(self, e, context):
        """ Trace rendering errors
        """
        if self.debugMode:
            formatted_lines = traceback.format_exc().splitlines()
            msg = "\n".join(formatted_lines[-3:]).strip()
            msg = "%s\nPlomino rendering error with context: %s" % (
                msg,
                '/'.join(context.getPhysicalPath()))
        else:
            msg = None

        if msg:
            logger.error(msg)

import os.path
from zope.component import getMultiAdapter

class DataTables(object):
    """Methods used manipulate JQuery DataTables language files.
    """
    
    def __init__(self, context, request):
        """Initialize adapter."""
        self.context = context
        self.request = request
    
    def getLanguagePath(self):
        """Select the right language file from the context language. 
        """
        
        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        current_language = portal_state.language()
        
        lang = current_language.split('-')[0]
        
        dir, _ = os.path.split(os.path.abspath(__file__))
        if not os.path.isfile(os.path.join(dir, "lang", lang + ".txt")):
            lang = "en"
        
        return self.context.portal_url() + "/++resource++dataTables.lang/" + lang + ".txt"
        
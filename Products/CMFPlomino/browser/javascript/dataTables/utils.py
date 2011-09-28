import os.path
from zope.component import getMultiAdapter

def get_language_path(context):
    """Select the right language file from the context language. 
    """
    
    if not getattr(context, 'REQUEST', None):
        return 'No language'
    portal_state = getMultiAdapter((context, context.REQUEST), name=u'plone_portal_state')
    current_language = portal_state.language()
    
    lang = current_language.split('-')[0]
    
    dir, _ = os.path.split(os.path.abspath(__file__))
    if not os.path.isfile(os.path.join(dir, "lang", lang + ".txt")):
        lang = "en"
    
    return context.portal_url() + "/++resource++dataTables.lang/" + lang + ".txt"

class DataTables(object):
    """ Provides access to get_language_path via a browserview.
    """
    
    def __init__(self, context, request):
        """Initialize adapter."""
        self.context = context
        self.request = request
    
    def getLanguagePath(self):
        """
        """
        
        context = self.context.aq_inner
        return get_language_path(context)

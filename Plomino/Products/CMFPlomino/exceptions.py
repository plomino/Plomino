class PlominoScriptException(Exception):
    
    def __init__(self, context_url, formula):
        """
        """
        self.context_url = context_url
        self.formula = formula


class PlominoReplicationException(Exception):
    pass


class PlominoDesignException(Exception):
    pass
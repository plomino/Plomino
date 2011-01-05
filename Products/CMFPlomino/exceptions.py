class PlominoScriptException(Exception):
    
    def __init__(self, context_url, formula):
        """
        """
        self.context_url = context_url
        self.formula = formula

    def __str__(self):
        """
        """
        msg = "Plomino formula error\n    in "+str(self.formula) + "\n    with context : " +self.context_url
        return msg

class PlominoReplicationException(Exception):
    pass


class PlominoDesignException(Exception):
    pass
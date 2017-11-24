## START formula {
try:
    editpath = plominoContext.REQUEST.get('Plomino_Macro_Context')
    editcontext = plominoContext.restrictedTraverse(editpath)
    ctype = editcontext.getPortalTypeName()
    return not (ctype=='PlominoForm' and (editcontext.isPage or editcontext.isSearchForm ))
except:
    return True
## END formula }
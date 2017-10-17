## START formula {
editpath = plominoContext.REQUEST.get('Plomino_Macro_Context')
Log('editpath %s' % editpath, severity='debug')
if editpath is None:
    return True
editcontext = plominoContext.restrictedTraverse(editpath)
Log('editcontext %s' % editcontext, severity='debug')
ctype = editcontext.getPortalTypeName()
return ctype=='PlominoForm' and editcontext.isPage
## END formula }
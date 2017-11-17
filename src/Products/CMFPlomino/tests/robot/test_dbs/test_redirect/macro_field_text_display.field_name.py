## START selectionlistformula {
### START macro_field_selection_db_elements_1 ###

editpath = plominoContext.REQUEST.get('Plomino_Macro_Context')
Log('editpath %s' % editpath, 'macro_field_selection_db_elements/selectionlistformula', severity='debug')
if editpath is None:
    return [] # we aren't being used in a popup
editcontext = plominoContext.restrictedTraverse(editpath)
Log('editcontext %s' % editcontext, 'macro_field_selection_db_elements/selectionlistformula', severity='debug')
ctype = editcontext.getPortalTypeName()
Log('ctype %s' % ctype, 'macro_field_selection_db_elements/selectionlistformula', severity='debug')
editform = editcontext if ctype == 'PlominoForm' else editcontext.getParentNode()
editdb = editcontext.getParentDatabase()
Log('editdb %s' % editdb, 'macro_field_selection_db_elements/selectionlistformula', severity='debug')

def item(elm):
  return '{title} ({id})|{id}'.format(id=elm.id, title=elm.Title())
return [item(f) for f in editform.getFormFields()]
### END macro_field_selection_db_elements_1 ###




## END selectionlistformula }
## START selectionlistformula {

### START macro_field_selection_db_elements_1 ###

defaultitems = ['Select...|']
editpath = plominoContext.REQUEST.get('Plomino_Macro_Context')
Log('editpath %s' % editpath, 'macro_field_selection_db_elements/selectionlistformula', severity='debug')
if editpath is None:
    return defaultitems # we aren't being used in a popup
editcontext = plominoContext.restrictedTraverse(editpath)
Log('editcontext %s' % editcontext, 'macro_field_selection_db_elements/selectionlistformula', severity='debug')
ctype = editcontext.getPortalTypeName()
Log('ctype %s' % ctype, 'macro_field_selection_db_elements/selectionlistformula', severity='debug')
editform = None
if ctype != 'PlominoView':
    if ctype == 'PlominoForm':
        editform = editcontext
    else:
        editform = editcontext.getParentNode()
editdb = editcontext.getParentDatabase()
Log('editdb %s' % editdb, 'macro_field_selection_db_elements/selectionlistformula', severity='debug')

def item(elm, form_name=''):
    if form_name:
        return '{title} ({id}) from form: {form_name}|{id}'.format(id=elm.id, title=elm.Title(), form_name=form_name)
    return '{title} ({id})|{id}'.format(id=elm.id, title=elm.Title())

items = ['Save (save)|plomino_save','Close (close)|plomino_close']
if editform:
    for f, method_name in editform.getActions(hide=False):
        try:
            if f.getPortalTypeName() == "PlominoAction":
                items.append(item(f))
        except AttributeError:
            continue
    return items
elif ctype == 'PlominoView':
    for f, method_name in editcontext.getActions(hide=False):
        try:
            if f.getPortalTypeName() == "PlominoAction":
                items.append(item(f))
        except AttributeError:
            continue
    return items
else:
    return []

### END macro_field_selection_db_elements_1 ###




## END selectionlistformula }
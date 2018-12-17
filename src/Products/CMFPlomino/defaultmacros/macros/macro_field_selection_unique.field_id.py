## START selectionlistformula {

### START macro_field_selection_db_elements_3 ###

defaultitems = ['Select...|']
editpath = plominoContext.REQUEST.get('Plomino_Macro_Context')
Log('editpath %s' % editpath, 'macro_field_selection_db_elements/selectionlistformula', severity='info')
if editpath is None:
    return defaultitems # we aren't being used in a popup
editcontext = plominoContext.restrictedTraverse(editpath)
Log('editcontext %s' % editcontext, 'macro_field_selection_db_elements/selectionlistformula', severity='info')
ctype = editcontext.getPortalTypeName()
Log('ctype %s' % ctype, 'macro_field_selection_db_elements/selectionlistformula', severity='info')
editform = None
if ctype != 'PlominoView':
    if ctype == 'PlominoForm':
        editform = editcontext
    else:
        editform = editcontext.getParentNode()
editdb = editcontext.getParentDatabase()
Log('editdb %s' % editdb, 'macro_field_selection_db_elements/selectionlistformula', severity='info')

def item(elm, form_name=''):
    if form_name:
        return '{title} ({id}) from form : {form_name}|{id}'.format(id=elm.id, title=elm.Title(), form_name=form_name)
    return '{title} ({id})|{id}'.format(id=elm.id, title=elm.Title())

def get_fields(form_element, form_name):
    field_items = []
    for this_form in form_element.getFormFields(includesubforms=True):
        try:
            if this_form.getPortalTypeName() == "PlominoField":
                field_items.append(item(this_form, form_name))
        except AttributeError:
            continue
    return field_items

current_form_name = "{title} ({id})".format(
        title=editform.Title(),
        id=editform.id)
if ctype == 'PlominoField':
    current_form_items = ['Current field |%s' % '@@CURRENT_FIELD']
else:
    current_form_items = defaultitems
current_form_items += get_fields(editform, current_form_name)
current_forms = editform.getSubforms() +[editform.id]
other_form_items = [] 
for other_form in editdb.getForms():
    try:
        if other_form.getPortalTypeName() == "PlominoForm" and not other_form.id in current_forms:
            other_form_name = "{title} ({id})".format(
                title=other_form.Title(),
                id=other_form.id)
            if current_form_name != other_form_name:
                other_form_items += get_fields(other_form, other_form_name)
    except AttributeError:
        continue
return current_form_items + other_form_items

### END macro_field_selection_db_elements_3 ###
## END selectionlistformula }
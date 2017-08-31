## START formula {
doc = plominoContext
type_ = doc.getItem('element_type')
include_other_ = doc.getItem('include_other', False)
code = """
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
"""

if type_ == 'Forms':
    return code + """
items = defaultitems
for f in editdb.getForms():
    try:
        if f.getPortalTypeName() == "PlominoForm":
            items.append(item(f))
    except AttributeError:
        continue
return items
"""
elif type_ == 'Views':
    return code + """
items = defaultitems
for f in editdb.getViews():
    try:
        if f.getPortalTypeName() == "PlominoView":
            items.append(item(f))
    except AttributeError:
        continue
return items
"""
elif type_ == 'Hidewhens':
    return code + """
items = defaultitems
for f in editform.getHidewhenFormulas():
    try:
        if f.getPortalTypeName() == "PlominoHidewhen":
            items.append(item(f))
    except AttributeError:
        continue
return items
"""
elif type_ == 'Actions':
    return code + """
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
"""
elif type_ == 'Fields':
    if include_other_:
        return code + """
def get_fields(form_element, form_name):
    field_items = defaultitems
    for this_form in form_element.getFormFields():
        try:
            if this_form.getPortalTypeName() == "PlominoField":
                field_items.append(item(this_form, form_name))
        except AttributeError:
            continue
    return field_items

current_form_name = ''
current_form_items = ['Form ID|Form']
if ctype == 'PlominoField':
    current_form_items.append('Current field |%s' % '@@CURRENT_FIELD')
if editform:
    current_form_name = "{title} ({id})".format(
        title=editform.Title(),
        id=editform.id)
    current_form_items = get_fields(editform, current_form_name)
    if ctype == 'PlominoField':
        current_form_items.insert(0, 'Current field |%s' % '@@CURRENT_FIELD')

other_form_items = []
for other_form in editdb.getForms():
    try:
        if other_form.getPortalTypeName() == "PlominoForm":
            other_form_name = "{title} ({id})".format(
                title=other_form.Title(),
                id=other_form.id)
            if current_form_name != other_form_name:
                other_form_items += get_fields(other_form, other_form_name)
    except AttributeError:
        continue
return current_form_items + other_form_items
"""
    else:
        return code + """
items = defaultitems
if ctype == 'PlominoField':
    items.append('Current field |%s' % '@@CURRENT_FIELD')
for f in editform.getFormFields():
    try:
        if f.getPortalTypeName() == "PlominoField":
            items.append(item(f))
    except AttributeError:
        continue

return items

"""
else:
    return code + 'return defaultitems'
## END formula }

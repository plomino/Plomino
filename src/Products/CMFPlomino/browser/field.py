from Products.Five import BrowserView
from plone.dexterity.browser import edit

from collective.instancebehavior import (
    enable_behaviors,
    instance_behaviors_of,
    disable_behaviors,
)

from ..config import SCRIPT_ID_DELIMITER


class FieldView(BrowserView):

    def filterusers(self):
        if self.context.field_type == "NAME":
            self.request.RESPONSE.setHeader(
                'content-type', 'application/json; charset=utf-8')
            return self.context.getSettings().getFilteredNames(
                self.request.get('query'))


class EditForm(edit.DefaultEditForm):

    def update(self):
        if 'update.field.type' in self.request:
            self._updateFieldType()
        return super(EditForm, self).update()

    def _updateFieldType(self):
        # Update the field type. This will force the form to load with the
        # relevant field type settings.
        field_type = self.request['form.widgets.field_type'][0]
        obj = self.getContent()
        obj.field_type = field_type

        # Disable, then enable the appropriate behaviors
        existing_behaviors = instance_behaviors_of(obj)
        disable_behaviors(obj, existing_behaviors, [], reindex=False)
        behavior = 'Products.CMFPlomino.fields.%s.I%sField' % (
            field_type.lower(),
            field_type.capitalize(),
        )

        # XXX: This doesn't seem to reindex object_provides properly
        enable_behaviors(obj, [behavior, ], [])

        # Ignore the context so the form is rendered with values on the request
        self.ignoreContext = True

        # cleanup compiled formulas
        obj.cleanFormulaScripts(
            SCRIPT_ID_DELIMITER.join([
                "field",
                obj.getPhysicalPath()[-2],
                obj.id
            ])
        )

        # re-index
        db = obj.getParentDatabase()
        if obj.to_be_indexed and not db.do_not_reindex:
            db.getIndex().createFieldIndex(
                obj.id,
                obj.field_type,
                indextype=obj.index_type,
                fieldmode=obj.field_mode,
            )

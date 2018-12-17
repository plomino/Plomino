# -*- coding: utf-8 -*-

from zope.interface import Interface, implements
from ZPublisher.HTTPRequest import record

from ..utils import asUnicode


class IBaseField(Interface):
    """
    """


class BaseField(object):
    """
    """
    implements(IBaseField)

    def __init__(self, context):
        """Initialize adapter."""
        self.context = context

    def render_read(self, *args, **kwargs):
        # if custom template, use it
        if self.context.read_template:
            pt = getattr(self.context.resources, self.context.read_template)
            return pt.__of__(self.context)(*args, **kwargs)
        return self.read_template(*args, **kwargs)

    def render_edit(self, *args, **kwargs):
        # if custom template, use it
        if self.context.edit_template:
            pt = getattr(self.context.resources, self.context.edit_template)
            return pt.__of__(self.context)(*args, **kwargs)
        return self.edit_template(*args, **kwargs)

    def validate(self, strValue):
        """
        """
        errors = []
        return errors

    def processInput(self, strValue):
        """
        """
        fieldName = self.context.id
        if type(strValue) == str:
            strValue = strValue.decode('utf-8')

        # if allow_other_value is enabled on RADIO and CHECKBOX, a special other text input {field_name}_other
        # is included in form input. Need to combine with main input
        other_value = self.context.REQUEST.get(fieldName + '@@OTHER_VALUE', '')
        if other_value:
            if isinstance(strValue, basestring) and strValue == '@@OTHER_VALUE':
                strValue = other_value
            if  type(strValue) == list and '@@OTHER_VALUE' in strValue:
                strValue = [other_value if v == '@@OTHER_VALUE' else v for v in strValue]
        return strValue

    def getSelectionList(self, doc):
        """
        """
        return None

    def getFieldValue(self, form, doc=None, editmode_obsolete=False,
            creation=False, request=None):
        """ Return the field as rendered by ``form`` on ``doc``.

        We may be called on:
        - a blank form, e.g. while creating a document;
        - an existing document;
        - a TemporaryDocument used during datagrid editing.

        - If EDITABLE, look for the field value:
          - are we creating a doc or editing a datagrid row?
            - do we have a request?
              - if we're being used for a datagrid,
                - get field value from `getDatagridRowdata`,
                - or compute a default value;
              - otherwise look for `request[fieldName]`;
              - otherwise look for `request[fieldName+'_querystring']`;
            - otherwise compute a default value.
          - otherwise just `getItem`
        - if DISPLAY/COMPUTED:
          - if DISPLAY and doc and no formula: `getItem`.
          - else compute
        - if CREATION
          - compute or `getItem`
        - if COMPUTEDONSAVE and doc: `getItem`
        - otherwise, give up.
        """
        # XXX: The editmode_obsolete parameter is unused.
        fieldName = self.context.id
        fieldType = self.context.field_type
        mode = self.context.field_mode

        if doc:
            target = doc
        else:
            target = form

        fieldValue = None

        if mode == "EDITABLE":
            # if (not doc) or creation
            if doc:
                fieldValue = doc.getItem(fieldName)
                db = doc.getParentDatabase()
                if fieldType == 'ATTACHMENT' and doc.id =='TEMPDOC' and db.getRequestCache(fieldName+"@@ATTACHMENT"):
                    fieldValue = db.getRequestCache(fieldName+"@@ATTACHMENT")
            if (not fieldValue) and self.context.formula:
                # This implies that if a falsy fieldValue is possible,
                # Formula needs to take it into account, e.g. using hasItem
                fieldValue = form.computeFieldValue(fieldName, target)
            elif (not fieldValue) and request:
                # if no doc context and no default formula, we accept
                # value passed in the REQUEST so we look for 'fieldName'
                # but also for 'fieldName_querystring' which allows to
                # pass value via the querystring without messing the
                # POST content
                request_value = request.get(fieldName, '')
                if not request_value:
                    request_value = request.get(fieldName + '_querystring', '')
                if isinstance(request_value, record):
                    fieldValue = request_value
                else:
                    fieldValue = asUnicode(request_value)
            if not fieldValue:
                fieldValue = ""

        elif mode in ["DISPLAY", "COMPUTED"]:
            if mode == "DISPLAY" and not self.context.formula and doc:
                fieldValue = doc.getItem(fieldName)
            else:
                fieldValue = form.computeFieldValue(fieldName, target)

        elif mode == "CREATION":
            if creation or not doc:
                # Note: on creation, there is no doc, we use form as target
                # in formula, and we do the same when no doc (e.g. with tojson)
                fieldValue = form.computeFieldValue(fieldName, form)
            else:
                fieldValue = doc.getItem(fieldName)
        elif mode == "COMPUTEDONSAVE" and doc:
            fieldValue = doc.getItem(fieldName)

        if fieldValue is None:
            fieldValue = ""

        return fieldValue

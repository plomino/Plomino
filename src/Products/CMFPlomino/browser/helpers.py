import json
from plone.app.widgets.base import InputWidget
from plone.app.z3cform.widget import BaseWidget
from z3c.form.browser.widget import HTMLInputWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IWidget, NO_VALUE
from z3c.form.widget import Widget
from zope.component import adapts
from zope.interface import implementsOnly
from zope.schema.interfaces import IList
import re
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.schema import getFieldsInOrder
from Products.CMFPlomino.document import getTemporaryDocument


__author__ = 'dylanjay'

class ISubformWidget(IWidget):
    """ Widget for collecting data from a list of possible subforms
    """


class SubformWidgetConverter(BaseDataConverter):
    """Convert single json input into list"""

    adapts(IList, ISubformWidget)

    def toWidgetValue(self, value):
        """Converts from field value to widget.

        :param value: Field value.
        :type value: date

        :returns: Date in format `Y-m-d`
        :rtype: string
        """
        return value

    def toFieldValue(self, value):
        """Converts from widget value to field.

        :param value: Value inserted by date widget.
        :type value: string

        :returns: `date.date` object.
        :rtype: date
        """
        return value


class SubformWidget(Widget):
    """ datatable z3cform widget for multple kinds of subforms.
    uses a list of (id,formid,json) objects
    """

    _converter = SubformWidgetConverter

    implementsOnly(ISubformWidget)

    def update(self):
        super(SubformWidget, self).update()
        self.subform = 'send-to-mail'
        self.raw = json.dumps(self.value if self.value else [])
        self.columns = ["Title"]
        self.fields = ['emailsubject']
        rendered = []
        for row in self.value:
            rendered.append([row[c] for c in self.fields if c in row])
        self.rendered = json.dumps(rendered)
        # TODO: need to run through each form to get rendered values


    def extract(self, default=NO_VALUE):
        value = super(SubformWidget, self).extract(default)
        raw = json.loads(value) if value and value != default else default
        return raw



    # def __call__(self):
    #     import pdb; pdb.set_trace()
    #     return super(SubformWidget, self).__call__(self)

    # def render(self):
    #     """Render widget.
    #
    #     :returns: Widget's HTML.
    #     :rtype: string
    #     """
    #     if self.mode != 'display':
    #         return super(SubformWidget, self).render()
    #
    #     if not self.value:
    #         return ''
    #
    #     field_value = self._converter(
    #         self.field, self).toFieldValue(self.value)
    #     if field_value is self.field.missing_value:
    #         return u''
    #
    #     formatter = self.request.locale.dates.getFormatter(
    #         self._formater, "short")
    #     if field_value.year > 1900:
    #         return formatter.format(field_value)
    #
    #     # due to fantastic datetime.strftime we need this hack
    #     # for now ctime is default
    #     return field_value.ctime()


def update_helpers(obj, event):
    """Update all the formula fields based on our helpers
    """

    helpers = obj.helpers
    fields = getFieldsInOrder(obj.getTypeInfo().lookupSchema())

    for helper in helpers:
        formid = 'send-as-email' #TODO: get form from store
        db = obj.getParentDatabase()
        form = db.getForm(formid)
        helperid = 'blah'

        doc = getTemporaryDocument(db, form, helper).__of__(db)
        # has to be computed on save so it appears in the doc
        doc.save()

        for id, field in fields:
            #value = getattr(getattr(self., key), 'output', getattr(obj, key)):

            #TODO: if its a formula then wipe any previous generated code
            #TODO: can work out whats a formula from the widget?

            value = None
            if doc.hasItem('generate_%s'%id.lower()):
                value = doc.getItem('generate_%s'%id.lower())
            elif doc.hasItem('generate_%s'%id):
                value = doc.getItem('generate_%s'%id)
            else:
                continue
            if value is None:
                continue
            code = getattr(obj, id)
            #TODO: what if the id has changed. Should redo all gen code?
            fmt = '### START {id} ###{code}### END {id} ###'
            reg_code = re.compile(fmt.format(id=helperid, code='((.|\n|\r)+)'))
            if not code or not reg_code.search(code):
                code = (code + u'\n') if code else u''
                code += fmt.format(id=helperid, code="\n"+value+"\n")
            else:
                repl = fmt.format(id=helperid, code="\n"+value+"\n")
                code = reg_code.sub(repl, code)
            setattr(obj, id, code)


class HelperView(BrowserView):
    pass

    template = ViewPageTemplateFile("templates/openform.pt")
    bare_template = ViewPageTemplateFile("templates/openbareform.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.form = self.context.aq_parent['send-as-email']
        self.target = self.context


    def openform(self):

        if self.request.form.get('plomino_save'):
            return self.processForm()
        return self.template()

    def processForm(self):
        """ validate and generate code, updating this form
        """
        REQUEST = self.request
        db = self.context.getParentDatabase()

        # validate submitted values
        errors = self.context.validateInputs(REQUEST)
        if errors:
            return self.context.notifyErrors(errors)

        doc = form.getTemporaryDocument(db, self.form, REQUEST).__of__(db)
        # has to be computed on save so it appears in the doc
        doc.save()

        # formulas = dict(getFieldsInOrder(self.context.getTypeInfo().lookupSchema()))
        # for id in doc.getItems():
        #     if not id.starts_with('generate_'):
        #         continue
        #     fieldid = id.lstrip('generate_')
        #     if fieldid not in formulas:
        #         continue




        for id, field in getFieldsInOrder(self.context.getTypeInfo().lookupSchema()):
            #value = getattr(getattr(self., key), 'output', getattr(obj, key)):

            #TODO: if its a formula then wipe any previous generated code
            #TODO: can work out whats a formula from the widget?

            value = None
            if doc.hasItem('generate_%s'%id.lower()):
                value = doc.getItem('generate_%s'%id.lower())
            elif doc.hasItem('generate_%s'%id):
                value = doc.getItem('generate_%s'%id)
            else:
                continue
            if value is None:
                continue
            import pdb; pdb.set_trace()
            code = getattr(self.context, id)
            #TODO: what if the id has changed. Should redo all gen code?
            fmt = '### START {id} ###{eol}{code}{eol}### END {id} ###'
            reg_code = re.compile(fmt.format(id=obj.id, code='(.*)',eol="^"))
            if not code or not reg_code.match(code):
                code += '\n'+fmt.format(id=self.form.id, code=value, eol="\n")
            else:
                code = reg_code.subn(
                    code,
                    fmt.format(id=self.form.id, code=value, eol="\n"),
                    1,
                    re.MULTILINE)
            setattr(self.context, id, code)

        return self.template()

        # # execute the onCreateDocument code of the form
        # valid = ''
        # try:
        #     valid = self.runFormulaScript(
        #         SCRIPT_ID_DELIMITER.join(['form', self.id, 'oncreate']),
        #         doc,
        #         self.onCreateDocument)
        # except PlominoScriptException, e:
        #     e.reportError('Document is created, but onCreate formula failed')
        #
        # if valid is None or valid == '':
        #     doc.saveDocument(REQUEST, creation=True)
        # else:
        #     db.documents._delOb(doc.id)
        #     db.writeMessageOnPage(valid, REQUEST, False)
        #     REQUEST.RESPONSE.redirect(db.absolute_url())

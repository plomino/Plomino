import json
from plone.app.widgets.base import InputWidget
from plone.app.z3cform.widget import BaseWidget
from z3c.form.browser.widget import HTMLInputWidget
from z3c.form.converter import BaseDataConverter
from z3c.form.interfaces import IWidget, NO_VALUE
from z3c.form.widget import Widget
from zope import schema
from zope.component import adapts
from zope.interface import implementsOnly
from zope.schema.interfaces import IList
from Products.CMFPlomino.contents.action import IPlominoAction
from Products.CMFPlomino.contents.field import IPlominoField
from Products.CMFPlomino.contents.form import IPlominoForm
from Products.CMFPlomino.contents.hidewhen import IPlominoHidewhen
from Products.CMFPlomino.contents.view import IPlominoView
import re
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.schema import getFieldsInOrder
from Products.CMFPlomino.document import getTemporaryDocument

from Products.CMFCore.interfaces import IDublinCore
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


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
        self.fields = ['title']

        OPEN_URL = "{formid}/OpenForm?ajax_load=1&Plomino_Parent_Field=_dummy_&Plomino_Parent_Form=_dummy_"
        helpers = [('send-as-email', "Send to email on save"),('helper_form_pdfdownload', "Download as PDF"), ]
        self.form_urls = [dict(url=OPEN_URL.format(formid=id),id=id,title=title) for id,title in helpers]
        self.form_urls = json.dumps(self.form_urls)

        self.rendered = []
        if self.value is not None:
            for row in self.value:
                self.rendered.append([row[c] for c in self.fields if c in row])
        self.rendered = json.dumps(self.rendered)
        # TODO: need to run through each form to get rendered values


    def extract(self, default=NO_VALUE):
        value = super(SubformWidget, self).extract(default)
        raw = json.loads(value) if value and value != default else default
        return raw



@provider(IFormFieldProvider)
class IHelpers(model.Schema):
    """Add tags to content
    """

    #
    # directives.fieldset(
    #         'categorization',
    #         label=_(u'Categorization'),
    #         fields=('tags',),
    #     )


    directives.widget('helpers', SubformWidget)
    directives.order_after(helpers = 'IBasic.description')
    helpers = schema.List(value_type=schema.Dict(),
                          title=u"Helpers",
                          description=u"Helpers applied",
                          required=False
    )

# @implementer(IHelpers)
# @adapter(IPlominoForm)
# # @adapter(IPlominoField)
# # @adapter(IPlominoHidewhen)
# # @adapter(IPlominoAction)
# # @adapter(IPlominoView)
# class Helpers(object):
#     """Add a field for storing helpers on
#     """
#
#     def __init__(self, context):
#         self.context = context
#
#     @property
#     def helpers(self):
#         res = set(self.context.helpers)
#         update_helpers(self.context, None)
#         return res
#
#     @helpers.setter
#     def helpers(self, value):
#         if value is None:
#             value = ()
#         self.context.helpers=value


# Event handler
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

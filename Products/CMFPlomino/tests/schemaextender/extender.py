from Products.Archetypes.public import StringField, StringWidget
from archetypes.schemaextender.field import ExtensionField

from Products.CMFPlomino.interfaces import IPlominoField


from zope.component import adapts


class _ExtensionStringField(ExtensionField, StringField):
    pass


class PlominoExtender(object):
    adapts(IPlominoField)

    fields = [
        _ExtensionStringField(
            "extension_field",
            widget=StringWidget(
                label=u"A new field",
                description=u"Added with atschemaextender",
            ),
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import model
from z3c.form.interfaces import IEditForm, IAddForm
from zope.interface import provider, Interface
from zope import schema
from plone.autoform import directives as autoform
from plone.supermodel import directives, model
from .. import _

@provider(IFormFieldProvider)
class IShortName(model.Schema):
    """ Marker interface for our behaviour
    """
    id = schema.ASCIILine(
        title=_(u'Id'),
#        description=_(u'The id used to store and retried this data in the document'),
        required=False,
    )
    autoform.write_permission(id='cmf.AddPortalContent')
    autoform.order_before(id = '*')

@provider(IFormFieldProvider)
class IBasic(model.Schema):

    # default fieldset
    title = schema.TextLine(
        title=_(u'label_title', default=u'Title'),
        required=True
    )

    description = schema.Text(
        title=_(u'label_description', default=u'Summary'),
        description=_(
            u'help_description',
            default=u'For documentation purposes'
        ),
        required=False,
        missing_value=u'',
    )

    directives.fieldset(
        'advanced',
        label=_(u'Advanced'),
        fields=(
            'description',
        ),
    )

    #autoform.order_before(description='*')
    autoform.order_before(title='*')

    autoform.omitted('title', 'description')
    autoform.no_omit(IEditForm, 'title', 'description')
    autoform.no_omit(IAddForm, 'title', 'description')

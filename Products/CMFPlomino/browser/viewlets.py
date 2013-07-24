""" Override title on Plomino documents to be dynamically computed
"""

from cgi import escape
from zope.component import getMultiAdapter
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone.utils import safe_unicode

class TitleViewlet(ViewletBase):
    index = ViewPageTemplateFile('title.pt')

    def update(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_portal_state')
        # context_state = getMultiAdapter((self.context, self.request),
        #                                  name=u'plone_context_state')
        # page_title = escape(safe_unicode(context_state.object_title()))
        page_title = escape(safe_unicode(self.context.getTitle()))
        portal_title = escape(safe_unicode(portal_state.navigation_root_title()))
        if page_title == portal_title:
            self.site_title = portal_title
        else:
            self.site_title = u"%s &mdash; %s" % (page_title, portal_title)

class PathBarViewlet(ViewletBase):
    index = ViewPageTemplateFile('path_bar.pt')

    def update(self):
        super(PathBarViewlet, self).update()

        self.is_rtl = self.portal_state.is_rtl()

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name='breadcrumbs_view')
        self.breadcrumbs = breadcrumbs_view.breadcrumbs()


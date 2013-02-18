from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound
from Products.Five import BrowserView


class DocumentView(BrowserView):
    """
    """
    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(DocumentView, self).__init__(context, request)
        self.doc = None

    def publishTraverse(self, request, name):
        doc = self.context.getDocument(name)
        if not doc:
            raise NotFound(self, name, request)
        self.doc = doc
        return self

    def __call__(self):
        return self.doc.checkBeforeOpenDocument()

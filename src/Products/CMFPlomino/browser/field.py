from Products.Five import BrowserView


class FieldView(BrowserView):

    def filterusers(self):
        if self.context.field_type == "NAME":
            self.request.RESPONSE.setHeader(
                'content-type', 'application/json; charset=utf-8')
            return self.context.getSettings().getFilteredNames(
                self.request.get('query'))

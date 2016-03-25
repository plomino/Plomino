from AccessControl import Unauthorized
from jsonutil import jsonutil as json
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ..config import (
    READ_PERMISSION,
    SCRIPT_ID_DELIMITER,
)
from ..utils import asList, asUnicode
from ..exceptions import PlominoScriptException


class ViewView(BrowserView):

    template = ViewPageTemplateFile("templates/openview.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.target = self.context

    def openview(self):
        """ Check read permission and open view.

        NOTE: if READ_PERMISSION is set on the 'view' action itself, it
        causes error 'maximum recursion depth exceeded' if user hasn't
        permission.
        """
        if self.context.checkUserPermission(READ_PERMISSION):
            valid = ''
            try:
                if self.context.onOpenView:
                    valid = self.context.runFormulaScript(
                        SCRIPT_ID_DELIMITER.join(
                            ['view', self.context.id, 'onopen']),
                        self.context,
                        self.context.onOpenView)
            except PlominoScriptException, e:
                e.reportError('onOpenView event failed')

            if valid:
                return self.context.unrestrictedTraverse('@@plomino_errors')(
                    errors=[valid])

            return self.template()
        else:
            raise Unauthorized("You cannot read this content")

    def json(self):
        """ Returns a JSON representation of view data
        """
        data = []
        categorized = self.context.categorized

        pagenumber = int(self.request.get('pagenumber', '1'))
        pagesize = self.request.get('pagesize', None)
        if pagesize:
            pagesize = int(pagesize)
        search = self.request.get('search', '').lower()
        if search:
            search = ' '.join([term + '*' for term in search.split(' ')])
        sort_column = self.request.get('sorton')
        if sort_column:
            sort_index = self.context.getIndexKey(sort_column)
        else:
            sort_index = None
        reverse = int(self.request.get('reverse', '0'))

        if 'request_query' in self.request:
            # query parameter in self.request is supposed to be a json object
            request_query = self.context.__query_loads__(
                self.request['request_query'])
        else:
            request_query = None

        results = self.context.getAllDocuments(
            pagenumber=pagenumber,
            pagesize=pagesize,
            getObject=False,
            fulltext_query=search,
            sortindex=sort_index,
            reverse=reverse,
            request_query=request_query)
        total = len(results)
        if pagesize:
            display_total = results.items_on_page
        else:
            display_total = total
        columns = [column for column in self.context.getColumns()
            if not column.hidden_column]
        for brain in results:
            row = [brain.id, ]
            for column in columns:
                column_value = getattr(brain,
                    self.context.getIndexKey(column.id), '')
                rendered = column.getColumnRender(column_value)
                if isinstance(rendered, list):
                    rendered = [asUnicode(e).encode('utf-8').replace('\r', '')
                        for e in rendered]
                else:
                    rendered = asUnicode(rendered).encode('utf-8').replace(
                        '\r', '')
                row.append(rendered or '&nbsp;')
            if categorized:
                for cat in asList(row[1]):
                    entry = [c for c in row]
                    entry[1] = cat
                    data.append(entry)
            else:
                data.append(row)

        self.request.RESPONSE.setHeader(
            'content-type', 'application/json; charset=utf-8')
        return json.dumps(
            {'total': total,
            'displayed': display_total,
            'rows': data})

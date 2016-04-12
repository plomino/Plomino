from AccessControl import Unauthorized
from jsonutil import jsonutil as json
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from ..config import READ_PERMISSION


class DatabaseView(BrowserView):

    acl_template = ViewPageTemplateFile("templates/acl.pt")
    design_template = ViewPageTemplateFile("templates/design.pt")
    replication_template = ViewPageTemplateFile("templates/replication.pt")
    view_template = ViewPageTemplateFile("templates/opendatabase.pt")
    profiling_template = ViewPageTemplateFile("templates/profiling.pt")

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.form = self.context
        self.target = self.context

    def view(self):
        if self.context.checkUserPermission(READ_PERMISSION):
            if self.context.start_page:
                target = getattr(self.context, self.context.start_page, None)
                if target:
                    self.request.response.redirect(target.absolute_url())
            else:
                return self.view_template()
        else:
            raise Unauthorized("You cannot read this content")

    def design(self):
        return self.design_template()

    def profiling(self):
        return self.profiling_template()

    def tree(self):
        database = self.context.getParentDatabase()

        # Create form tree
        forms = []
        for form in database.getForms():
            fields = []
            for field in form.getFormFields():
                fields.append({
                    "label": field.id,
                    "url": field.absolute_url(),
                    "type" : 'field'
                })
            plomino_form = []
            plomino_form.append({
                "label" : "Fields",
                "folder" : True,
                "children" : fields,
                "type" : "fields",
            })
            actions = []
            for action in form.getFormActions():
                actions.append({
                    "label": action.id,
                    'type' : 'action',
                    "url" : action.absolute_url()
                })
            plomino_form.append({
                "label": "Actions",
                "folder": True,
                "children": actions,
                "type" : "actions",
            })
            forms.append({
                "label": form.id,
                "folder": True,
                "children": plomino_form,
                "type" : "form",
                "url" : form.absolute_url(),
            })

        # Create Views Tree
        views = []
        for view in database.getViews():
            plomino_view = []
            actions = []
            for action in view.getActions():
                # view.getActions() returns tuples
                actions.append({
                    "label": action[0].id,
                    "type": 'action',
                    "url": action[0].absolute_url()
                })
            plomino_view.append({
                "label": "Actions",
                "folder": True,
                "children": actions,
                "type": "actions",
            })
            columns = []
            for column in view.getColumns():
                columns.append({
                    "label": column.id,
                    "type": 'column',
                    "url": column.absolute_url()
                })
            plomino_view.append({
                "label": "Columns",
                "folder": True,
                "children": columns,
                "type": "columns",
            })
            views.append({
                "label": view.id,
                "type": "view",
                "children": plomino_view,
                "url": view.absolute_url(),
            })


        # Create Agents View
        agents = []
        for agent in database.getAgents():

            agents.append({
                "label" : agent.id,
                "type" : "agent",
                "url" : agent.absolute_url()
            })

        # Build the final element tree
        elements = [
            {
                "label": "Forms",
                "folder": True,
                "children": forms,
                "type" : 'database'
            },
            {
                "label": "Views",
                "folder": True,
                "children": views,
                "type" : 'views'
            },
            {
                "label": "Agents",
                "folder": True,
                "children": agents ,
                "type" : 'agents'
            }
        ]
        self.request.RESPONSE.setHeader(
            'content-type', 'application/json; charset=utf-8')
        return json.dumps(elements)

    def acl(self):
        return self.acl_template()

    def replication(self):
        return self.replication_template()

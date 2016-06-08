 from AccessControl import Unauthorized
from jsonutil import jsonutil as json
import re
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides
import plone.protect.interfaces

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

    def code(self):
        if self.request.method == "GET":
            code = ""
            methods = []
            if self.request.get("Form") != None:
                formID = self.request.get("Form")
                form = self.context.getForm(formID)
                if not form :
                    return "##Unknown"

                methods.append({
                    "id": "document_title",
                    "name": "Document title formula",
                    "desc": "Compute the document title"
                })
                if form.document_title:
                    code+= "## START document_title {\n"
                    code+= form.document_title
                    code+= "\n## END document_title }\n\r"

                methods.append({
                    "id": "document_id",
                    "name": "Document id formula",
                    "desc": "Compute the document id at creation."
                })
                if form.document_id:
                    code+= "## START document_id {\n"
                    code+= form.document_id
                    code+= "\n## END document_id }\n\r"

                methods.append({
                    "id": "search_formula",
                    "name": "Search formula",
                    "desc": "Leave blank to use default ZCatalog search"
                })
                if form.search_formula:
                    code+= "## START search_formula {\n"
                    code+= form.search_formula
                    code+= "\n## END search_formula }\n\r"

                methods.append({
                    "id": "onCreateDocument",
                    "name": "On create document",
                    "desc": "Action to take when the document is created"
                })
                if form.onCreateDocument:
                    code+= "## START onCreateDocument {\n"
                    code+= form.onCreateDocument
                    code+= "\n## END onCreateDocument }\n\r"

                methods.append({
                    "id": "onOpenDocument",
                    "name": "On open document",
                    "desc": "Action to take when the document is opened"
                })
                if form.onOpenDocument:
                    code+= "## START onOpenDocument {\n"
                    code+= form.onOpenDocument
                    code+= "\n## END onOpenDocument }\n\r"

                methods.append({
                    "id": "beforeSaveDocument",
                    "name": "Before save document",
                    "desc": "Action to take before submitted values are saved into the document (submitted values are in context.REQUEST)"
                })
                if form.beforeSaveDocument:
                    code+= "## START beforeSaveDocument {\n"
                    code+= form.beforeSaveDocument
                    code+= "\n## END beforeSaveDocument }\n\r"

                methods.append({
                    "id": "onSaveDocument",
                    "name": "On save document",
                    "desc": "Action to take when saving the document"
                })
                if form.onSaveDocument:
                    code+= "## START onSaveDocument {\n"
                    code+= form.onSaveDocument
                    code+= "\n## END onSaveDocument }\n\r"

                methods.append({
                    "id": "onDeleteDocument",
                    "name": "On delete document",
                    "desc": "Action to take before deleting the document"
                })
                if form.onDeleteDocument:
                    code+= "## START onDeleteDocument {\n"
                    code+= form.onDeleteDocument
                    code+= "\n## END onDeleteDocument }\n\r"

                methods.append({
                    "id": "onSearch",
                    "name": "On submission of search form",
                    "desc": "Action to take when submitting a search"
                })
                if form.onSearch:
                    code+= "## START onSearch {\n"
                    code+= form.onSearch
                    code+= "\n## END onSearch }\n\r"

                methods.append({
                    "id": "beforeCreateDocument",
                    "name": "Before document creation",
                    "desc": "Action to take when opening a blank form"
                })
                if form.beforeCreateDocument:
                    code+= "## START beforeCreateDocument {\n"
                    code+= form.beforeCreateDocument
                    code+= "\n## END beforeCreateDocument }\n\r"

            if self.request.get("FormField") != None:
                fieldID = self.request.get("FormField").split("/")
                field = self.context.getForm(fieldID[0]).getFormField(fieldID[1])

                if not field :
                    return "##Unknown"

                methods.append({
                    "id": "formula",
                    "name": "Formula",
                    "desc": "How to calculate field content"
                })
                if field.formula:
                    code+= "## START formula {\n"
                    code+= field.formula
                    code+= "\n## END formula }\n\r"

                methods.append({
                    "id": "validation_formula",
                    "name": "Validation formula",
                    "desc": "Evaluate the input validation"
                })
                if field.validation_formula:
                    code+= "## START validation_formula {\n"
                    code+= field.validation_formula
                    code+= "\n## END validation_formula }\n\r"

                methods.append({
                    "id": "html_attributes_formula",
                    "name": "HTML attributes formula",
                    "desc": "Inject DOM attributes in the field tag"
                })
                if field.html_attributes_formula:
                    code+= "## START html_attributes_formula {\n"
                    code+= field.html_attributes_formula
                    code+= "\n## END html_attributes_formula }\n\r"

            if self.request.get("FormAction") != None:
                actionID = self.request.get("FormAction").split("/")
                action = self.context.getForm(actionID[0]).getAction(actionID[1])

                methods.append({
                    "id": "content",
                    "name": "Parameter or code",
                    "desc": "Code or parameter depending on the action type"
                })
                if action.content:
                    code+= "## START content {\n"
                    code+= action.content
                    code+= "\n## END content }\n\r"

                methods.append({
                    "id": "hidewhen",
                    "name": "Hide when",
                    "desc": "Action is hidden if formula returns True"
                })
                if action.hidewhen:
                    code+= "## START hidewhen {\n"
                    code+= action.hidewhen
                    code+= "\n## END hidewhen }\n\r"

            if self.request.get("View") != None:
                viewID = self.request.get("View")
                view = self.context.getView(viewID)

                if not view:
                    return "##Unknown"

                methods.append({
                    "id": "selection_formula",
                    "name": "Selection formula",
                    "desc": "The view selection formula is a line of Python code which should return True or False. The formula will be evaluated for each document in the database to decide if the document must be displayed in the view or not. 'plominoDocument' is a reserved name in formulae: it returns the current Plomino document."
                })
                if view.selection_formula:
                    code+= "## START selection_formula {\n"
                    code+= view.selection_formula or ''
                    code+= "\n## END selection_formula }\n\r"

                methods.append({
                    "id": "form_formula",
                    "name": "Form formula",
                    "desc": "Documents open from the view will use the form defined by the following formula (they use their own form if empty)"
                })
                if view.form_formula:
                    code+= "## START form_formula {\n"
                    code+= view.form_formula or ''
                    code+= "\n## END form_formula }\n\r"

                methods.append({
                    "id": "onOpenView",
                    "name": "On open view",
                    "desc": "Action to take when the view is opened. If a string is returned, it is considered an error message, and the opening is not allowed."
                })
                if view.onOpenView:
                    code+= "## START onOpenView {\n"
                    code+= view.onOpenView or ''
                    code+= "\n## END onOpenView }\n\r"

            if self.request.get("ViewAction") != None:
                actionID = self.request.get("ViewAction").split("/")
                action = self.context.getView(actionID[0]).getAction(actionID[1])

                if not action:
                    return "##Unknown"

                methods.append({
                    "id": "content",
                    "name": "Parameter or code",
                    "desc": "Code or parameter depending on the action type"
                })
                if action.content:
                    code+= "## START content {\n"
                    code+= action.content
                    code+= "\n## END content }\n\r"

                methods.append({
                    "id": "hidewhen",
                    "name": "Hide when",
                    "desc": "Action is hidden if formula returns True"
                })
                if action.hidewhen:
                    code+= "## START hidewhen {\n"
                    code+= action.hidewhen
                    code+= "\n## END hidewhen }\n\r"

            if self.request.get("ViewColumn") != None:
                actionID = self.request.get("ViewColumn").split("/")
                column = self.context.getView(actionID[0]).getColumn(actionID[1])

                if not column:
                    return "##Unknown"

                methods.append({
                    "id": "formula",
                    "name": "Formula",
                    "desc": "Python code returning the column value."
                })
                if column.formula:
                    code+= "## START formula {\n"
                    code+= column.formula
                    code+= "\n## END formula }\n\r"

            if self.request.get("Agent") != None:
                agent = self.context.getAgent(self.request.get("Agent"))

                if not agent:
                    return "##Unknown"

                if agent.content:
                    code+= agent.content

            self.request.RESPONSE.setHeader(
                'content-type', 'text/plain; charset=utf-8')

            elements = {"code" : code, "methods" : methods}
            return json.dumps(elements)

        if self.request.method == "POST":
            alsoProvides(self.request,plone.protect.interfaces.IDisableCSRFProtection)

            self.request.RESPONSE.setHeader(
                'content-type', 'application/json; charset=utf-8')
            response = json.loads(self.request.BODY)
            type = response["Type"]
            id = response["Id"]
            code = response["Code"]

            if type == "Agent":
                self.context.getAgent(id).content = code
                return json.dumps({
                    "type": "OK"
                })

            methodList = self.getMethodsId(type)

            content = ""
            contents = []
            inside = False

            for lineNumber, line in enumerate(code.split('\n')):
                start_reg = re.match(r'^##\s*START\s+(.*){$', line)
                end_reg = re.match(r'^##\s*END\s+(.*)}$',line)

                if start_reg and not inside:
                    if start_reg.group(1).strip() in methodList:
                        methodName = start_reg.group(1).strip()
                        inside = True
                    else:
                        return json.dumps({
                            "type": "Error",
                            "error": "Method \""+start_reg.group(1).strip()+"\" doesn't exists",
                            "line": lineNumber+1
                        })

                elif end_reg and inside:
                    if end_reg.group(1).strip() != methodName:
                        return json.dumps({
                            "type": "Error",
                            "error": "END tag doesn't match START tag",
                            "line": lineNumber+1
                        })
                    contents.append({
                        "name": methodName,
                        "code": content
                    })
                    inside = False
                    content = ''
                elif not start_reg and not end_reg and inside:
                    content+= line+"\n"

                elif end_reg and not inside:
                    return json.dumps({
                        "type": "Error",
                        "error": "Unexpected END tag",
                        "line": lineNumber+1
                    })

                elif start_reg and inside:
                    return json.dumps({
                        "type": "Error",
                        "error": "Unexpected START tag",
                        "line": lineNumber+1
                    })

            element = self.getElementByType(type,id)
            for formula in contents:
                setattr(element,formula['name'],formula['code'].rstrip())

            return json.dumps({
                "type": "OK"
            })

    def getElementByType(self,type,name):
        if type == "Form":
            return self.context.getForm(name)

        if type == "FormField":
            id = name.split('/')
            return self.context.getForm(id[0]).getFormField(id[1])

        if type == "FormAction":
            id = name.split('/')
            return self.context.getForm(id[0]).getAction(id[1])

        if type == "View":
            return self.context.getView(name)

        if type == "ViewAction":
            id = name.split('/')
            return self.context.getView(id[0]).getAction(id[1])

        if type == "ViewColumn":
            id = name.split('/')
            return self.context.getView(id[0]).getColumn(id[1])

        if type == "Agent":
            return self.context.getAgent(name)

        return


    def getMethodsId(self,type):
        methodList = []
        for method in self.getMethods(type):
            methodList.append(method['id'])
        return methodList

    def getMethods(self,type):
        return {
            'Form': [{
                "id": "document_title",
                "name": "Document title formula",
                "desc": "Compute the document title"
            },{
                "id": "document_id",
                "name": "Document id formula",
                "desc": "Compute the document id at creation."
            },{
                "id": "search_formula",
                "name": "Search formula",
                "desc": "Leave blank to use default ZCatalog search"
            },{
                "id": "onCreateDocument",
                "name": "On create document",
                "desc": "Action to take when the document is created"
            },{
                "id": "onOpenDocument",
                "name": "On open document",
                "desc": "Action to take when the document is opened"
            },{
                "id": "beforeSaveDocument",
                "name": "Before save document",
                "desc": "Action to take before submitted values are saved into the document (submitted values are in context.REQUEST)"
            },{
                "id": "onSaveDocument",
                "name": "On save document",
                "desc": "Action to take when saving the document"
            },{
                "id": "onDeleteDocument",
                "name": "On delete document",
                "desc": "Action to take before deleting the document"
            },{
                "id": "onSearch",
                "name": "On submission of search form",
                "desc": "Action to take when submitting a search"
            },{
                "id": "beforeCreateDocument",
                "name": "Before document creation",
                "desc": "Action to take when opening a blank form"
            }],
            'FormField': [{
                "id": "formula",
                "name": "Formula",
                "desc": "How to calculate field content"
            },{
                "id": "validation_formula",
                "name": "Validation formula",
                "desc": "Evaluate the input validation"
            },{
                "id": "html_attributes_formula",
                "name": "HTML attributes formula",
                "desc": "Inject DOM attributes in the field tag"
            }],
            'FormAction': [{
                "id": "content",
                "name": "Parameter or code",
                "desc": "Code or parameter depending on the action type"
            },{
                "id": "hidewhen",
                "name": "Hide when",
                "desc": "Action is hidden if formula returns True"
            }],
            'View': [{
                "id": "selection_formula",
                "name": "Selection formula",
                "desc": "The view selection formula is a line of Python code which should return True or False. The formula will be evaluated for each document in the database to decide if the document must be displayed in the view or not. 'plominoDocument' is a reserved name in formulae: it returns the current Plomino document."
            },{
                "id": "form_formula",
                "name": "Form formula",
                "desc": "Documents open from the view will use the form defined by the following formula (they use their own form if empty)"
            },{
                "id": "onOpenView",
                "name": "On open view",
                "desc": "Action to take when the view is opened. If a string is returned, it is considered an error message, and the opening is not allowed."
            }],
            'ViewAction': [{
                "id": "content",
                "name": "Parameter or code",
                "desc": "Code or parameter depending on the action type"
            },{
                "id": "hidewhen",
                "name": "Hide when",
                "desc": "Action is hidden if formula returns True"
            }],
            'ViewColumn': [{
                "id": "formula",
                "name": "Formula",
                "desc": "Python code returning the column value."
            }]
        }[type]

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

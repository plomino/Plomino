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
            self.request.RESPONSE.setHeader(
                'content-type', 'text/plain; charset=utf-8')

            type = self.request.form.keys()[0]
            if type not in ["Form", "FormField", "FormAction", "FormHidewhen", "View", "ViewAction", "ViewColumn", "Agent"]:
                return "Parameter error"

            element = self.getElementByType(type, self.request.form[type])
            if not element:
                return "Name error"

            if type == "Agent":
                return json.dumps({"code" : element.content, "methods" : []})

            if type == "FormHidewhen":
                return json.dumps({"code" : element.formula, "methods" : []})

            methods = self.getMethods(type)
            code = ""

            for method in self.getMethodsId(type):
                formula = getattr(element, method, None)
                if formula:
                    code+= "## START "+method+" {\n"
                    code+= formula
                    code+= "\n## END "+method+" }\n\r"

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

            if type == "FormHidewhen":
                id = id.split('/')
                self.context.getForm(id[0]).getHidewhen(id[1]).formula = code
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

            for formula in methodList:
                setattr(element,formula,'')

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

        if type == "FormHidewhen":
            id = name.split('/')
            return self.context.getForm(id[0]).getHidewhen(id[1])

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
            },{
                "id": "selectionlistformula",
                "name": "Selection List Formula",
                "desc": "Formula to compute the selection list elements"
            },{
                "id": "documentslistformula",
                "name": "Documents list formula",
                "desc": "Formula to compute the linkable documents list (must return a list of 'label|docid_or_path')"
            },{
                "id": "jssettings",
                "name": "Javascript settings",
                "desc": "Google Vizualization code"
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
                    "label": field.title,
                    "url": field.absolute_url(),
                    "type" : 'PlominoField'
                })
            plomino_form = []
            plomino_form.append({
                "label" : "Fields",
                "folder" : True,
                "children" : fields,
                "type" : "PlominoField",
                "url" : form.absolute_url()
            })
            actions = []
            for action in form.getFormActions():
                actions.append({
                    "label": action.title,
                    'type' : 'PlominoAction',
                    "url" : action.absolute_url()
                })
            plomino_form.append({
                "label": "Actions",
                "folder": True,
                "children": actions,
                "type" : "PlominoAction",
                "url" : form.absolute_url()
            })
            hide_whens = []
            for hide_when in form.getHidewhenFormulas():
                hide_whens.append({
                    "label": hide_when.title,
                    'type' : 'PlominoHidewhen',
                    "url" : hide_when.absolute_url()
                })
            plomino_form.append({
                "label": "Hide Whens",
                "folder": True,
                "children": hide_whens,
                "type" : "PlominoHidewhen",
                "url" : form.absolute_url()
            })
            forms.append({
                "label": form.title,
                "folder": True,
                "children": plomino_form,
                "type" : "PlominoForm",
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
                    "label": action[0].title,
                    "type": 'PlominoAction',
                    "url": action[0].absolute_url()
                })
            plomino_view.append({
                "label": "Actions",
                "folder": True,
                "children": actions,
                "type": "PlominoAction",
                "url": view.absolute_url()
            })
            columns = []
            for column in view.getColumns():
                columns.append({
                    "label": column.title,
                    "type": "PlominoColumn",
                    "url": column.absolute_url()
                })
            plomino_view.append({
                "label": "Columns",
                "folder": True,
                "children": columns,
                "type": "PlominoColumn",
                "url": view.absolute_url()
            })
            views.append({
                "label": view.title,
                "type": "PlominoView",
                "children": plomino_view,
                "url": view.absolute_url(),
            })


        # Create Agents View
        agents = []
        for agent in database.getAgents():

            agents.append({
                "label" : agent.title,
                "type" : "PlominoAgent",
                "url" : agent.absolute_url()
            })

        # Build the final element tree
        elements = [
            {
                "label": "Forms",
                "folder": True,
                "children": forms,
                "type" : 'PlominoForm',
                "url" : database.absolute_url()
            },
            {
                "label": "Views",
                "folder": True,
                "children": views,
                "type" : 'PlominoView',
                "url" : database.absolute_url()
            },
            {
                "label": "Agents",
                "folder": True,
                "children": agents ,
                "type" : 'PlominoAgent',
                "url" : database.absolute_url()
            }
        ]
        self.request.RESPONSE.setHeader(
            'content-type', 'application/json; charset=utf-8')
        return json.dumps(elements)

    def acl(self):
        return self.acl_template()

    def replication(self):
        return self.replication_template()

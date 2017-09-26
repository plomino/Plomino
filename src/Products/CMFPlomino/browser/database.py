from AccessControl import Unauthorized
from jsonutil import jsonutil as json
from plone.behavior.interfaces import IBehaviorAssignable
from plone.dexterity.interfaces import IDexterityFTI
from zope import component
from zope.schema import getFieldsInOrder
from Products.CMFPlomino.utils import PlominoTranslate
import re
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.interface import alsoProvides
import plone.protect.interfaces
from zope.lifecycleevent import modified

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
                #TODO: Not sure this is a good idea. Bad UX to be inconsistent
                return json.dumps({"code" : element.formula, "methods" : []})

            methods = self.getMethods(element=element)
            code = ""

            for method in self.getMethodsId(element=element):
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

            element = self.getElementByType(type,id)
            methodList = self.getMethodsId(element=element)

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


            for formula in methodList:
                setattr(element,formula,u'')

            for formula in contents:
                setattr(element,formula['name'],formula['code'].rstrip())

            # have to ensure pythons scripts get cleared
            modified(element)

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


    def getMethodsId(self,type=None, element=None):
        methodList = []
        for method in self.getMethods(type=type,element=element):
            methodList.append(method['id'])
        return methodList

    def getMethods(self,type=None, element=None):
        """ type comes in the form of ViewAction, FormAction etc
        """

        db = self.context.getParentDatabase()
        i18n_domain = db.i18n

        if type is not None:
            if type != 'Form' and type != 'View':
                type = type.replace('Form','').replace('View','')
            schema = component.getUtility(IDexterityFTI, name='Plomino'+type).lookupSchema()
            schemas = [schema]
        else:
            schema = element.getTypeInfo().lookupSchema()
            assignable = IBehaviorAssignable(element)
            schemas = [schema] + [behaviour.interface for behaviour in assignable.enumerateBehaviors()]
        methods = []
        for schema in schemas:
            widgets = schema.queryTaggedValue(u'plone.autoform.widgets', {})
            for name,field in getFieldsInOrder(schema):
                #field = schema.get(name)
                widget = widgets.get(name, None)
                if widget is None:
                    continue
                # bit of a HACK
                if widget.params.get('klass') == 'plomino-formula':
                    methods.append(dict(
                        id=name,
                        name=PlominoTranslate(field.title, db, domain=i18n_domain),
                        desc=PlominoTranslate(field.description, db, domain=i18n_domain),
                    ))
        return methods


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

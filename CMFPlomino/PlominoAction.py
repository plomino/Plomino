#################################################################################
#                                                                               #
#                               Eric BREHAULT - 2006                            #
#                                                                               #
#################################################################################

from Products.Archetypes.public import *
from Products.CMFCore import CMFCorePermissions
from AccessControl import ClassSecurityInfo
from Products.CMFPlomino.config import PROJECTNAME

class PlominoAction(BaseContent):
	""" Plomino Action """
	ACTION_TYPES = [["OPENFORM", "Open form"], ["OPENVIEW", "Open view"], ["CLOSE", "Close"], ["SAVE", "Save"], ["PYTHON", "Python script"]]
	ACTION_DISPLAY = [["LINK", "Link"], ["SUBMIT", "Submit button"], ["BUTTON", "Button"]]	
	
	schema = BaseSchema + Schema((
		StringField('Description', widget=TextAreaWidget(label='Description')),
		StringField('Label',widget=StringWidget(label='Label')),
		StringField('ActionType',widget=SelectionWidget(label='Type'), vocabulary=ACTION_TYPES),
		StringField('ActionDisplay',widget=SelectionWidget(label='Display'), vocabulary=ACTION_DISPLAY),
		TextField('Content', widget=TextAreaWidget(label='Parameter or code'))
		))
	
	content_icon = "PlominoAction.gif"
	
	security = ClassSecurityInfo()

	security.declareProtected(CMFCorePermissions.View, 'executeAction')
	def executeAction(self, target):
		""" return the action resulting url """
		db = self.getParentDatabase()
		if self.ActionType == "OPENFORM":
			form = db.getForm(self.Content())
			return form.absolute_url() + '/OpenForm'
		elif self.ActionType == "OPENVIEW":
			view = db.getView(self.Content())
			return view.absolute_url() + '/OpenView'
		elif self.ActionType == "CLOSE":
			return db.absolute_url() + '/OpenDatabase'
		elif self.ActionType == "PYTHON":
			if target is None:
				targetid="None"
			else:
				targetid=target.id
			return self.absolute_url() + '/runScript?target='+targetid
		else:
			return '.'
		
	security.declareProtected(CMFCorePermissions.View, 'runScript')
	def runScript(self, REQUEST):
		""" execute the python code """
		target = REQUEST.get('target')
		if target == "None":
			plominoContext = self.getParentDatabase()
		else:
			plominoContext = self.getParentDatabase()._getOb(target)
		plominoReturnURL = plominoContext.absolute_url()
		try:
			formula = self.Content().replace('\r\n', '; ')
			exec formula
			REQUEST.RESPONSE.redirect(plominoReturnURL)
		except Exception, e:
			return "Error: %s \nCode->\n%s" % (e, self.Content())
		
registerType(PlominoAction, PROJECTNAME)
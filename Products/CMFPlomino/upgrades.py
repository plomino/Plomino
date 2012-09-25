from Products.CMFCore.utils import getToolByName

default_profile = 'profile-Products.CMFPlomino:default'

def upgrade_22_to_23(context):
    #install collective.js.jqueryui as new dependency
    setup = getToolByName(context, 'portal_setup')
    setup.runAllImportStepsFromProfile('profile-collective.js.jqueryui:default',
                                   purge_old=False)

    #remove ++resource++plomino.javascript/jquery-ui-1.7.3.custom.min.js
    js_id = '++resource++plomino.javascript/jquery-ui-1.7.3.custom.min.js'
    jsregistry = getToolByName(context, 'portal_javascripts')
    jsregistry.unregisterResource(js_id)
    
    #remove jquery-ui-1.7.3.custom.css
    css_id = 'jquery-ui-1.7.3.custom.css'
    cssregistry = getToolByName(context, 'portal_css')
    cssregistry.unregisterResource(css_id)

def upgrade_to_28(context):
    # register plomino.debug.js
    # (it should have been done earlier, as plomino.debug.js was added in
    # version 1.8)
    context.runImportStepFromProfile(default_profile, 'jsregistry')

def upgrade_to_30(context):
    # register plomino.codemirror.js and 
    context.runImportStepFromProfile(default_profile, 'jsregistry')

def upgrade_to_31(context):
    qi = getToolByName(context, 'portal_quickinstaller')
    if not qi.isProductInstalled('collective.js.datatables'):
        qi.installProducts(products=['collective.js.datatables'])
    #remove datatables from plomino
    jsregistry = getToolByName(context, 'portal_javascripts')
    jsid = "++resource++plomino.javascript/jquery.dataTables.js"
    jsregistry.unregisterResource(jsid)
    jsregistry.cookResources()
    cssregistry = getToolByName(context, 'portal_css')
    cssid = "datatable.css"
    cssregistry.unregisterResource(cssid)
    cssregistry.cookResources()

def upgrade_to_32(context):
    # refresh PlominoView type settings 
    context.runImportStepFromProfile(default_profile, 'typeinfo')

def upgrade_to_33(context):
    # refresh js
    context.runImportStepFromProfile(default_profile, 'jsregistry')
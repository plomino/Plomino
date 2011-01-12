from Products.CMFCore.utils import getToolByName

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
    
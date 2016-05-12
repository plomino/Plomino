PROFILE_ID = 'profile-Products.CMFPlomino:default'


def run_registry_step(context):
    context.runImportStepFromProfile(PROFILE_ID, 'plone.app.registry')

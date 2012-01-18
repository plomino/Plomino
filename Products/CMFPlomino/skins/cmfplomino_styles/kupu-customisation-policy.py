## Script (Python) "kupu-customisation-policy"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Kupu Customisation Policy
##

# Make a copy of this script called 'kupu-customisation-policy'
# in any skin folder on your site and edit it to set up your own
# preferred kupu configuration.
from Products.CMFCore.utils import getToolByName

LINKABLE_BLACKLIST = (
    'ATBooleanCriterion',
    'ATCurrentAuthorCriterion',
    'ATDateCriteria',
    'ATDateRangeCriterion',
    'ATListCriterion',
    'ATPathCriterion',
    'ATPortalTypeCriterion',
    'ATReferenceCriterion',
    'ATRelativePathCriterion',
    'ATSelectionCriterion',
    'ATSimpleIntCriterion',
    'ATSimpleStringCriterion',
    'ATSortCriterion',
    'ChangeSet',
    'CMF Document',
    'CMF Event',
    'CMF Favorite',
    'CMF File',
    'CMF Image',
    'CMF Link',
    'CMF News Item',
    'Discussion Item',
    'Favorite',
    'Link',
    'TempFolder',
)
RESOURCES = dict(
    linkable = ('blacklist', LINKABLE_BLACKLIST),
    mediaobject = ('whitelist', ('Image',)),
    collection = ('whitelist', ('Plone Site', 'Folder', 'Large Plone Folder')),
    containsanchors = ('whitelist', ('Document', 'News Item', 'Event')),
    )

EXCLUDED_HTML = [
  {'tags': ('center','tt','big','small','basefont','font',),
   'attributes':(),
   'keep': 1 },

  {'tags':(),
  'attributes': ('lang','valign','halign','border','frame',
      'rules','cellspacing','cellpadding','bgcolor'),
   'keep': 1},

  {'tags': ('table','th','td'),
   'attributes': ('width','height'),
   'keep': 1},

   {'tags': '', 'attributes': '' } # Must be dummy entry at end.
]

STYLE_WHITELIST = ['text-align', 'list-style-type', 'float', 'plominoFieldClass', 'plominoActionClass', 'plominoHidewhenClass', 'plominoSubformClass']
CLASS_BLACKLIST = ['MsoNormal', 'MsoTitle', 'MsoHeader', 'MsoFootnoteText',
        'Bullet1', 'Bullet2']

TABLE_CLASSNAMES = ('plain', 'listing', 'grid', 'data')

PARAGRAPH_STYLES = (
    "Heading|h2",
    "Subheading|h3",
    "Literal|pre",
    "Discreet|p|discreet",
    "Pull-quote|div|pullquote",
    "Call-out|p|callout",
    "Highlight|span|visualHighlight",
    "Odd row|tr|odd",
    "Even row|tr|even",
    "Heading cell|th|",
    "Plomino Field|span|plominoFieldClass",
    "Plomino Action|span|plominoActionClass",
    "Plomino Hide-when formula|span|plominoHidewhenClass",
    "Plomino Subform|span|plominoSubformClass",
    "Plomino Cache|span|plominoCacheClass"
#    'Fancy|div|fancyClass',
#    'Plain|div|plainClass',
)

LIBRARIES = (
    dict(id="root",
         title="string:Home",
         uri="string:${globals_view/navigationRootUrl|portal_url}",
         src="string:${globals_view/navigationRootUrl|portal_url}/kupucollection.xml",
         icon="string:${globals_view/navigationRootUrl|portal_url}/misc_/CMFPlone/plone_icon"),
    dict(id="current",
         title="string:Current folder",
         uri="string:${folder_url}",
         src="string:${folder_url}/kupucollection.xml",
         icon="string:${folder/getIcon}"),
    dict(id="myitems",
         title="string:My recent items",
         uri="string:${portal_url}/kupumyitems.xml",
         src="string:${portal_url}/kupumyitems.xml",
         icon="string:${portal_url}/kupuimages/kupusearch_icon.gif"),
    dict(id="recentitems",
         title="string:Recent items",
         uri="string:${portal_url}/kupurecentitems.xml",
         src="string:${portal_url}/kupurecentitems.xml",
         icon="string:${portal_url}/kupuimages/kupusearch_icon.gif")
    )
DEFAULT_LIBRARY = 'current'

INSTALL_BEFOREUNLOAD = False
LINKBYUID = False
CAPTIONING = False

tool = getToolByName(context, 'kupu_library_tool')
typetool = getToolByName(context, 'portal_types')

# This code generates preview URLs automatically from the most
# appropriately sized image (if you have PIL installed) or just an
# image field (if you don't).
#
# If you have content types which don't always have an image, or if
# this picks the wrong preview URL, you might want to change these
# expressions.
PREVIEW_EXPR = 'string:${object_url}/%s'
PREVIEW = [ { 'portal_type': type,
    'expression': PREVIEW_EXPR % image,
    'normal': None,
    'scalefield': image.split('_',1)[0],
    'classes': '',
    'mediatype': 'image',
    }
            for (type, image) in tool.getPreviewable() ]
# e.g. PREVIEW=[{'portal_type': 'Image',
#                'expression':'string:${object_url}/image_thumb'
#                'normal': 'string:$object_url',
#                'scalefield': 'image' }]

for p in PREVIEW:
    print p['portal_type'], p['expression']

print "add preview actions"
tool.updatePreviewActions(PREVIEW)


def typefilter(types):
    all_meta_types = dict([ (t.id, 1) for t in typetool.listTypeInfo()])
    return [ t for t in types if t in all_meta_types ]

print "remove old resources"
types = tool.zmi_get_resourcetypes()
tool.deleteResourceTypes([ t.name for t in types])

print "add resources"
for k,(mode,types) in RESOURCES.items():
    tool.addResourceType(k, typefilter(types), mode=mode)

mappings = tool.zmi_get_resourcetypes()
for t in mappings:
    print t.name, ", ".join(t.types)

print "remove old libraries"
libs = tool.zmi_get_libraries()
tool.deleteLibraries(range(len(libs)))

print "add libraries"
for lib in LIBRARIES:
    tool.addLibrary(**lib)

for lib in tool.zmi_get_libraries():
    keys = lib.keys()
    keys.remove('id')
    keys.sort()
    print lib['id']
    for k in (keys):
        print '   ',k, lib[k]

tool.zmi_set_default_library(DEFAULT_LIBRARY)

print "configure kupu"
tool.configure_kupu(
    table_classnames = TABLE_CLASSNAMES,
    parastyles=PARAGRAPH_STYLES,
    html_exclusions = EXCLUDED_HTML,
    style_whitelist = STYLE_WHITELIST,
    class_blacklist = CLASS_BLACKLIST,
    installBeforeUnload=INSTALL_BEFOREUNLOAD,
    linkbyuid=LINKBYUID,
    captioning=CAPTIONING,
    )

return printed

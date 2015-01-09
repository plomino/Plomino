from AccessControl import ClassSecurityInfo

security = ClassSecurityInfo()

PROJECTNAME = 'CMFPlomino'

VERSION = "1.19.2"

import logging
logger = logging.getLogger('Plomino')

import os
TIMEZONE = os.environ.get('TZ', None)
if TIMEZONE:
    from DateTime import Timezones
    if TIMEZONE not in Timezones():
        logger.info('Specified timezone not recognized: %s, '
                'defaulting to local timezone.' % TIMEZONE)
        TIMEZONE = None
if not TIMEZONE:
    from DateTime import DateTime
    TIMEZONE = DateTime().timezone()

security.declarePublic('ADD_DESIGN_PERMISSION')
ADD_DESIGN_PERMISSION = 'CMFPlomino: Add Plomino design elements'
security.declarePublic('ADD_CONTENT_PERMISSION')
ADD_CONTENT_PERMISSION = 'CMFPlomino: Add Plomino content'
security.declarePublic('READ_PERMISSION')
READ_PERMISSION = 'CMFPlomino: Read documents'
security.declarePublic('EDIT_PERMISSION')
EDIT_PERMISSION = 'CMFPlomino: Edit documents'
security.declarePublic('CREATE_PERMISSION')
CREATE_PERMISSION = 'CMFPlomino: Create documents'
security.declarePublic('REMOVE_PERMISSION')
REMOVE_PERMISSION = 'CMFPlomino: Remove documents'
security.declarePublic('DESIGN_PERMISSION')
DESIGN_PERMISSION = 'CMFPlomino: Modify Database design'
security.declarePublic('ACL_PERMISSION')
ACL_PERMISSION = 'CMFPlomino: Control Database ACL'

FIELD_TYPES = {
        "TEXT": ["Text", "FieldIndex"],
        "NUMBER": ["Number", "FieldIndex"],
        "RICHTEXT": ["Rich text", "ZCTextIndex"],
        "DATETIME": ["Date/Time", "DateIndex"],
        "NAME": ["Name", "FieldIndex"],
        "SELECTION": ["Selection list", "KeywordIndex"],
        "ATTACHMENT": ["File attachment", "ZCTextIndex"],
        "DOCLINK": ["Doclink", "KeywordIndex"],
        "GOOGLECHART": ["Google chart", "FieldIndex"],
        "GOOGLEVISUALIZATION": ["Google visualization", "FieldIndex"],
        "BOOLEAN": ["Boolean", "FieldIndex"],
        }

FIELD_MODES = [
        ["EDITABLE", "Editable"],
        ["COMPUTED", "Computed"],
        ["CREATION", "Computed on creation"],
        ["DISPLAY", "Computed for display"],
        ["COMPUTEDONSAVE", "Computed on save"]
        ]

#FCKeditor configuration styles
FCK_STYLES = '''
<Style name="Heading" element="h2" />
<Style name="Subheading" element="h3" />
<Style name="Literal" element="pre" />
<Style name="Discreet paragraph" element="p">
  <Attribute name="class" value="discreet" />
</Style>
<Style name="Pull-quote" element="div">
  <Attribute name="class" value="pullquote" />
</Style>
<Style name="Call-out" element="p">
  <Attribute name="class" value="callout" />
</Style>
<Style name="Highlight" element="span">
  <Attribute name="class" value="visualHighlight" />
</Style>
<Style name="Heading cell" element="th" />
<Style name="Plomino Label" element="span">
  <Attribute name="class" value="plominoLabelClass" />
</Style>
<Style name="Plomino Legend" element="span">
  <Attribute name="class" value="plominoLegendClass" />
</Style>
<Style name="Plomino Field" element="span">
  <Attribute name="class" value="plominoFieldClass" />
</Style>
<Style name="Plomino Action" element="span">
  <Attribute name="class" value="plominoActionClass" />
</Style>
<Style name="Plomino Hide-when formula" element="span">
  <Attribute name="class" value="plominoHidewhenClass" />
</Style>
<Style name="Plomino Subform" element="span">
  <Attribute name="class" value="plominoSubformClass" />
</Style>'''

MSG_SEPARATOR = '\n'

SCRIPT_ID_DELIMITER = '_-_'


ADD_DESIGN_PERMISSION = 'CMFPlomino: Add Plomino design elements'
ADD_CONTENT_PERMISSION = 'CMFPlomino: Add Plomino content'
READ_PERMISSION = 'CMFPlomino: Read documents'
EDIT_PERMISSION = 'CMFPlomino: Edit documents'
CREATE_PERMISSION = 'CMFPlomino: Create documents'
REMOVE_PERMISSION = 'CMFPlomino: Remove documents'
DESIGN_PERMISSION = 'CMFPlomino: Modify Database design'
ACL_PERMISSION = 'CMFPlomino: Control Database ACL'

SCRIPT_ID_DELIMITER = '_-_'

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
    ["COMPUTEDONSAVE", "Computed on save"],
]

export var DATA: any =
[{
    "folder": true,
    "type": "database",
    "children": [{
        "url": "http://localhost:8080/Plone/testdb/formulaire2",
        "folder": true,
        "type": "form",
        "children": [{
            "folder": true,
            "type": "fields",
            "children": [],
            "label": "Fields"
        }, {
            "folder": true,
            "type": "actions",
            "children": [],
            "label": "Actions"
        }],
        "label": "formulaire2"
    }, {
        "url": "http://localhost:8080/Plone/testdb/test",
        "folder": true,
        "type": "form",
        "children": [{
            "folder": true,
            "type": "fields",
            "children": [{
                "url": "http://localhost:8080/Plone/testdb/test/mot",
                "type": "field",
                "label": "mot"
            }],
            "label": "Fields"
        }, {
            "folder": true,
            "type": "actions",
            "children": [{
                "url": "http://localhost:8080/Plone/testdb/test/testtest",
                "type": "action",
                "label": "testtest"
            }],
            "label": "Actions"
        }],
        "label": "test"
    }],
    "label": "Forms"
}, {
    "folder": true,
    "type": "views",
    "children": [{
        "url": "http://localhost:8080/Plone/testdb/testview",
        "type": "view",
        "children": [{
            "folder": true,
            "type": "actions",
            "children": [],
            "label": "Actions"
        }, {
            "folder": true,
            "type": "columns",
            "children": [],
            "label": "Columns"
        }],
        "label": "testview"
    }],
    "label": "Views"
}, {
    "folder": true,
    "type": "agents",
    "children": [],
    "label": "Agents"
}]

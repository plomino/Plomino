import {Component} from 'angular2/core';
import {TreeElementComponent} from './tree-element.component';

@Component({
    selector: 'my-tree',
    templateUrl: 'app/tree.component.html',
    directives: [TreeElementComponent]
})
export class TreeComponent {
    /* data:any = [{name: 'Contact (form)',
        children: [
            {name: 'Layout',
            children: [
                {name: 'Form1',
                    children: [
                        {name: 'Test1'}
                    ]},
                {name: 'Form2'}
            ]},
            {name: 'Settings',
            children: [
                {name: 'Form1'},
                {name: 'Form2'}
            ]}
        ]
    }];*/

    data:any = [{"folder": true, "type": "database", "children": [{"url": "http://localhost:8080/Plone/testdb/test", "folder": true, "type": "form", "children": [{"folder": true, "type": "fields", "children": [{"url": "http://localhost:8080/Plone/testdb/test/mot", "type": "field", "label": "mot"}], "label": "Fields"}, {"folder": true, "type": "actions", "children": [{"url": "http://localhost:8080/Plone/testdb/test/testtest", "type": "action", "label": "testtest"}], "label": "Actions"}], "label": "test"}], "label": "Forms"}, {"folder": true, "type": "views", "children": [], "label": "Views"}, {"folder": true, "type": "agents", "children": [], "label": "Agents"}]
}

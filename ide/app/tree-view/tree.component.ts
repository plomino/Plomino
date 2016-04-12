import {Component} from 'angular2/core';
import {TreeElementComponent} from './tree-element.component';
import {TreeSearchComponent} from './tree-search.component';

@Component({
    selector: 'my-tree',
    templateUrl: 'app/tree-view/tree.component.html',
    directives: [TreeElementComponent, TreeSearchComponent]
})
export class TreeComponent {
    data:any = [{"folder": true, "type": "database", "children": [{"url": "http://localhost:8080/Plone/plominodb/formulaire", "folder": true, "type": "form", "children": [{"folder": true, "type": "fields", "children": [{"url": "http://localhost:8080/Plone/plominodb/formulaire/field", "type": "field", "label": "field"}], "label": "Fields"}, {"folder": true, "type": "actions", "children": [{"url": "http://localhost:8080/Plone/plominodb/formulaire/actiontest", "type": "action", "label": "actiontest"}], "label": "Actions"}], "label": "formulaire"}], "label": "Forms"}, {"folder": true, "type": "views", "children": [{"url": "http://localhost:8080/Plone/plominodb/testview", "type": "view", "children": [{"folder": true, "type": "actions", "children": [], "label": "Actions"}, {"folder": true, "type": "columns", "children": [], "label": "Columns"}], "label": "testview"}], "label": "Views"}, {"folder": true, "type": "agents", "children": [], "label": "Agents"}]
}

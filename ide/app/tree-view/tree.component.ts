import {Component} from 'angular2/core';
import {TreeElementComponent} from './tree-element.component';
import {TreeService} from './tree.service';
import {BUTTON_DIRECTIVES} from 'ng2-bootstrap/ng2-bootstrap';

@Component({
    selector: 'my-tree',
    templateUrl: 'app/tree-view/tree.component.html',
    styleUrls: ['app/tree-view/tree.component.css'],
    directives: [TreeElementComponent],
    providers: [TreeService, BUTTON_DIRECTIVES]
})
export class TreeComponent {
    data: any;
    result: any;
    selected: any;
    input_value: string;

    constructor(private _treeService: TreeService) { }

    ngOnInit() {
        this.getTree();
    }

    getTree() {
        this._treeService.getTree().then(data => { this.data = data; this.result = data });
    }

    onSelect(event: any) {
        this.selected = event;
    }

    createNew(){
        console.log("Create new "+this.selected.type+" with name "+this.input_value);
    }

    delete(){
        console.log("Delete "+this.selected.type+" named "+this.selected.label);
    }

    search(pdata: any) {
        this.result = [];
        if (this.input_value != "")
            this.search_child(pdata);
        else
            this.result = this.data;
    }

    search_child(pdata: any) {
        for (var key in pdata) {
            if (pdata[key].label.toLowerCase().indexOf(this.input_value.toLowerCase()) != -1) {
                this.result.push(pdata[key]);
            }
            else {
                this.search_child(pdata[key].children);
            }
        }
    }
}

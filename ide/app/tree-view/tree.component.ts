import { Component, Input, Output, EventEmitter } from 'angular2/core';
import { Collapse }                               from 'ng2-bootstrap/ng2-bootstrap';

@Component({
    selector: 'my-tree',
    templateUrl: 'app/tree-view/tree.component.html',
    styleUrls: ['app/tree-view/tree.component.css'],
    directives: [ Collapse ]
})
export class TreeComponent {
    @Input() data: any;
    @Input() selected: any;
    @Output() edit = new EventEmitter();
    @Output() add = new EventEmitter();

    onEdit(event: any){
        this.edit.emit(event);
    }
    onAdd(event: any){
        this.add.emit(event);
    }
}

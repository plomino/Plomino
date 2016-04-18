import {Input, Output, EventEmitter, Component} from 'angular2/core';

@Component({
    selector: 'my-tree-element',
    templateUrl: 'app/tree-view/tree-element.component.html',
    styleUrls: ['app/tree-view/tree-element.component.css'],
    directives: [TreeElementComponent]
})
export class TreeElementComponent {
    @Input() data: any;
    @Output() select = new EventEmitter();
    @Output() edit = new EventEmitter();

    display: boolean = true;

    toggleDisplayChild(elt: any) {
        this.display = !this.display;
        this.onSelect(elt);
    }
    
    onSelect(event: any) {
        this.select.emit(event);
    }

    onEdit(event: any) {
        this.edit.emit(event);
    }
}

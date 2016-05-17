import { Component, Input, Output, EventEmitter, ViewChildren, OnChanges, ContentChild } from '@angular/core';
import { CollapseDirective }                                                             from 'ng2-bootstrap/ng2-bootstrap';

@Component({
    selector: 'my-tree',
    templateUrl: 'app/tree-view/tree.component.html',
    styleUrls: ['app/tree-view/tree.component.css'],
    directives: [CollapseDirective]
})
export class TreeComponent {
    @Input() data: any;
    @Input() selected: any;
    @Output() edit = new EventEmitter();
    @Output() add = new EventEmitter();
    @ViewChildren('selectable') element: any;

    previousSelected: any;

    isItSelected(name: any) {
        if (name === this.selected){
            if (this.selected != this.previousSelected) {
                this.previousSelected = this.selected;
                this.scroll();
            }
            return true;
        }
        else { return false; }
    }

    scroll() {
        if (this.element != undefined)
            for (let elt of this.element._results)
                if (elt.nativeElement.className === 'selected')
                    elt.nativeElement.scrollIntoView();
    }

    onEdit(event: any) {
        this.edit.emit(event);
    }
    onAdd(event: any) {
        this.add.emit(event);
    }
}

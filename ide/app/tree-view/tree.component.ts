import { Component, Input, Output, EventEmitter, ViewChildren, OnChanges, ContentChild } from '@angular/core';
import { CollapseDirective }                                                             from 'ng2-bootstrap/ng2-bootstrap';
import { ElementService }                                                                from '../services/element.service';
import { DND_DIRECTIVES }                                                                from 'ng2-dnd';

@Component({
    selector: 'plomino-tree',
    template: require('./tree.component.html'),
    styles: [require('./tree.component.css')],
    directives: [CollapseDirective, DND_DIRECTIVES],
    providers: [ElementService]
})
export class TreeComponent {
    @Input() data: any;
    @Input() selected: any;
    @Output() edit = new EventEmitter();
    @Output() add = new EventEmitter();
    @Output() isDragged = new EventEmitter();
    @ViewChildren('selectable') element: any;

    searchResults: any;
    filtered: boolean = false;
    previousSelected: any;

    constructor(private _elementService: ElementService) { }

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

    sendSearch(query: string) {
        if (query === '') {
            this.searchResults = null;
            this.filtered = false;
        }
        else
            this._elementService.searchElement(query).subscribe(
                data => { this.searchResults = data; this.filtered = true; },
                err => console.error(err)
            );
    }
}

import { 
    Component, 
    Input, 
    Output, 
    EventEmitter, 
    ViewChildren,
    OnInit,
    OnChanges, 
    ContentChild 
} from '@angular/core';

import { CollapseDirective } from 'ng2-bootstrap/ng2-bootstrap';
import { DND_DIRECTIVES } from 'ng2-dnd/ng2-dnd';

import { 
    ElementService,
    TabsService,
    DraggingService 
} from '../services';

import { ExtractNamePipe } from '../pipes';

@Component({
    selector: 'plomino-tree',
    template: require('./tree.component.html'),
    styles: [require('./tree.component.css')],
    directives: [CollapseDirective, DND_DIRECTIVES],
    pipes: [ExtractNamePipe],
    providers: [ElementService]
})
export class TreeComponent implements OnInit {
    @Input() data: any;
    @Output() openTab = new EventEmitter();
    @Output() add = new EventEmitter();
    @ViewChildren('selectable') element: any;
    
    selected: any;
    searchResults: any;
    filtered: boolean = false;
    previousSelected: any;

    constructor(private _elementService: ElementService,
                private tabsService: TabsService,
                public draggingService: DraggingService) { }
    
    ngOnInit() {
        this.tabsService.getActiveTab()
            .subscribe((activeTab) => {
                this.selected = activeTab;
            });
    }

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
        this.openTab.emit(event);
    }
    onAdd(event: any) {
        this.add.emit(event);
    }

    startDrag(data: any): void {
        this.draggingService.setDragging(data);
    }

    endDrag(): void {
        this.draggingService.setDragging(null);
    }

    openFieldSettings(fieldData: any): void {
        let id = fieldData.name.slice(fieldData.name.lastIndexOf('/') + 1);
        if ((this.selected && this.selected.url) !== fieldData.parent) {
            let tabLabel = fieldData.parent.slice(fieldData.parent.lastIndexOf('/') + 1);
            this.tabsService.openTab({
                editor: 'layout',
                label: tabLabel,
                url: fieldData.parent,
                path: [
                    {    
                        name: tabLabel,
                        type: 'Forms'
                    }
                ],
            }, false);
        }  
        this.tabsService.selectField({ id: id, type: fieldData.type, parent: fieldData.parent });
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

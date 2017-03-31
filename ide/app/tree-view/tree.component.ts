import { PlominoActiveEditorService } from './../services/active-editor.service';
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
import { DND_DIRECTIVES } from 'ng2-dnd';

import { 
    ElementService,
    TabsService,
    FormsService,
    DraggingService,
    LogService
} from '../services';

import { ExtractNamePipe } from '../pipes';
import { Observable, Subscription } from "rxjs/Rx";

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

    private click2DragDelay: Subscription;

    constructor(
      private _elementService: ElementService,
      private tabsService: TabsService,
      private formsService: FormsService,
      private log: LogService,
      private activeEditorService: PlominoActiveEditorService,
      public draggingService: DraggingService
    ) { }
    
    ngOnInit() {
      this.tabsService.getActiveTab()
        .subscribe((activeTab) => {
          this.log.info('activeTab', activeTab);
          this.log.extra('tree.component.ts ngOnInit');
          this.selected = activeTab;
        });
    }

    getCollapseState(collapseVar: any, selected: boolean) {
      return typeof collapseVar === 'undefined' && !selected 
        ? true : (collapseVar === null ? false : (collapseVar === true));
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

    selectDBSettingsTab() {
      this.formsService.changePaletteTab(3);
    }

    treeFormItemClick(
      selected: boolean, mouseEvent: MouseEvent, 
      typeLabel: string, typeNameUrl: string,
      typeNameLabel: string, formUniqueId: string
    ) {
      if (typeLabel === 'Views') {
        this.onEdit({
          formUniqueId: formUniqueId,
          label: typeNameLabel,
          url: typeNameUrl,
          editor: 'view',
          path: [{ name: typeNameLabel, type: typeLabel }]
        });
      }
      else {
        this.click2DragDelay = Observable.timer(500, 1000).subscribe((t: number) => {
          this.dragSubform(selected, mouseEvent, typeLabel, typeNameUrl);
          this.click2DragDelay.unsubscribe();
        });
      }
      return true;
    }

    dragSubform(selected: boolean, mouseEvent: MouseEvent, 
      typeLabel: string, typeNameUrl: string
    ) {
      this.log.info('drag subform', selected, mouseEvent, typeLabel, typeNameUrl);
      this.log.extra('tree.component.ts dragSubform');
      if (this.activeEditorService.getActive() && selected && typeLabel === 'Forms' 
        && typeNameUrl !== this.activeEditorService.getActive().id) {
        this.draggingService.subformDragEvent.next(mouseEvent);
      }
    }

    getTypeImage(childName: any) {
        return {
            'PlominoField': 'images/ic_input_black_18px.svg',
            'PlominoHidewhen': 'images/ic_remove_red_eye_black_18px.svg',
            'PlominoAction': 'images/ic_gavel_black_18px.svg',
            'PlominoForm': 'images/ic_featured_play_list_black_18px.svg',
            'PlominoView': 'images/ic_picture_in_picture_black_18px.svg',
        }[childName.type] || 'images/ic_input_black_18px.svg';
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

    onTreeFieldClick(fieldData: PlominoFieldTreeObject) {
      this.openFieldSettings(fieldData);
      this.selectFirstOccurenceInCurrentEditor(fieldData);
    }

    selectFirstOccurenceInCurrentEditor(fieldData: PlominoFieldTreeObject) {
      const $body = $(this.activeEditorService.getActive().getBody());
      $body.find('[data-mce-selected]').removeAttr('data-mce-selected');
      
      const $results = $body
        .find(
          `.plominoFieldClass[data-plominoid="${ fieldData.name.split('/').pop() }"]`
        );

      if ($results.length) {
        const $first = $results.first();
        $first.attr('data-mce-selected', '1');
      }
    }

    openFieldSettings(fieldData: PlominoFieldTreeObject): void {
      let id = fieldData.name.slice(fieldData.name.lastIndexOf('/') + 1);
      if ((this.selected && this.selected.url) !== fieldData.parent) {
        let tabLabel = fieldData.parent.slice(fieldData.parent.lastIndexOf('/') + 1);
        this.log.info('this.tabsService.openTab #t0001');
        this.tabsService.openTab({
          formUniqueId: this.selected.formUniqueId,
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
      this.tabsService.selectField({
        id: id, type: fieldData.type, parent: fieldData.parent
      });
    }

    sendSearch(query: string) {
        if (query === '') {
            this.searchResults = null;
            this.filtered = false;
        }
        else
            this._elementService.searchElement(query).subscribe(
                (data: any) => { this.searchResults = data; this.filtered = true; },
                (err: any) => console.error(err)
            );
    }
}

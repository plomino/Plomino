// import { TinyMCE } from 'mockup-patterns-tinymce';
// import { Modal } from 'mockup-patterns-modal';

// window.TinyMCE = TinyMCE();
// window.Modal = Modal;

// new window.TinyMCE();

// Core
import { 
    Component, 
    ViewChild,
    NgZone, 
    OnInit,
    AfterViewInit,
    ChangeDetectorRef,
    trigger,
    animate,
    state,
    style,
    transition
} from '@angular/core';

// External Components
import { TAB_DIRECTIVES } from 'ng2-bootstrap/ng2-bootstrap';
import { DND_DIRECTIVES } from 'ng2-dnd/ng2-dnd';

// Components
import { TreeComponent } from './tree-view';
import { PaletteComponent } from './palette-view';
import {
    TinyMCEComponent,
    ACEEditorComponent,
    FormsSettingsComponent,
    FieldsSettingsComponent,
    ActionsSettingsComponent,
    HideWhenSettingsComponent,
    ViewsSettingsComponent,
    ColumnsSettingsComponent,
    AgentsSettingsComponent
} from './editors';


// Services
import { 
    TreeService,
    ElementService,
    ObjService,
    TabsService,
    FieldsService,
    DraggingService,
    TemplatesService,
    WidgetService,
    FormsService
} from './services';

// Pipes 
import { ExtractNamePipe } from './pipes';

// Interfaces
import { IField } from './interfaces';

// Utility Components
import { PlominoModalComponent, ResizeDividerComponent } from './utility';

import 'lodash';
import {LoadingComponent} from "./editors/loading/loading.component";

declare let _: any;
declare let $: any;
declare let tinymce: any;

@Component({
    selector: 'plomino-app',
    template: require('./app.component.html'),
    styles: [require('./app.component.css')],
    directives: [
        TreeComponent,
        PaletteComponent,
        TAB_DIRECTIVES,
        DND_DIRECTIVES,
        TinyMCEComponent,
        ACEEditorComponent,
        PlominoModalComponent,
        FormsSettingsComponent,
        FieldsSettingsComponent,
        ActionsSettingsComponent,
        HideWhenSettingsComponent,
        ViewsSettingsComponent,
        ColumnsSettingsComponent,
        AgentsSettingsComponent,
        LoadingComponent,
        ResizeDividerComponent
    ],
    providers: [
        TreeService, 
        ElementService, 
        ObjService, 
        TabsService, 
        FieldsService,
        DraggingService,
        TemplatesService,
        WidgetService,
        FormsService
    ],
    pipes: [ExtractNamePipe],
    animations: [
        trigger('dropZoneState', [
            state('*', style({
                opacity: 1
            })),
            transition('void => *', [
                style({
                    opacity: 0
                }),
                animate(300)
            ]),
            transition('* => void', animate(300, style({
                opacity: 0
            })))
        ])
    ]
})
export class AppComponent implements OnInit, AfterViewInit {

    data: any;
    selectedField: IField;
    tabs: Array<any> = [];

    isModalOpen: boolean = false;
    modalData: any;

    isDragging: boolean = false;
    dragData: any = null;

    aceNumber: number = 0;

    DIRECTION_DOWN = 'down';
    DIRECTION_UP = 'up';
    DIRECTION_LEFT = 'left';
    DIRECTION_RIGHT = 'right';
    wrapperWidth: number = 464;

    constructor(private treeService: TreeService,     
                private elementService: ElementService, 
                private objService: ObjService,
                private tabsService: TabsService,
                private draggingService: DraggingService,
                private zone: NgZone,
                private changeDetector: ChangeDetectorRef) { }

    collapseTreeElements(data:any, oldData:any) {
        if(!Array.isArray(data) || Array.isArray(oldData))
            return data;

        data.forEach((item: any) => {
            item.collapsed = !(item.label === 'Forms' && item.type === 'PlominoForm');
            item.children = this.collapseTreeElements(item.children, null);
        });

        return data.slice();
    }

    ngOnInit() {
        this.treeService.getTree()
            .subscribe((tree) => {
                const data = this.collapseTreeElements(tree, this.data);
                if (!data) { return; }

                /* little callback hell */
                data.forEach((z: any, topIndex: number) => {
                    z.children.forEach((firstLevelChildrenItem: any, index: number) => {
                        
                        let tmp = firstLevelChildrenItem.children;
                        firstLevelChildrenItem.children.forEach((subChild: any) => {
                            tmp = tmp.concat(subChild.children);
                        });

                        tmp = tmp.filter((item: any) => {
                            return !item.folder;
                        });

                        data[topIndex].children[index].children = tmp;
                    })
                });
                
                /* extracting children of children */
                this.data = data;
                
            });
        
        this.tabsService.getTabs()
            .subscribe((tabs) => {
                this.tabs = tabs;
            })

        this.draggingService.getDragging()
            .subscribe((dragData: any) => {
                this.isDragging = !!dragData;
                this.dragData = dragData;
            })

        $(() => {
            $('.palette-wrapper')
            .css('height', `${ window.innerHeight / 2 }px`);

            window['Modal'] = require('mockup-patterns-modal');
            window['TineMCE'] = require('mockup-patterns-tinymce');
            require('./assets/scripts/macros.js');
            require('./assets/scripts/dynamic.js');
        });
    }

    ngAfterViewInit() {
        this.tabsService.getActiveTab()
            .subscribe((activeTab: any) => {
                
            });
    }

    getTabTypeImage(editor: any) {
        return {
            'layout': 'images/ic_featured_play_list_black_18px.svg',
            'code': 'images/ic_code_black_18px.svg',
        }[editor] || 'images/ic_code_black_18px.svg';
    }

    onAdd(event: any) {
        event.isAction = event.type == "PlominoAction";
        this.modalData = event;
        this.isModalOpen = true;
    }

    resizeColumns(event: { directions: string[], difference: {x: number, y: number} }) {
        const directions = event.directions;
        const difference = event.difference;

        const contains = (direction: string) => {
            return directions.indexOf(direction) !== -1;
        };

        if (!directions.length) { return; }

        const $wrapper = $('.well.sidebar');
        const attribute = 'width';
        let width = this.wrapperWidth;

        if (contains(this.DIRECTION_LEFT)) {
            width = width - difference.x - 1;
        }
        else if (contains(this.DIRECTION_RIGHT)) {
            width = width + difference.x + 1;
        }

        this.wrapperWidth = width;

        $wrapper
        // .css('-ms-flex-preferred-size', `${ width }px`)
        .css(attribute, `${ width }px`);

        /* for fixed tabs */
        // $('plomino-palette ul.nav-tabs')
        // .css('width', `${ $('.palette-wrapper').width() - 2 }px`);
    }

    resizeTree(event: { directions: string[], difference: {x: number, y: number} }) {
        const directions = event.directions;
        const difference = event.difference;

        const contains = (direction: string) => {
            return directions.indexOf(direction) !== -1;
        };

        if (!directions.length) { return; }

        const $wrapper = $('.palette-wrapper');
        let height = parseInt($wrapper.css('height').replace('px', ''), 10);

        if (contains(this.DIRECTION_UP)) {
            height = height - difference.y - 0.5;
        }
        else if (contains(this.DIRECTION_DOWN)) {
            height = height + difference.y;
        }

        $wrapper.css('height', `${ height }px`);
    }

    indexOf(type: any) {
        let index: any = {};
        let parentToSearch: any;

        if (type.parent === undefined)
            parentToSearch = type.type;
        else
            parentToSearch = type.parentType;

        switch (parentToSearch) {
            case 'Forms':
                index.parent = 0;
                break;
            case 'Views':
                index.parent = 1;
                break;
            case 'Agents':
                index.parent = 2;
                break;
        }

        if (type.parent != undefined) {
            index.index = this.searchParentIndex(type.parent, index.parent);
            switch (index.parent) {
                case 0:
                    switch (type.type) {
                        case 'Fields':
                            index.child = 0;
                            break;
                        case 'Actions':
                            index.child = 1;
                            break;
                    }
                    break;
                case 1:
                    switch (type.type) {
                        case 'Actions':
                            index.child = 0;
                            break;
                        case 'Columns':
                            index.child = 1;
                            break;
                    }
                    break;
            }
        }

        return index;

    }

    searchParentIndex(parent: string, index: number) {
        for (let i = 0; i < this.data[index].children.length; i++) {
            if (this.data[index].children[i].label === parent) return i;
        }
        return -1;
    }

    allowDrop() {
        let dataType = this.dragData['@type'];
        return () => dataType === 'PlominoForm' || dataType === 'PlominoView';
    }

    dropped() {
        this.resolveData(this.dragData, this.dragData.resolver);
    }

    openTab(tab: any) {
        this.tabsService.openTab(tab, true);
    }

    closeTab(tab: any) {
        this.tabsService.closeTab(tab);
        // if (tab.editor === 'code') this.aceNumber++; // What is this code for?
    }

    onModalClose(event: any) {
        this.isModalOpen = false;
        let newElement: any = {
            "@type": event.type,
            "title": event.name
        };
        if (event.type == "PlominoAgent")
            newElement.content = "";
        if (event.type == "PlominoAction")
            newElement.action_type = event.action_type;
        this.elementService.postElement(event.url,newElement)
            .subscribe(data => this.treeService.updateTree());
    }

    onTabSelect(tab: any) {
        this.tabsService.setActiveTab(tab, true);
    }

    fieldSelected(fieldData: any): void {
        this.tabsService.selectField(fieldData);
    }

    setTabzAsDirty(tabz: any, dirty: boolean) {
        tabz.isdirty = dirty;

        $(window)
        .unbind('beforeunload')
        .bind('beforeunload', (eventObject: any) => {
            if (tabz.isdirty) {
                return confirm('Do you want to close window. The form is unsaved.');
            }
        });
    }

    private resolveData(data: any, resolver: Function): void {
        resolver(data);
    }
}

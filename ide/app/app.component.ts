// Core
import { 
    Component, 
    ViewChild,
    NgZone, 
    OnInit,
    ChangeDetectorRef
} from '@angular/core';

// External Components
import { TAB_DIRECTIVES }               from 'ng2-bootstrap/ng2-bootstrap';

// Components
import { TreeComponent }                from './tree-view/tree.component';
import { PaletteComponent }             from './palette-view/palette.component';
import { TinyMCEComponent }             from './editors/tiny-mce.component';
import { ACEEditorComponent }           from './editors/ace-editor.component';
import { FormsSettingsComponent }       from './editors/settings/forms-settings.component';
import { FieldsSettingsComponent }      from './editors/settings/fields-settings.component';
import { ActionsSettingsComponent }     from './editors/settings/actions-settings.component';
import { HideWhenSettingsComponent }    from './editors/settings/hide_when-settings.component';
import { ViewsSettingsComponent }       from './editors/settings/views-settings.component';
import { ColumnsSettingsComponent }     from './editors/settings/columns-settings.component';
import { AgentsSettingsComponent }      from './editors/settings/agents-settings.component';
import { PlominoModalComponent }        from './modal.component';

// Services
import { 
    TreeService,
    ElementService,
    ObjService,
    TabsService 
}                                       from './services';

// Pipes 
import { ExtractNamePipe }              from './pipes';

// Interfaces
import { IField } from './interfaces';

import 'lodash';

declare let _: any;

@Component({
    selector: 'plomino-app',
    template: require('./app.component.html'),
    styles: [require('./app.component.css')],
    directives: [
        TreeComponent,
        PaletteComponent,
        TAB_DIRECTIVES,
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
        
    ],
    providers: [TreeService, ElementService, ObjService, TabsService],
    pipes: [ExtractNamePipe]
})
export class AppComponent {
    data: any;
    selected: any;
    selectedField: IField;
    tabs: Array<any> = [];

    isModalOpen: boolean = false;
    modalData: any;

    aceNumber: number = 0;

    constructor(private treeService: TreeService,     
                private elementService: ElementService, 
                private objService: ObjService,
                private tabsService: TabsService,
                private zone: NgZone,
                private changeDetector: ChangeDetectorRef) { }

    ngOnInit() {
        this.treeService.getTree()
            .subscribe((tree) => {
                this.data = tree;
            });
        
        this.tabsService.getTabs()
            .subscribe((tabs) => {
                console.log(`Tabs arrived! `, tabs);
                this.tabs = tabs;
            })
    }

    onAdd(event: any) {
        event.isAction = event.type == "PlominoAction";
        this.modalData = event;
        this.isModalOpen = true;
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


    openTab(tab: any) {
        this.tabsService.openTab(tab);
        // if (_.find(this.tabs, { url: event.url })) {
        //     return;
        // } else {
        //     this.tabs.push(this.buildTab(event));
        // }
    }

    closeTab(tab: any) {
        this.tabsService.closeTab(tab);
        // this.tabs.splice(this.tabs.indexOf(tab), 1);
        if (tab.editor === 'code') this.aceNumber++; // What is this code for?
        // if (this.tabs.length === 0) this.selected = null;
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


    index(type: string, parentIndex?: number) {
        if (parentIndex === undefined)
            switch (type) {
                case 'Forms':
                    return 0;
                case 'Views':
                    return 1;
                case 'Agents':
                    return 2;
            }
        else {
            switch (parentIndex) {
                case 0:
                    switch (type) {
                        case 'Fields':
                            return 0;
                        case 'Actions':
                            return 1;
                        case 'Hide Whens':
                            return 2;
                    }
                    break;
                case 1:
                    switch (type) {
                        case 'Actions':
                            return 0;
                        case 'Columns':
                            return 1;
                    }
                    break;
                case 2:
                    return 0;
            }
        }
    }

    onTabSelect(tab: any) {
        // this.selected = this.retrieveTab(path, url);
        // this.changeDetector.detectChanges();
        // this.tabsService.setActiveTab(tab);
    }

    fieldSelected(fieldId: string): void {
        this.zone.run(() => {
            this.selectedField = Object.assign({}, { id: fieldId, url: this.selected.url + '/' + fieldId });
        });
    }

    retrieveTab(path: any, url: string) {
        let pindex = this.index(path[0].type);
        for (let elt of this.data[pindex].children) {
            if (elt.url.split('/').pop() == url.split('/').pop()) {
                if (path.length > 1) {
                    let cindex = this.index(path[1].type, pindex);
                    for (let celt of elt.children[cindex].children) {
                        if (celt.label == path[1].name) {
                            return celt;
                        }
                    }
                }
                return elt;
            }
        }
    }

    buildTab(tab: any) {
        let newtab = { title: tab.label, editor: tab.editor, path: tab.path, url: tab.url };
        if (newtab.editor === 'code') {
            this.aceNumber++;
        }
        return newtab;
    }
}

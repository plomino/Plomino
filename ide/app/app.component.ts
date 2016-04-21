// Core
import { Component, ViewChild, OnInit } from 'angular2/core';

// External Components
import { TAB_DIRECTIVES }               from 'ng2-bootstrap/ng2-bootstrap';

// Components
import { TreeComponent }                from './tree-view/tree.component';
import { TinyMCEComponent }             from './editors/tiny-mce.component';
import { ACEEditorComponent }           from './editors/ace-editor.component';
import { MyModalComponent }             from './my-modal.component';

// Services
import { TreeService }                  from './services/tree.service';

@Component({
    selector: 'my-app',
    templateUrl: 'app/app.component.html',
    styleUrls: ['app/app.component.css'],
    directives: [TreeComponent, TAB_DIRECTIVES, TinyMCEComponent, ACEEditorComponent, MyModalComponent],
    providers: [TreeService]
})
export class AppComponent {
    data: any;

    selectedEditor: string;
    tabs: Array<any> = [];

    isModalOpen: boolean = false;
    modalData: any;

    aceNumber: number = 0;

    constructor(private _treeService: TreeService) { }

    ngOnInit() {
        this.getTree();
    }

    getTree() {
        this._treeService.getTree().then(data => { this.data = data });
    }

    onAdd(event: any) {
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

        switch(parentToSearch) {
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
            switch(index.parent){
                case 0:
                    switch(type.type){
                        case 'Fields':
                            index.child = 0;
                            break;
                        case 'Actions':
                            index.child = 1;
                            break;
                    }
                    break;
                case 1:
                    switch(type.type){
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


    onEdit(event: any) {
        this.tabs.push(this.buildTab(event));
    }

    onModalClose(event: any) {
        let index = this.indexOf(event);
        console.table(index);
        if (event.parent === undefined)
            this.data[index.parent].children.push({label:event.name});
        else
            this.data[index.parent].children[index.index].children[index.child].children.push({label:event.name});

        this.isModalOpen = false;
    }

    onTabClose(tab: any) {
        this.tabs.splice(this.tabs.indexOf(tab), 1);
        if (tab.editor === 'code') this.aceNumber++;
    }

    buildTab(tab: any) {
        let newtab = { title: tab.label, editor: tab.editor };
        if (newtab.editor === 'code') {
            newtab["code"] = "def " + newtab.title + `(param):
    print \'test\'
    return 4`;
            this.aceNumber++;
        }
        else if (newtab.editor === 'layout') {
            newtab["layout"] = "I am the content of " + newtab.title;
        }
        else if (newtab.editor === 'settings') {
            newtab["settings"] = "Name : <input><br>Stuff : <input>";
        }
        return newtab;
    }
}

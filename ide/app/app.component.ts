import {Component, ViewChild} from 'angular2/core';
import {TreeComponent} from './tree-view/tree.component';
import {TAB_DIRECTIVES} from 'ng2-bootstrap/ng2-bootstrap';
import {TinyMCEComponent} from './tiny-mce.component';
import {ACEEditorComponent} from './ace-editor.component';
import {MyModalComponent} from './my-modal.component';

@Component({
    selector: 'my-app',
    templateUrl: 'app/app.component.html',
    styleUrls: ['app/app.component.css'],
    directives: [TreeComponent, TAB_DIRECTIVES, TinyMCEComponent, ACEEditorComponent, MyModalComponent]
})
export class AppComponent {

    selectedEditor: string;
    tabs: Array<any> = [];

    isModalOpen: boolean = false;
    modalData: any;

    aceNumber: number = 0;

    onAdd(event: string) {
        this.modalData = { name: event };
        this.isModalOpen = true;
    }
    onEdit(event: any) {
        this.tabs.push(this.buildTab(event));
    }
    onModalClose(event: any) {
        if (event != undefined)
            this.tabs.push(this.buildTab(event));
            //this.tabs.push({ title: event.name, content: 'content of ' + event.name, editor: event.editor });

        this.isModalOpen = false;
    }
    onTabClose(tab: any) {
        this.tabs.splice(this.tabs.indexOf(tab), 1);
        if (tab.editor === 'code') this.aceNumber++;
    }

    buildTab(tab: any){
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
        else if(newtab.editor === 'settings') {
            newtab["settings"] = "Name : <input><br>Stuff : <input>";
        }
        return newtab;
    }

    showtabs() {
        console.table(this.tabs);
    }
}

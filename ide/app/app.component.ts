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

    onAdd(event: string) {
        this.modalData = {name: event};
        this.isModalOpen = true;
    }
    onEdit(event: any) {
        let newtab = { title: event.label, content: 'I am the content of <a>' + event.url+'</a>'};
        this.tabs.push(newtab);
    }
    onModalClose(event: any) {
        if(event != undefined)
            this.tabs.push({ title: event.name, content: 'content of '+event.name, editor:event.editor });

        this.isModalOpen = false;
    }
    onTabClose(tab: any) {
        this.tabs.splice(this.tabs.indexOf(tab), 1);
    }
    showtabs() {
        console.table(this.tabs);
    }
}

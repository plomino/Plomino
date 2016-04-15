import {Component, ViewChild} from 'angular2/core';
import {TreeComponent} from './tree-view/tree.component';
import {MODAL_DIRECTIVES, ModalComponent } from 'ng2-bs3-modal/ng2-bs3-modal';
import {TAB_DIRECTIVES} from 'ng2-bootstrap/ng2-bootstrap';
import {TinyMCEComponent} from './tiny-mce.component';

@Component({
    selector: 'my-app',
    templateUrl: 'app/app.component.html',
    styleUrls: ['app/app.component.css'],
    directives: [TreeComponent, MODAL_DIRECTIVES, TAB_DIRECTIVES, TinyMCEComponent]
})
export class AppComponent {
    @ViewChild('modal')
    modal: ModalComponent;

    selectedEditor: string;
    tabs: Array<any> = [];
    newName: string;

    onAdd(event: string) {
        this.newName = event;
        this.modal.open();
    }
    onEdit(event: any) {
        let newtab = { title: event.label, content: 'I am the content of <a>' + event.url+'</a>'};
        this.tabs.push(newtab);
    }
    onModalClose() {
        this.tabs.push({ title: this.newName, content: 'content of '+this.newName });
    }
    onTabClose(tab: any) {
        this.tabs.splice(this.tabs.indexOf(tab), 1);
    }
    showtabs() {
        console.table(this.tabs);
    }
}

import {Component, EventEmitter, Input, Output, ViewChild, AfterViewInit} from 'angular2/core';
import {MODAL_DIRECTIVES, ModalComponent } from 'ng2-bs3-modal/ng2-bs3-modal';
import {Alert} from 'ng2-bootstrap/ng2-bootstrap';

@Component({
    selector: 'my-modal',
    templateUrl: 'app/my-modal.component.html',
    directives: [MODAL_DIRECTIVES, Alert]
})
export class MyModalComponent {
    @Input() name: string;
    @Output() modalClosed = new EventEmitter();
    @ViewChild('modal') modal: ModalComponent;

    editor: string = 'tinymce';
    newName: string = "";
    nameError: boolean = false;

    ngAfterViewInit() {
        this.modal.open();
    }
    onModalClose(event: any) {
        if (event != undefined && !/\S/.test(event.name)) {
            this.nameError = true;
            this.modal.open();
        }
        else {
            this.modalClosed.emit(event);
        }
    }
    changeEditor(event: string) {
        this.editor = event;
    }
}

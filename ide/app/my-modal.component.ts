import {Component, EventEmitter, Input, Output, ViewChild, AfterViewInit} from 'angular2/core';
import {MODAL_DIRECTIVES, ModalComponent } from 'ng2-bs3-modal/ng2-bs3-modal';
import {Alert} from 'ng2-bootstrap/ng2-bootstrap';

@Component({
    selector: 'my-modal',
    templateUrl: 'app/my-modal.component.html',
    directives: [MODAL_DIRECTIVES, Alert]
})
export class MyModalComponent {
    @Input() data: any;
    @Output() modalClosed = new EventEmitter();
    @Output() modalDismissed = new EventEmitter();
    @ViewChild('modal') modal: ModalComponent;

    nameError: boolean = false;

    ngAfterViewInit() {
        this.modal.open();
    }
    onModalClose() {
        if (this.data.name === undefined || !/\S/.test(this.data.name)) {
            this.nameError = true;
            this.modal.open();
        }
        else {
            this.modalClosed.emit(this.data);
        }
    }
    onModalDismiss() {
        this.modalDismissed.emit(true);
    }
}

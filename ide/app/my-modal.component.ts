import {Component, EventEmitter, Input, Output, ViewChild, AfterViewInit} from '@angular/core';
import {MODAL_DIRECTIVES, ModalComponent } from 'ng2-bs3-modal/ng2-bs3-modal';
import {AlertComponent} from 'ng2-bootstrap/ng2-bootstrap';

@Component({
    selector: 'my-modal',
    template: require('./my-modal.component.html'),
    directives: [MODAL_DIRECTIVES, AlertComponent]
})
export class MyModalComponent {
    @Input() data: any;
    @Output() modalClosed = new EventEmitter();
    @Output() modalDismissed = new EventEmitter();
    @ViewChild('modal') modal: ModalComponent;

    nameError: boolean = false;

    ngAfterViewInit() {
        this.modal.open();
        console.log(this.data);
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

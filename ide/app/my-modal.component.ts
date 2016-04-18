import {Component, EventEmitter, Input, Output, ViewChild, AfterViewInit} from 'angular2/core';
import {MODAL_DIRECTIVES, ModalComponent } from 'ng2-bs3-modal/ng2-bs3-modal';

@Component({
    selector: 'my-modal',
    templateUrl: 'app/my-modal.component.html',
    directives: [MODAL_DIRECTIVES]
})
export class MyModalComponent {
    @Input() name: string;
    @Output() modalClosed = new EventEmitter();
    @ViewChild('modal') modal: ModalComponent;

    editor: string = 'tinymce';
    newName: string;

    ngAfterViewInit() {
        this.modal.open();
    }
    onModalClose(event: any) {
        this.modalClosed.emit(event);
    }
    changeEditor(event: string) {
        this.editor = event;
    }
}

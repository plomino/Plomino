// import {Component, EventEmitter, Input, Output, ViewChild, AfterViewInit} from '@angular/core';
// import {MODAL_DIRECTIVES, ModalComponent } from 'ng2-bs3-modal/ng2-bs3-modal';
// import {AlertComponent} from 'ng2-bootstrap/ng2-bootstrap';

// @Component({
//     selector: 'pmodal',
//     template: require('./modal.component.html'),
//     directives: [MODAL_DIRECTIVES, AlertComponent]
// })
// export class PlominoModalComponent {
//     @Input() data: any;
//     @Output() modalClosed = new EventEmitter();
//     @Output() modalDismissed = new EventEmitter();
//     @ViewChild('modal') modal: ModalComponent;

//     name: string;
//     action_type: string = "OPENFORM";

//     nameError: boolean = false;

//     ngAfterViewInit() {
//         this.modal.open();
//     }
//     onModalClose() {
//         if (this.name === undefined || !/\S/.test(this.name)) {
//             this.nameError = true;
//             this.modal.open();
//         }
//         else {
//             let element = this.data;
//             element.name = this.name;
//             if(element.type === 'PlominoAction')
//                 element.action_type = this.action_type;
//             this.modalClosed.emit(element);
//         }
//     }
//     onModalDismiss() {
//         this.modalDismissed.emit(true);
//     }
// }

import { Component, Input, Output, EventEmitter, ViewChild } from '@angular/core';
import { ElementService } from '../../services/element.service';

@Component({
    selector: 'my-agents-settings',
    template: require('./agents-settings.component.html'),
    styles: ['form {margin: 15px;} .help-block {font-style: italix;}'],
    providers: [ElementService]
})
export class AgentsSettingsComponent {
    @Input() id: string;
    data: any;
    @Output() isDirty = new EventEmitter();
    @Output() titleChanged = new EventEmitter();
    @ViewChild('form') form: any;

    constructor(private _elementService: ElementService) {}

    ngOnInit() {
        this.getElement();
    }

    ngAfterViewInit() {
        this.form.control.valueChanges
            .subscribe(() => this.isDirty.emit(true));
    }

    getElement() {
        this._elementService.getElement(this.id)
            .subscribe(
                data => {
                    this.data = data;
                    this.isDirty.emit(false);
                },
                err => console.log(err)
            );
    }

    onSubmit(id: string, title: string, description: string, run_as: string) {
        let element = { title, description, run_as };
        this._elementService.patchElement(id, JSON.stringify(element)).subscribe(
            () => {
                this.titleChanged.emit(this.data.title);
                this.isDirty.emit(false);
            },
            err => console.error(err)
        );
    }
}

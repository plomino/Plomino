import { Component, Input, Output, EventEmitter, ViewChild } from '@angular/core';
import { ElementService } from '../../services/element.service';

@Component({
    selector: 'my-actions-settings',
    template: require('./actions-settings.component.html'),
    styles: ['form {margin: 15px;} .help-block {font-style: italic;}'],
    providers: [ElementService]
})
export class ActionsSettingsComponent {
    @Input() id: string;
    data: any;
    @Output() isDirty = new EventEmitter();
    @Output() titleChanged = new EventEmitter();
    @ViewChild('form') form: any;

    constructor(private _elementService: ElementService) { }

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
                err => console.error(err)
            );
    }

    onSubmit(id: string, title: string, description: string, actionType:string, actionDisplay:string, inActionBar: boolean) {
        let element = {
            "title": title,
            "description": description,
            "action_type": actionType,
            "action_display": actionDisplay,
            "in_action_bar": inActionBar
        };
        this._elementService.patchElement(id, JSON.stringify(element)).subscribe(
            () => {
                this.titleChanged.emit(this.data.title);
                this.isDirty.emit(false);
            },
            err => console.error(err)
        );
    }
}

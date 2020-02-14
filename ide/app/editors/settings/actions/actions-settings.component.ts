import { Component, Input, Output, EventEmitter, ViewChild } from '@angular/core';
import { REACTIVE_FORM_DIRECTIVES } from '@angular/forms';
import { ElementService, LogService } from '../../../services';

@Component({
    selector: 'plomino-actions-settings',
    template: require('./actions-settings.component.html'),
    styles: ['form {margin: 15px;} .help-block {font-style: italic;}'],
    providers: [ElementService],
    directives: [ REACTIVE_FORM_DIRECTIVES ]
})
export class ActionsSettingsComponent {
    @Input() id: string;
    data: any;
    @Output() isDirty = new EventEmitter();
    @Output() titleChanged = new EventEmitter();
    @Output() elementDeleted = new EventEmitter();
    @ViewChild('form') form: any;

    constructor(
      private _elementService: ElementService,
      private log: LogService,
    ) { }

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
                (data: any) => {
                    this.data = data;
                    this.isDirty.emit(false);
                },
                (err: any) => console.error(err)
            );
      this.log.extra('actions-settings.component.ts getElement');
    }

    onSubmit(id: string, title: string, description: string, actionType: string, actionDisplay: string, inActionBar: boolean) {
        const element = {
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
            (err: any) => console.error(err)
        );
        this.log.extra('actions-settings.component.ts onSubmit');
    }

    deleteElement() {
        this._elementService.deleteElement(this.data["@id"]).subscribe(
            () => this.elementDeleted.emit(this.data["@id"]),
            (err: any) => console.error(err)
        );
        this.log.extra('actions-settings.component.ts deleteElement');
    }
}

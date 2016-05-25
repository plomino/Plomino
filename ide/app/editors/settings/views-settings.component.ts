import { Component, Input, Output, EventEmitter, ViewChild } from '@angular/core';
import { ElementService } from '../../services/element.service';

@Component({
    selector: 'my-views-settings',
    template: require('./views-settings.component.html'),
    styles: ['form {margin: 15px;} .help-block {font-style: italic;}'],
    providers: [ElementService]
})
export class ViewsSettingsComponent {
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

    onSubmit(id: string,
        title: string,
        description: string,
        hideDefaultActions: boolean,
        sortColumn: string,
        keyColumn: string,
        categorized: boolean,
        reverseSorting: boolean,
        staticRendering: boolean) {
            let element = {
                "title": title,
                "description": description,
                "hide_default_actions": hideDefaultActions,
                "sort_column": sortColumn,
                "key_column": keyColumn,
                "categorized": categorized,
                "reverse_sorting": reverseSorting,
                "static_rendering": staticRendering
        };
        this._elementService.patchElement(id, JSON.stringify(element));
        this.titleChanged.emit(this.data.title);
        this.isDirty.emit(false);
    }
}

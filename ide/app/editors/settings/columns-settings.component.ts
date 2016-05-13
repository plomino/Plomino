import { Component, Input, Output, EventEmitter } from 'angular2/core';
import { ElementService } from '../../services/element.service';

@Component({
    selector: 'my-columns-settings',
    templateUrl: 'app/editors/settings/columns-settings.component.html',
    styles: ['form {margin: 15px;} .help-block {font-style: italic;}'],
    providers: [ElementService]
})
export class ColumnsSettingsComponent {
    @Input() id: string;
    data: any;
    @Output() titleChanged = new EventEmitter();

    constructor(private _elementService: ElementService) { }

    ngOnInit() {
        this.getElement();
    }

    getElement() {
        this._elementService.getElement(this.id)
            .subscribe(
                data => { this.data = data },
                err => console.error(err)
            );
    }

    onSubmit(id: string, title: string, description: string, hiddenColumn: boolean) {
        let element = {
            "title": title,
            "description": description,
            "hidden_column": hiddenColumn
        };
        this._elementService.patchElement(id, JSON.stringify(element));
        this.titleChanged.emit(this.data.title);
    }
}
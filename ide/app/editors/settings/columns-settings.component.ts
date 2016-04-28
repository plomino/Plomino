import { Component, Input, Output, EventEmitter } from 'angular2/core';

@Component({
    selector: 'my-columns-settings',
    templateUrl: 'app/editors/settings/columns-settings.component.html',
    styles: ['form {margin: 15px;} .help-block {font-style: italic;}']
})
export class ColumnsSettingsComponent {
    @Input() title: string;
    @Output() titleChanged = new EventEmitter();

    onSubmit() {
        this.titleChanged.emit(this.title);
    }
}

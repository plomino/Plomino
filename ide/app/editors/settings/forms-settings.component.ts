import { Component, Input, Output, EventEmitter } from 'angular2/core';

@Component({
    selector: 'my-forms-settings',
    templateUrl: 'app/editors/settings/forms-settings.component.html',
    styles: ['form {margin: 15px;} .help-block {font-style: italic;}']
})
export class FormsSettingsComponent {
    @Input() title: string;
    @Output() titleChanged = new EventEmitter();

    onSubmit() {
        this.titleChanged.emit(this.title);
    }
}

import { Component, Input, Output, EventEmitter } from 'angular2/core';

@Component({
    selector: 'my-actions-settings',
    templateUrl: 'app/editors/settings/actions-settings.component.html',
    styles: ['form {margin: 15px;} .help-block {font-style: italic;}']
})
export class ActionsSettingsComponent {
    @Input() title: string;
    @Output() titleChanged = new EventEmitter();

    onSubmit() {
        this.titleChanged.emit(this.title);
    }
}

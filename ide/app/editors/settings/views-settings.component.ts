import { Component, Input, Output, EventEmitter } from 'angular2/core';

@Component({
    selector: 'my-views-settings',
    templateUrl: 'app/editors/settings/views-settings.component.html',
    styles: ['form {margin: 15px;} .help-block {font-style: italic;}']
})
export class ViewsSettingsComponent {
    @Input() title: string;
    @Output() titleChanged = new EventEmitter();

    onSubmit() {
        this.titleChanged.emit(this.title);
    }
}

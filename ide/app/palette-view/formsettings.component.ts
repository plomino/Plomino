import { Component, Input, Output, EventEmitter } from '@angular/core';

@Component({
    selector: 'plomino-palette-formsettings',
    template: require('./formsettings.component.html'),
    directives: [],
    providers: []
})

export class FormSettingsComponent {

    // This needs to handle both views and forms
    heading: string;

    ngOnInit() {
        // By default use Form for the heading
        // Change this depending on what we're looking at
        // Need to work out how to update the tab heading with this though
        this.heading = 'Form';
    }
}

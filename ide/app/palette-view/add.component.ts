import { Component, Input, Output, OnInit, EventEmitter } from '@angular/core';

@Component({
    selector: 'plomino-palette-add',
    template: require('./add.component.html'),
    styles: [require('./add.component.css')],
    directives: [],
    providers: []
})

export class AddComponent {

    addableComponents: Array<any> = [];

    ngOnInit() {
        // Set up the addable components
        this.addableComponents = [
            {title: 'Form', components: [
                {title: 'Field', icon: 'tasks', type: 'field', addable: false},
                {title: 'Hide When', icon: 'sunglasses', type: 'hidewhen', addable: false},
                {title: 'Action', icon: 'cog', type: 'action', addable: false},
                ]
            },
            {title: 'View', components: [
                {title: 'Column', icon: 'stats', type: 'column', addable: false},
                {title: 'Action', icon: 'cog', type: 'action', addable: false},
                ]
            },
            {title: 'DB', components: [
                {title: 'Form', icon: 'th-list', type: 'form', addable: true},
                {title: 'View', icon: 'list-alt', type: 'view', addable: true},
                ]
            }

        ];
    }

    // XXX: temp. For toggling state of Form/View buttons until hooked up to
    // event that handles currently selected item in main view
    toggle(type: string) {
        if (type == 'form') {
            for (let component of this.addableComponents[0]['components']) {
                component.addable = !component.addable;
            }
        } else if (type == 'view') {
            for (let component of this.addableComponents[1]['components']) {
                component.addable = !component.addable;
            }
        }
    }

    add(type: any) {
        // console.log(event.target.id);
        // XXX: Handle the adding of components

        if (type == 'form') {

        }

    }

    // When a Form or View is selected, adjust the addable state of the
    // relevant buttons

}

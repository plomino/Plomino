import { Component, Input, Output, OnInit, EventEmitter } from '@angular/core';

@Component({
    selector: 'plomino-palette-add',
    template: require('./add.component.html'),
    directives: [],
    providers: []
})

export class AddComponent {

    addableComponents: Array<any> = [];

    ngOnInit() {
        // Set up the addable components
        this.addableComponents = [
            {title: 'DB', components: [
                {title: 'Form', icon: 'th-list', type: 'form', addable: true},
                {title: 'View', icon: 'list-alt', type: 'view', addable: true},
                ]
            },
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
            }
        ];
    }

    add(type: any) {
        // console.log(event.target.id);
        // XXX: Handle the adding of components

        // XXX: Remove this later
        // This isn't real. Controlling the state of the buttons needs to be done
        // By listening to the event that handles the currently selected item 
        if (type == 'form') {
            for (let component of this.addableComponents[1]['components']) {
                component.addable = true;
            }
            for (let component of this.addableComponents[2]['components']) {
                component.addable = false;
            }
        } else if (type == 'view') {
            for (let component of this.addableComponents[2]['components']) {
                component.addable = true;
            }
            for (let component of this.addableComponents[1]['components']) {
                component.addable = false;
            }
        }
    }

    // When a Form or View is selected, adjust the addable state of the
    // relevant buttons

}

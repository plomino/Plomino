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

    // When a Form or View is selected, adjust the addable state of the
    // relevant buttons. How do we do this? Do we need a service that stores
    // the currently selected object?

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
        // XXX: Handle the adding of components. This needs to take into account
        // the currently selected object. i.e. if we're on a Form, the
        // field/action/hidewhen should be created then added to the form.
        // If we're on a view, the action/column should be added to the view.
        // The tree should be updated and, if it's a Form, the object should
        // be added to the layout. If it's a Drag and Drop (not implemented) yet,
        // The new field etc. should be added at the cursor. Otherwise to the
        // end of the form layout.
        switch (type) {
            case 'form':
                // Do stuff for the form
                console.log('Add form');
                break;
            case 'view':
                // Do
                console.log('Add view');
                break;
            default:
                console.log(type + ' not handled yet')
        }
    }
}

import { Component, Input, Output, OnInit, EventEmitter } from '@angular/core';
import { ElementService }               from '../services/element.service';

@Component({
    selector: 'plomino-palette-add',
    template: require('./add.component.html'),
    styles: [require('./add.component.css')],
    directives: [],
    providers: [ElementService]
})

export class AddComponent {
    addableComponents: Array<any> = [];

    constructor(private _elementService: ElementService) { }

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

        // XXX: this is handled in the modal popup via the ElementService/TreeComponent
        // by calling postElement. We effectively need to do the exact same thing,
        // but bypass the modal and just set a default title/id for the object

        // XXX: For updating the tree, can that be handled via the ElementService?
        // If the POST that creates the new object happens over there, can there be
        // something that the main app/tree subscribes to so it refreshes automatically?
        switch (type) {
            case 'form':
                let formElement: any = {
                    "@type": "PlominoForm",
                    "title": "New Form"
                };
                this._elementService.postElement('../../', formElement).subscribe();
                console.log('Added new form');
                // Get the ID of the new element back in the response.
                // Update the Tree
                // Open the form layout in the editor
                break;
            case 'view':
                let viewElement: any = {
                    "@type": "PlominoView",
                    "title": "New View"
                };
                this._elementService.postElement('../../', viewElement).subscribe();
                console.log('Added new view')
                // Get the ID of the new element back in the response.
                // Update the Tree
                // Open the View in the editor
                break;
            case 'field':
                // Add the field, then insert it into the form layout. Update the tree etc.
                console.log('Adding a field');
                break;
            case 'hidewhen':
                // Add the hidewhen, then insert it into the form layout. Update the tree etc.
                console.log('Adding a hidewhen');
                break;
            case 'action':
                // Add the action, then insert it into the form. Update the tree etc.
                // If it's a view it doesn't have to be insetred into a layout
                console.log('Adding an action');
                break;
            case 'column':
                // Add the action to the view. Update the tree etc.
                console.log('Adding a column');
                break;
            default:
                console.log(type + ' not handled yet')
        }
    }
}

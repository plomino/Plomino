import { 
    Component, 
    Input, 
    Output, 
    OnInit, 
    EventEmitter,
    ChangeDetectorRef 
} from '@angular/core';

import { 
    ElementService,
    TreeService,
    TabsService,
    FieldsService
} from '../services';

@Component({
    selector: 'plomino-palette-add',
    template: require('./add.component.html'),
    styles: [require('./add.component.css')],
    directives: [],
    providers: [ElementService]
})

export class AddComponent {
    activeTab: any;
    addableComponents: Array<any> = [];

    constructor(private elementService: ElementService,
                private treeService: TreeService,
                private tabsService: TabsService,
                private fieldsService: FieldsService,
                private changeDetector: ChangeDetectorRef) { 

    }

    ngOnInit() {
        // Set up the addable components
        this.addableComponents = [
            {
                title: 'Form', 
                components: [
                    {title: 'Field', icon: 'tasks', type: 'field', addable: true},
                    {title: 'Hide When', icon: 'sunglasses', type: 'hidewhen', addable: true},
                    {title: 'Action', icon: 'cog', type: 'action', addable: true},
                ]
            },
            {
                title: 'View', 
                components: [
                    {title: 'Column', icon: 'stats', type: 'column', addable: true},
                    {title: 'Action', icon: 'cog', type: 'action', addable: true},
                ]
            },
            {
                title: 'DB', 
                components: [
                    {title: 'Form', icon: 'th-list', type: 'form', addable: true},
                    {title: 'View', icon: 'list-alt', type: 'view', addable: true},
                ]
            }

        ];

        this.tabsService.getActiveTab()
            .subscribe((tab) => {
                this.activeTab = tab; 
                this.changeDetector.detectChanges();
            });
    }

    // When a Form or View is selected, adjust the addable state of the
    // relevant buttons. How do we do this? Do we need a service that stores
    // the currently selected object?

    // XXX: temp. For toggling state of Form/View buttons until hooked up to
    // event that handles currently selected item in main view
    // toggle(type: string) {
    //     if (type == 'form') {
    //         for (let component of this.addableComponents[0]['components']) {
    //             component.addable = !component.addable;
    //         }
    //     } else if (type == 'view') {
    //         for (let component of this.addableComponents[1]['components']) {
    //             component.addable = !component.addable;
    //         }
    //     }
    // }

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
        let randomId: number = Math.round((Math.random() * 999 - 0));
        let field: any;
        switch (type) {
            case 'form':
                let formElement: any = {
                    "@type": "PlominoForm",
                    "title": "New Form"
                };
                this.elementService.postElement('../../', formElement).subscribe((respose) => {
                    this.treeService.updateTree();
                    console.log('Added new form');
                });
                // Get the ID of the new element back in the response.
                // Update the Tree
                // Open the form layout in the editor
                break;
            case 'view':
                let viewElement: any = {
                    "@type": "PlominoView",
                    "title": "New View"
                };
                this.elementService.postElement('../../', viewElement).subscribe(() => {
                    this.treeService.updateTree();
                    console.log('Added new view')
                });
                // Get the ID of the new element back in the response.
                // Update the Tree
                // Open the View in the editor
                break;
            case 'field':
                // Add the field, then insert it into the form layout. Update the tree etc.
                console.log('Adding a field');
                field = {
                    title: 'defaultField',
                    name: 'defaultField',
                    '@type': 'PlominoField',
                    url: `${this.activeTab.url}/default-field-${randomId}`
                }
                this.elementService.postElement(this.activeTab.url, field)
                    .subscribe(() => {
                        this.fieldsService.insertField(field);
                        this.treeService.updateTree();
                    })
                break;
            case 'hidewhen':
                // Add the hidewhen, then insert it into the form layout. Update the tree etc.
                console.log(`Adding a hidewhen`);
                field = {
                    title: 'defaultHidewhen',
                    name: 'defaultHidewhen',
                    '@type': 'PlominoHidewhen',
                    url: `${this.activeTab.url}/default-hidewhen-${randomId}`
                }
                this.elementService.postElement(this.activeTab.url, field)
                    .subscribe(() => {
                        this.fieldsService.insertField(field);
                        this.treeService.updateTree();
                    })
                break;
            case 'action':
                // Add the action, then insert it into the form. Update the tree etc.
                // If it's a view it doesn't have to be insetred into a layout
                console.log('Adding an action');
                field = {
                    title: 'defaultAction',
                    name: 'defaultAction',
                    action_type: 'OPENFORM',
                    '@type': 'PlominoAction',
                    url: `${this.activeTab.url}/default-action-${randomId}`
                }
                this.elementService.postElement(this.activeTab.url, field)
                    .subscribe(() => {
                        this.fieldsService.insertField(field);
                        this.treeService.updateTree();
                    })
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

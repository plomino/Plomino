import { 
    Component, 
    Input, 
    Output, 
    OnInit, 
    EventEmitter,
    ChangeDetectorRef,
    ChangeDetectionStrategy
} from '@angular/core';

import { DND_DIRECTIVES } from 'ng2-dnd/ng2-dnd';

import { 
    ElementService,
    TreeService,
    TabsService,
    FieldsService,
    DraggingService,
    TemplatesService,
    WidgetService
} from '../../services';

@Component({
    selector: 'plomino-palette-add',
    template: require('./add.component.html'),
    styles: [require('./add.component.css')],
    directives: [DND_DIRECTIVES],
    providers: [ElementService],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class AddComponent {
    activeTab: any;
    templates: any[] = [];
    addableComponents: Array<any> = [];

    constructor(private elementService: ElementService,
                private treeService: TreeService,
                private tabsService: TabsService,
                private fieldsService: FieldsService,
                private draggingService: DraggingService,
                private changeDetector: ChangeDetectorRef,
                private templatesService: TemplatesService,
                private widgetService: WidgetService) { 

    }

    ngOnInit() {
        // Set up the addable components
        this.addableComponents = [
            {
                title: 'Form', 
                components: [
                    { title: 'Label', icon: '', type: 'PlominoLabel', addable: true },
                    { title: 'Field', icon: 'tasks', type: 'PlominoField', addable: true },
                    { title: 'Hide When', icon: 'sunglasses', type: 'PlominoHidewhen', addable: true },
                    { title: 'Action', icon: 'cog', type: 'PlominoAction', addable: true },
                ],
                hidden: (tab: any) => {
                    if (!tab) return true;
                    return tab.type !== 'PlominoForm';
                }
            },
            {
                title: 'View', 
                components: [
                    { title: 'Column', icon: 'stats', type: 'column', addable: true },
                    { title: 'Action', icon: 'cog', type: 'action', addable: true },
                ],
                hidden: (tab: any) => {
                    if (!tab) return true;
                    return tab.type === 'PlominoForm';
                }
            },
            {
                title: 'DB', 
                components: [
                    { title: 'Form', icon: 'th-list', type: 'PlominoForm', addable: true },
                    { title: 'View', icon: 'list-alt', type: 'PlominoView', addable: true },
                ],
                hidden: () => {
                    return false;
                }
            }

        ];

        this.tabsService.getActiveTab()
            .subscribe((tab) => {
                this.activeTab = tab;
                if (tab) {
                    this.templatesService.getTemplates(tab.url).subscribe((templates: any[]) => {
                        this.templates = templates;
                        this.changeDetector.markForCheck();
                    });
                } else {
                    this.changeDetector.markForCheck();
                }
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
            case 'PlominoForm':
                let formElement: any = {
                    '@type': 'PlominoForm',
                    'title': 'New Form'
                };
                this.elementService.postElement('../../', formElement).subscribe((response) => {
                    this.treeService.updateTree().then(() => {
                        this.tabsService.openTab({
                            editor: 'layout',
                            label: response.title,
                            url: response['@id'] + response.id,
                            path: [{
                                name: response.title,
                                type: 'Forms'
                            }]
                        });
                    });
                });
                break;
            case 'PlominoView':
                let viewElement: any = {
                    '@type': 'PlominoView',
                    'title': 'New View'
                };
                this.elementService.postElement('../../', viewElement).subscribe((response) => {
                    this.treeService.updateTree().then(() => {
                        this.tabsService.openTab({
                            editor: 'code',
                            label: response.title,
                            url: response['@id'] + response.id,
                            path: [{
                                name: response.title,
                                type: 'Views'
                            }]
                        });
                    });
                    console.log('Added new view')
                });
                // Get the ID of the new element back in the response.
                // Update the Tree
                // Open the View in the editor
                break;
            case 'PlominoLabel':
                let field: any = {
                    '@type': 'PlominoLabel',
                    title: 'defaultLabel'
                };
                this.elementService.postElement(this.activeTab.url, field)
                .subscribe((response) => {
                    let extendedField = Object.assign({}, field, {
                        name: `${this.activeTab.url}/${response.created}`
                    });

                    this.treeService.updateTree()
                    .then(() => {
                        this.fieldsService.insertField(extendedField);
                    });
                });
                break;
            case 'PlominoField':
                field = {
                    title: 'defaultField',
                    '@type': 'PlominoField'
                }
                this.elementService.postElement(this.activeTab.url, field)
                    .subscribe((response) => {
                        let extendedField = Object.assign({}, field, {
                            name: `${this.activeTab.url}/${response.created}`
                        });

                        this.treeService.updateTree()
                            .then(() => {
                                this.fieldsService.insertField(extendedField);
                            });
                    })
                break;
            case 'PlominoHidewhen':
                field = {
                    title: 'defaultHidewhen',
                    '@type': 'PlominoHidewhen',
                }
                this.elementService.postElement(this.activeTab.url, field)
                    .subscribe((response) => {
                        let extendedField = Object.assign({}, field, {
                            name: response['@id']
                        });

                        this.treeService.updateTree()
                            .then(() => {
                                this.fieldsService.insertField(extendedField);
                            });
                    })
                break;
            case 'PlominoAction':
                field = {
                    title: 'defaultAction',
                    action_type: 'OPENFORM',
                    '@type': 'PlominoAction'
                }
                this.elementService.postElement(this.activeTab.url, field)
                    .subscribe((response) => {
                        let extendedField = Object.assign({}, field, {
                            name: response['@id']
                        });
                        this.treeService.updateTree()
                            .then(() => {
                                this.fieldsService.insertField(extendedField);
                            });
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


    addTemplate(templateId: string) {
        this.templatesService.addTemplate(this.activeTab.url, templateId)
            .subscribe((response: any) => {
                this.templatesService.insertTemplate(Object.assign({}, response, { 
                    parent: this.activeTab.url,
                    group: this.widgetService.getLayout(response) 
                }));
            });
    }

    // Refactor this code, put switch into separated fn
    startDrag(type: any): void {
        let data: any;
        let draggingData: any = {};
        switch(type) {
            case 'PlominoForm':
                data = {
                    '@type': 'PlominoForm'
                };
                break;
            case 'PlominoView':
                data = {
                    '@type': 'PlominoView'
                };
                break;
            case 'PlominoLabel':
                data = {
                  '@type': 'PlominoLabel'  
                };
                break;
            case 'PlominoField':
                data = {
                    '@type': 'PlominoField'
                };
                break;
            case 'PlominoHidewhen':
                data = {
                    '@type': 'PlominoHidewhen'
                }
                break;
            case 'PlominoAction':
                data = {
                    '@type': 'PlominoAction'
                };
                break;
            default: return;
        }
        

        /* @Resolved & @Resolver are needed,
         * because we have 2 types of drag data for now
         * 1 type is drag data from tree, which is already
         * populated with server data, and drag data from 
         * palette, which needs to be populated!
         * @Resolver will be called on drop event in tinymce.component
         */
        if (type === 'PlominoForm' || type === 'PlominoView') {
            Object.assign(draggingData, data, {
                resolved: false
            });
        } else {
            Object.assign(draggingData, data, {
                parent: this.activeTab.url,
                resolved: false
            });
        }

        draggingData.resolver = (data: any) => {
            this.add(data['@type']);
        }

        this.draggingService.setDragging(draggingData);
    }

    endDrag(): void {
        this.draggingService.setDragging(false);
    }
}

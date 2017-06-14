import { PlominoDBService } from './../../services/db.service';
import { Subscription, Observable, Subject } from 'rxjs/Rx';
import { PlominoActiveEditorService } from './../../services/active-editor.service';
import { PlominoViewsAPIService } from './../../editors/view-editor/views-api.service';
import { PlominoBlockPreloaderComponent } from './../../utility/block-preloader';
import {
  LabelsRegistryService
} from './../../editors/tiny-mce/services/labels-registry.service';
import { 
    Component, 
    Input, 
    Output, 
    OnInit, 
    AfterViewInit,
    EventEmitter,
    ChangeDetectorRef,
    ElementRef,
    ChangeDetectionStrategy
} from '@angular/core';

import { DND_DIRECTIVES } from 'ng2-dnd';

import { 
    ElementService,
    TreeService,
    TabsService,
    FieldsService,
    LogService,
    DraggingService,
    TemplatesService,
    WidgetService
} from '../../services';

interface TemplateClickEvent {
  eventData: MouseEvent;
  target: any;
  templateId: string;
}

@Component({
    selector: 'plomino-palette-add',
    template: require('./add.component.html'),
    styles: [require('./add.component.css')],
    directives: [DND_DIRECTIVES, PlominoBlockPreloaderComponent],
    providers: [ElementService, PlominoViewsAPIService],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class AddComponent implements OnInit, AfterViewInit {
    activeTab: PlominoTab;
    templates: PlominoFormGroupTemplate[] = [];
    addableComponents: Array<any> = [];
    mouseDownTemplateId: string;
    mouseDownTime: number;

    private tClickSubject: Subject<TemplateClickEvent> = new Subject<TemplateClickEvent>();
    public tClickFlow$: Observable<TemplateClickEvent> = this.tClickSubject.asObservable();
    private aClickSubject: Subject<string> = new Subject<string>();
    public aClickFlow$: Observable<string> = this.aClickSubject.asObservable();

    /**
     * display block preloader
     */
    loading: boolean = false;

    constructor(private elementService: ElementService,
                private treeService: TreeService,
                private tabsService: TabsService,
                private log: LogService,
                private dbService: PlominoDBService,
                private viewsAPIService: PlominoViewsAPIService,
                private labelsRegistry: LabelsRegistryService,
                private fieldsService: FieldsService,
                private draggingService: DraggingService,
                private elementRef: ElementRef,
                private activeEditorService: PlominoActiveEditorService,
                private changeDetector: ChangeDetectorRef,
                private templatesService: TemplatesService,
                private widgetService: WidgetService) { 
      this.tClickFlow$.debounceTime(200).subscribe((t: TemplateClickEvent) => {
        this.addTemplate(t.eventData, t.target, t.templateId);
      });
      this.aClickFlow$.debounceTime(200).subscribe((x: string) => {
        this.add(x, true);
      });
    }

    ngAfterViewInit() {
      // const isFF = 'MozAppearance' in document.documentElement.style;
    }

    ngOnInit() {
        // Set up the addable components
        this.addableComponents = [
            {
                title: 'Form', 
                components: [
                    { title: 'Label', icon: '', type: 'PlominoLabel', addable: true },
                    { title: 'Field', icon: 'tasks', type: 'PlominoField', addable: true },
                    { title: 'Pagebreak', icon: 'tasks', type: 'PlominoPagebreak', addable: true },
                    { title: 'Hide When', icon: 'sunglasses', type: 'PlominoHidewhen', addable: true },
                    { title: 'Action', icon: 'cog', type: 'PlominoAction', addable: true },
                    { title: 'Subform', icon: 'cog', type: 'PlominoSubform', addable: true },
                ],
                hidden: (tab: any) => {
                    if (!tab) return true;
                    return tab.type !== 'PlominoForm';
                }
            },
            {
                title: 'View', 
                components: [
                    { 
                      title: 'Column', 
                      icon: 'stats', 
                      type: 'column', 
                      addable: true, 
                      dragData: { type: 'column' } 
                    },
                    { 
                      title: 'Action', 
                      icon: 'cog', 
                      type: 'action', 
                      addable: true, 
                      dragData: { type: 'action' } 
                    },
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

          this.log.info('tab', tab);
          this.log.extra('add.component.ts this.tabsService.getActiveTab()');
          
          this.templates = [];
          this.loading = true;
          this.activeTab = tab;
          this.changeDetector.markForCheck();
          this.changeDetector.detectChanges();

          if (tab && tab.type === 'PlominoView') {
            this.loading = false;
            this.changeDetector.markForCheck();
            this.changeDetector.detectChanges();
          }
          else if (tab && tab.url) {
            this.log.info('tab && tab.url', tab, tab.url);
            this.templatesService.getTemplates(tab.url)
            .subscribe((templates: PlominoFormGroupTemplate[]) => {
              componentHandler.upgradeDom();
              this.templates = templates.map((template) => {

                this.templatesService.buildTemplate(tab.url, template);

                return Object.assign({}, template, {
                  url: `${tab.url.slice(0, tab.url.lastIndexOf('/'))}/${template.id}`,
                  hidewhen: (tab: any) => {
                    if (!tab) return true;
                    return tab.type !== 'PlominoForm';        
                  }
                })
              });

              $('#PlominoHidewhen, #PlominoAction, ' +
                '#PlominoField, #PlominoLabel, #PlominoPagebreak, #PlominoSubform')
              .each((i, element) => {
                const $element = $(element);
                const $id = $element.attr('id');

                $element
                .removeAttr('dnd-draggable')
                .removeAttr('draggable')
                .unbind().bind('mousedown', ($event) => {
                  this.simulateDrag(<MouseEvent>$event.originalEvent, $id);
                });
              });

              this.draggingService.subformDragEvent$
              .subscribe((mouseEvent) => {
                $('#drag-data-cursor').remove();
                this.simulateDrag(mouseEvent, 'PlominoSubform');
              });

              this.loading = false;
              this.changeDetector.markForCheck();
              this.changeDetector.detectChanges();
            });
          } else {
            this.loading = false;
            this.changeDetector.markForCheck();
            this.changeDetector.detectChanges();
          }
        });
    }

    add(type: string, target?: HTMLElement|true, treeSubform?: boolean) {
      const clickTime = (new Date).getTime();

      //todo: detect click
      // if (clickTime > (this.mouseDownTime + 500)) {
      //   return false;
      // }

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
      let field: InsertFieldEvent;
      switch (type) {
          case 'PlominoForm':
              let formElement: InsertFieldEvent = {
                  '@type': 'PlominoForm',
                  'title': 'New Form'
              };
              this.log.startTimer('create_new_form_hold');
              this.elementService.postElement(this.getDBOptionsLink(''), formElement)
              .subscribe((response: AddFieldResponse) => {
                this.treeService.updateTree().then(() => {
                  this.log.info('this.tabsService.openTab #a001');
                  // this.treeService.latestId++;
                  this.tabsService.openTab({
                    formUniqueId: undefined,
                    editor: 'layout',
                    label: response.title,
                    url: response.parent['@id'] + '/' + response.id,
                    path: [{
                        name: response.title,
                        type: 'Forms'
                    }]
                  });
                  this.log.stopTimer('create_new_form_hold');
                });
              });
              break;
          case 'PlominoView':
            this.log.startTimer('create_new_view_hold');
              let viewElement: InsertFieldEvent = {
                '@type': 'PlominoView',
                'title': 'New View'
              };
              this.elementService.postElement(this.getDBOptionsLink(''), viewElement)
              .subscribe((response: AddFieldResponse) => {
                this.log.info('this.tabsService.openTab #a002');
                
                this.treeService.updateTree().then(() => {
                  this.tabsService.openTab({
                    editor: 'view',
                    label: response.title,
                    url: response.parent['@id'] + '/' + response.id,
                    path: [{
                        name: response.title,
                        type: 'Views'
                    }]
                  });

                  this.log.stopTimer('create_new_view_hold');
                });
              });
              // Get the ID of the new element back in the response.
              // Update the Tree
              // Open the View in the editor
              break;
          case 'PlominoLabel':
            this.log.startTimer('create_new_label_hold');
              let field: InsertFieldEvent = {
                '@type': 'PlominoLabel',
                title: 'defaultLabel',
                name: `${this.activeTab.url}/defaultLabel`,
                target
              };
              this.fieldsService.insertField(field);
              this.log.stopTimer('create_new_label_hold');
              break;
          case 'PlominoField':
            this.log.startTimer('create_new_field_hold');
              field = {
                  title: 'defaultField',
                  '@type': 'PlominoField',
                  target
              }
              this.elementService.postElement(this.activeTab.url, field)
              .subscribe((response: AddFieldResponse) => {
                let extendedField: InsertFieldEvent = Object.assign({}, field, {
                  name: `${this.activeTab.url}/${response.created}`
                });

                this.labelsRegistry.update(
                  `${ this.activeTab.url }/${ response.created }`, field.title, 'title'
                );

                this.fieldsService.insertField(extendedField);
                this.log.stopTimer('create_new_field_hold');

                this.treeService.updateTree().then(() => {});
              })
              break;
          case 'PlominoPagebreak':
              field = {
                name: `${this.activeTab.url}/defaultPagebreak`,
                title: 'defaultPagebreak',
                '@type': 'PlominoPagebreak',
                target
              }
              this.fieldsService.insertField(field);
              break;
          case 'PlominoSubform':
            /**
             * should be similar as on subform settings
             */
            this.mouseDownTemplateId;
            this.draggingService.currentDraggingTemplateCode;

            const getSubformLayout$ = (this.mouseDownTemplateId) 
              ? this.widgetService.getGroupLayout(
                  `${ this.dbService.getDBLink() }/${ 
                    this.activeEditorService.getActive().id }`,
                  {
                    id: this.mouseDownTemplateId,
                    layout: $(this.draggingService.currentDraggingTemplateCode).html()
                  }
                )
              : Observable.of('');

            getSubformLayout$
            .subscribe((result: string) => {
              let subformHTML: string = null;

              if (result) {
                const $result = $(result);
                $result.find('input,textarea,button')
                  .removeAttr('name')
                  .removeAttr('id');
                $result.find('span')
                  .removeAttr('data-plominoid')
                  .removeAttr('data-mce-resize');
                $result.removeAttr('data-groupid');
                $result.find('div')
                  .removeAttr('data-groupid');
                subformHTML = $($result.html()).html();
              }

              field = {
                name: `${ this.activeTab.url }/defaultSubform`,
                title: this.mouseDownTemplateId || 'defaultSubform',
                '@type': 'PlominoSubform',
                subformHTML,
                target
              }

              this.fieldsService.insertField(field);
            });
            break;
          case 'PlominoHidewhen':
              field = {
                  title: 'defaultHidewhen',
                  '@type': 'PlominoHidewhen',
              }
              /**
               * here the code does HTTP POST query to create a new field/etc
               * and returns its widget code
               */
              this.elementService.postElement(this.activeTab.url, field)
              .subscribe((response: AddFieldResponse) => {
                let extendedField = Object.assign({}, field, {
                  name: response['@id'],
                  target
                });

                this.log.info('extendedField', extendedField);
                this.fieldsService.insertField(extendedField);

                this.treeService.updateTree().then(() => {});
              });
              break;
          case 'PlominoAction':
              field = {
                  title: 'defaultAction',
                  action_type: 'OPENFORM',
                  '@type': 'PlominoAction',
                  target
              }
              this.elementService.postElement(this.activeTab.url, field)
              .subscribe((response: AddFieldResponse) => {
                let extendedField = Object.assign({}, field, {
                    name: response['@id']
                });
                this.fieldsService.insertField(extendedField);
                this.treeService.updateTree().then(() => {});
                })
              break;
          case 'column':
              this.fieldsService.viewColumnInserted.next(this.activeTab.url);
              break;
          case 'action':
              field = {
                  title: 'default-action',
                  action_type: 'OPENFORM',
                  '@type': 'PlominoAction',
              }
              this.viewsAPIService.addNewAction(this.activeTab.url)
              .subscribe((response: AddFieldResponse) => {
                this.fieldsService.viewActionInserted.next(this.activeTab.url);
                let extendedField = Object.assign({}, field, {
                    name: response['@id']
                });
                 
                const url = this.activeTab.url;
                const newAction = `<input class="context mdl-button
                  mdl-js-button mdl-button--primary mdl-button--raised"
                  type="button" id="${ response.id }" name="${ response.id }"
                  value="${ response.title }">`;
                $(`[data-url="${ url }"] .actionButtons`)
                  .append(newAction);

                componentHandler.upgradeDom();
                $(`[data-url="${ url }"] .actionButtons #${ response.id }`).click();

                this.fieldsService.insertField(extendedField);
                this.treeService.updateTree().then(() => {});
              })
              break;
          default:
              console.log(type + ' not handled yet')
      }
    }

    runAddTemplate(eventData: MouseEvent, target: any, templateId: string) {
      this.activeEditorService.turnActiveEditorToLoadingState();
      this.tClickSubject.next({eventData, target, templateId});
    }

    runAdd(comp: string) {
      this.activeEditorService.turnActiveEditorToLoadingState();
      this.aClickSubject.next(comp);
    }

    addTemplate(eventData: MouseEvent, target: any, templateId: string) {

      this.log.startTimer('create_new_template_hold');

      const a = $(eventData.currentTarget).data('templateId');
      const b = templateId;
      const c = this.mouseDownTemplateId;
      const clickTime = (new Date).getTime();
      
      // 1. form insert: undefined, template-text, template-text
      // 2. form drag and return to blank: no
      // 3. form drag and return to keyboard: template_radio template_radio template_text
      // 4. click: template_long_text template_long_text template_long_text

      if (clickTime > (this.mouseDownTime + 500) && 
        (typeof a !== 'undefined' && (c !== b))) {
        return false;
      }
      
      this.templatesService.addTemplate(this.activeTab.url, templateId)
        .subscribe((response: PlominoFormGroupTemplate) => {
          response = this.templatesService.fixCustomTemplate(response);
          this.widgetService.getGroupLayout(this.activeTab.url, response)
          .subscribe((layout: string) => {
            layout = this.templatesService.fixBuildedTemplate(layout);
  
            this.templatesService.insertTemplate(
              <InsertTemplateEvent> Object.assign({}, response, {
              parent: this.activeTab.url,
              target: target,
              group: layout
            }));
  
            this.log.stopTimer('create_new_template_hold');
            this.activeEditorService.turnActiveEditorToLoadingState(false);
            this.treeService.updateTree().then(() => {});
          });    
        });
    }

    simulateDrag(eventData: MouseEvent, type: any, template?: PlominoFormGroupTemplate) {
      this.mouseDownTemplateId = template ? template.id : null;
      this.mouseDownTime = (new Date).getTime();
      this.startDrag(eventData, type, template);
    }

    // Refactor this code, put switch into separated fn
    startDrag(
      eventData: MouseEvent, type: any, 
      template?: PlominoFormGroupTemplate
    ) {
        const draggingData: PlominoDraggingData = {
          '@type': type === 'template' ? 'PlominoTemplate' : type,
          resolver: () => {},
          resolved: false,
          eventData: eventData
        };

        /* @Resolved & @Resolver are needed,
         * because we have 2 types of drag data for now
         * 1 type is drag data from tree, which is already
         * populated with server data, and drag data from 
         * palette, which needs to be populated!
         * @Resolver will be called on drop event in tinymce.component
         */
        if (type !== 'PlominoForm' && type !== 'PlominoView') {
            draggingData.parent = this.activeTab.url;
        }

        let treeSubform = false;
        if (!template && eventData.target) {
          const $target = (<HTMLElement> eventData.target).classList
            .contains('tree-node--name') 
              ? $(eventData.target) 
              : $(eventData.target).find('.tree-node--name');
          const text = $target.text().trim();
          if (text) {
            this.mouseDownTemplateId = text;
            treeSubform = true;
          }
        }

        if (type !== 'template') {
            draggingData.resolver = (target, data = {'@type': ''}) => {
              this.add(data['@type'], target, treeSubform);
            }
        } else {
            draggingData.templateId = template.id;
            draggingData.template = template;
            draggingData.resolver = (target) => {
              this.addTemplate(eventData, target, template.id);
            }
        }

        this.draggingService.currentDraggingData = draggingData;
        
        this.draggingService.setDragging(draggingData);

        if (draggingData['@type']) {
          this.draggingService.followDNDType(draggingData['@type']);
        }
    }

    endDrag(): void {
        this.draggingService.setDragging(false);
    }

    private getDBOptionsLink(link: string) {
      return `${ 
        window.location.pathname
        .replace('++resource++Products.CMFPlomino/ide/', '')
        .replace('/index.html', '')
      }/${ link }`;
    }
}

import { PlominoWorkflowChangesNotifyService } from './editors/workflow/workflow.changes.notify.service';
import { LabelsRegistryService } from './editors/tiny-mce/services/labels-registry.service';
import { 
  TinyMCEFormContentManagerService
} from './editors/tiny-mce/content-manager/content-manager.service';

// Core
import { 
  Component, 
  ViewChild,
  NgZone, 
  OnInit,
  AfterViewInit,
  ChangeDetectorRef,
  trigger,
  animate,
  state,
  style,
  transition
} from '@angular/core';

// External Components
import { TAB_DIRECTIVES } from 'ng2-bootstrap/ng2-bootstrap';
import { DND_DIRECTIVES } from 'ng2-dnd';
// import {DndModule} from 'ng2-dnd';

// Components
import { TreeComponent } from './tree-view';
import { PaletteComponent, PlominoWorkflowNodeSettingsComponent } from './palette-view';

import {
  TinyMCEComponent,
  ACEEditorComponent,
  FormsSettingsComponent,
  FieldsSettingsComponent,
  ActionsSettingsComponent,
  HideWhenSettingsComponent,
  ViewsSettingsComponent,
  ColumnsSettingsComponent,
  AgentsSettingsComponent,
  PlominoWorkflowComponent,
  PlominoViewEditorComponent
} from './editors';

// Services
import {
  LogService,
  PlominoHTTPAPIService,
  TreeService,
  ElementService,
  ObjService,
  TabsService,
  FieldsService,
  DraggingService,
  TemplatesService,
  PlominoElementAdapterService,
  WidgetService,
  FormsService,
  PlominoFormsListService,
  PlominoApplicationLoaderService,
  URLManagerService,
  PlominoActiveEditorService,
} from './services';

// Pipes 
import { ExtractNamePipe } from './pipes';

// Interfaces
import { IField } from './interfaces';

// Utility Components
import {
  PlominoModalComponent, ResizeDividerComponent, PlominoBlockPreloaderComponent
} from './utility';
import { LoadingComponent } from "./editors/loading/loading.component";

@Component({
  selector: 'plomino-app',
  template: require('./app.component.html'),
  styles: [require('./app.component.css')],
  directives: [
    TreeComponent,
    PaletteComponent,
    TAB_DIRECTIVES,
    DND_DIRECTIVES,
    TinyMCEComponent,
    ACEEditorComponent,
    PlominoModalComponent,
    FormsSettingsComponent,
    FieldsSettingsComponent,
    ActionsSettingsComponent,
    HideWhenSettingsComponent,
    ViewsSettingsComponent,
    ColumnsSettingsComponent,
    AgentsSettingsComponent,
    LoadingComponent,
    ResizeDividerComponent,
    PlominoBlockPreloaderComponent,
    PlominoWorkflowComponent,
    PlominoWorkflowNodeSettingsComponent,
    PlominoViewEditorComponent,
  ],
  providers: [
    LogService,
    PlominoHTTPAPIService,
    TreeService, 
    ElementService, 
    ObjService, 
    TabsService, 
    FieldsService,
    DraggingService,
    TemplatesService,
    WidgetService,
    FormsService,
    PlominoFormsListService,
    TinyMCEFormContentManagerService,
    PlominoElementAdapterService,
    LabelsRegistryService,
    PlominoApplicationLoaderService,
    PlominoWorkflowChangesNotifyService,
    URLManagerService,
    PlominoActiveEditorService,
  ],
  pipes: [ExtractNamePipe],
  animations: [
    trigger('dropZoneState', [
      state('*', style({
        opacity: 1
      })),
      transition('void => *', [
        style({
            opacity: 0
        }),
        animate(300)
      ]),
      transition('* => void', animate(300, style({
        opacity: 0
      })))
    ])
  ]
})
export class AppComponent implements OnInit, AfterViewInit {

  data: any;
  selectedField: IField;
  selected: any;
  tabs: Array<any> = [];

  isModalOpen: boolean = false;
  modalData: any;

  isDragging: boolean = false;
  dragData: any = null;

  aceNumber: number = 0;

  DIRECTION_DOWN = 'down';
  DIRECTION_UP = 'up';
  DIRECTION_LEFT = 'left';
  DIRECTION_RIGHT = 'right';
  wrapperWidth: number = 464;
  addDialog: HTMLDialogElement;

  constructor(private treeService: TreeService,     
    private elementService: ElementService, 
    private objService: ObjService,
    private tabsService: TabsService,
    private log: LogService,
    private contentManager: TinyMCEFormContentManagerService,
    private draggingService: DraggingService,
    private formsList: PlominoFormsListService,
    private appLoader: PlominoApplicationLoaderService,
    private activeEditorService: PlominoActiveEditorService,
    private zone: NgZone,
    private changeDetector: ChangeDetectorRef) {
      window['jQuery'] = jQuery;

      this.addDialog = <HTMLDialogElement> 
        document.querySelector('#modal-tab-plus');

      if (!this.addDialog.showModal) {
        window['materialPromise'].then(() => {
          dialogPolyfill.registerDialog(this.addDialog);
        });
      }

      Array.from(
        this.addDialog
          .querySelectorAll('.mdl-dialog__actions button')
      )
      .forEach((btn: HTMLElement) => {
        btn.addEventListener('click', (evt) => {
          if (btn.dataset.create === 'form') {
            this.addNewForm(evt);
          }
          else if (btn.dataset.create === 'view') {
            this.addNewView(evt);
          }
          this.addDialog.close();
        });
      })
    }

  collapseTreeElements(data:any, oldData:any) {
    if(!Array.isArray(data) || Array.isArray(oldData))
      return data;

    data.forEach((item: any) => {
      item.collapsed = !(item.label === 'Forms' && item.type === 'PlominoForm');
      item.children = this.collapseTreeElements(item.children, null);
    });

    return data.slice();
  }

  ngOnInit() {
    $('#add-new-form-tab').remove();
    const addNewFormBtn = `<li class="add-new-form-tab" id="add-new-form-tab">
      <a href class="nav-link"><span class="icon material-icons">add</span></a>
      <div class="mdl-tooltip mdl-tooltip--large" for="add-new-form-tab">
      Click to add a new form or view
      </div>
    </li>`;

    $('div.main-app.panel > tabset > ul').append(addNewFormBtn);
    $('#add-new-form-tab').click((evt) => {
      $('#add-new-form-tab .mdl-tooltip').removeClass('is-active');
      this.addDialog.showModal();
      evt.preventDefault();
      return false;
    });

    this.treeService
    .getTree()
    .subscribe((tree) => {
      let data = this.collapseTreeElements(tree, this.data);
      if (!data) { return; }

      /* little callback hell */
      data = data.filter((dataItem: any) => dataItem.type !== 'PlominoAgent');

      const topFormsViewsList: any[] = [];
      data.forEach((z: any, topIndex: number) => {
        z.children.forEach((firstLevelChildrenItem: any, index: number) => {
          let tmp = firstLevelChildrenItem.children;
          firstLevelChildrenItem.children.forEach((subChild: any) => {
            firstLevelChildrenItem.typeLabel = z.label;
            subChild.children.forEach((subChild: any) => {
              subChild.typeNameUrl = firstLevelChildrenItem.url;
            });
            tmp = tmp.concat(subChild.children);
          });
          tmp = tmp.filter((item: any) => {
            return !item.folder;
          });
          data[topIndex].children[index].children = tmp;
          data[topIndex].children[index].typeNameUrl = z.url;
          topFormsViewsList.push(firstLevelChildrenItem);
        });
      });
      
      /* extracting children of children */
      this.data = topFormsViewsList;
      this.formsList.setForms(topFormsViewsList);
      this.appLoader.markLoaded('app.component');
      
      /* fix the tooltips */
      topFormsViewsList.forEach((x: any) => {
        $(`[data-mdl-for="tab_${ x.url }"]`).html(x.label);
      });
    });
    
    this.tabsService
    .getTabs()
    .subscribe((tabs: any) => {
      this.tabs = tabs;

      tabs.forEach((tab: any) => {
        if (tab.active && this.tabsService.closing) {
          this.tabsService.closing = false;
        }
      });
    });

    this.draggingService
    .getDragging()
    .subscribe((dragData: any) => {
      this.isDragging = !!dragData;
      this.dragData = dragData;
    })

    $(() => {
      $('.palette-wrapper .mdl-tabs__panel')
      .css('height', `${ window.innerHeight / 2 }px`);

      this.resizeInnerScrollingContainers();

      window['Modal'] = require('mockup-patterns-modal');
      window['TineMCE'] = require('mockup-patterns-tinymce');

      require('./assets/scripts/macros.js');
      require('./assets/scripts/dynamic.js');
      require('./assets/scripts/links.js');
    });
  }

  ngAfterViewInit() {
    this.tabsService.getActiveTab().subscribe(() => {});
  }

  getTabTypeImage(editor: any) {
    return {
      'layout': 'images/ic_featured_play_list_black_18px.svg',
      'code': 'images/ic_code_black_18px.svg',
    }[editor] || 'images/ic_code_black_18px.svg';
  }

  onAdd(event: any) {
    event.isAction = event.type == "PlominoAction";
    this.modalData = event;
    this.isModalOpen = true;
  }

  resizeColumns(event: { directions: string[], difference: {x: number, y: number} }) {
    const directions = event.directions;
    const difference = event.difference;

    const contains = (direction: string) => {
      return directions.indexOf(direction) !== -1;
    };

    if (!directions.length) { return; }

    const $wrapper = $('.well.sidebar');
    const attribute = 'width';
    let width = this.wrapperWidth;

    if (contains(this.DIRECTION_LEFT)) {
      width = width - difference.x - 1;
    }
    else if (contains(this.DIRECTION_RIGHT)) {
      width = width + difference.x + 1;
    }

    this.wrapperWidth = width;
    $wrapper.css(attribute, `${ width }px`);
  }

  resizeInnerScrollingContainers() {
    const $wrapper = $('.palette-wrapper .mdl-tabs__panel');
    const $containers76 = $('.scrolling-container--76');
    const $containers66 = $('.scrolling-container--66');
    const $containers0 = $('.scrolling-container--0');
    const height = parseInt($wrapper.css('height').replace('px', ''), 10);
    $containers76.css('height', `${ height - 76 }px`);
    $containers66.css('height', `${ height - 66 }px`);
    $containers0.css('height', `${ height }px`);
  }

  resizeTree(event: { directions: string[], difference: {x: number, y: number} }) {
    const directions = event.directions;
    const difference = event.difference;

    const contains = (direction: string) => {
      return directions.indexOf(direction) !== -1;
    };

    if (!directions.length) { return; }

    const $wrapper = $('.palette-wrapper .mdl-tabs__panel');
    let height = parseInt($wrapper.css('height').replace('px', ''), 10);

    if (contains(this.DIRECTION_UP)) {
      height = height - difference.y - 0.5;
    }
    else if (contains(this.DIRECTION_DOWN)) {
      height = height + difference.y;
    }

    $wrapper.css('height', `${ height }px`);
    this.resizeInnerScrollingContainers();
  }

  indexOf(type: any) {
    let index: any = {};
    let parentToSearch: any;

    if (type.parent === undefined)
      parentToSearch = type.type;
    else
      parentToSearch = type.parentType;

    switch (parentToSearch) {
      case 'Forms':
        index.parent = 0;
        break;
      case 'Views':
        index.parent = 1;
        break;
      case 'Agents':
        index.parent = 2;
        break;
    }

    if (type.parent != undefined) {
      index.index = this.searchParentIndex(type.parent, index.parent);
      switch (index.parent) {
        case 0:
          switch (type.type) {
              case 'Fields':
                index.child = 0;
                break;
              case 'Actions':
                index.child = 1;
                break;
          }
          break;
        case 1:
          switch (type.type) {
              case 'Actions':
                index.child = 0;
                break;
              case 'Columns':
                index.child = 1;
                break;
          }
          break;
      }
    }

    return index;

  }

  searchParentIndex(parent: string, index: number) {
    for (let i = 0; i < this.data[index].children.length; i++) {
      if (this.data[index].children[i].label === parent) return i;
    }
    return -1;
  }

  allowDrop() {
    let dataType = this.dragData['@type'];
    return () => dataType === 'PlominoForm' || dataType === 'PlominoView';
  }

  dropped() {
    this.resolveData(this.dragData, this.dragData.resolver);
  }

  openTab(tab: any) {
    this.log.info('this.tabsService.openTab #app0001 with showAdd');
    this.tabsService.openTab(tab, true);
  }

  closeTab(tab: any) {
    this.activeEditorService.setActive(null);
    this.tabsService.closing = true;
    this.tabsService.closeTab(tab);

    setTimeout(() => {
      // debugger;
      /* detect wrong case */
      const $activeTrigger = $('.tab-trigger[data-active="true"]');
      if ($activeTrigger.length) {
        const url = $activeTrigger.attr('data-url');
        const editor = $activeTrigger.attr('data-editor');

        if (editor === 'layout') {
          this.activeEditorService.setActive(url);
        }
        
        // check that tinymce is broken after 100ms
        if (this.activeEditorService.getActive()) {
          const $iframe = $(this.activeEditorService.getActive()
              .getContainer().querySelector('iframe'));
          let x = $iframe.contents().find('body').html();
          if (
            /* x === '' in case when <p> are missing, why? */
            typeof x === 'undefined' || !x.length
            // typeof x === 'undefined' || (!x.length 
            //   && !$iframe.contents().find('body').length
            // )
          ) {
            // const $tinyTextarea = $iframe.closest('form').find('>textarea');
            tinymce.EditorManager.execCommand('mceRemoveEditor', true, url);
            tinymce.EditorManager.execCommand('mceAddEditor', true, url);
            tinymce.EditorManager.execCommand('mceAddEditor', true, url);

            /* reset content hooks */
            setTimeout(() => {
              const x = this.contentManager.getContent(
                this.activeEditorService.editorURL
              );
              this.contentManager.setContent(
                this.activeEditorService.editorURL, x,
                this.draggingService
              );
            }, 100);
          }
        }
      }
    }, 100);
  }

  onModalClose(event: any) {
    this.isModalOpen = false;
    
    let newElement: any = {
      "@type": event.type,
      "title": event.name
    };
    
    if (event.type == "PlominoAgent")
      newElement.content = "";
    if (event.type == "PlominoAction")
      newElement.action_type = event.action_type;
    
    this.elementService
    .postElement(event.url,newElement)
    .subscribe(data => this.treeService.updateTree());
  }

  onTabSelect(tab: any) {
    this.log.info('onTabSelect', tab);
    this.activeEditorService.setActive(
      tab.path[0].type === 'Forms' ? tab.url : null
    );
    this.log.info('onTabSelect setActive', tab.path[0].type === 'Forms' ? tab.url : null);
    this.log.info('onTabSelect getActive', this.activeEditorService.editorURL, this.activeEditorService.getActive());
    this.tabsService.setActiveTab(tab, true);
  }

  fieldSelected(fieldData: any): void {
    this.tabsService.selectField(fieldData);
  }

  setTabzAsDirty(tabz: any, dirty: boolean) {
    this.log.info('setTabzAsDirty', tabz, tabz.url, dirty);
    tabz.isdirty = dirty;

    if (!dirty) {
      $(`span[data-url="${ tabz.url }"] > span:contains("* ")`).remove();
      if (tinymce.get(tabz.url)) {
        tinymce.get(tabz.url).setDirty(false);
      }
    }

    $(window)
    .unbind('beforeunload')
    .bind('beforeunload', (eventObject: any) => {
      if (tabz.isdirty && !window['reloadAccepted']) {
        return confirm('Do you want to close window. The form is unsaved.');
      }
    });
  }

  private addNewView(event: MouseEvent) {
    event.preventDefault();
    let viewElement: InsertFieldEvent = {
      '@type': 'PlominoView',
      'title': 'New View'
    };
    this.elementService.postElement(this.getDBLink(), viewElement)
    .subscribe((response: AddFieldResponse) => {
      this.treeService.updateTree().then(() => {
        this.log.info('this.tabsService.openTab #app0009');
        this.tabsService.openTab({
          editor: 'view',
          label: response.title,
          url: response.parent['@id'] + '/' + response.id,
          path: [{
              name: response.title,
              type: 'Views'
          }]
        });
      });
    });
  }

  private addNewForm(event: MouseEvent) {
    event.preventDefault();
    let formElement: InsertFieldEvent = {
        '@type': 'PlominoForm',
        'title': 'New Form'
    };
    this.elementService.postElement(this.getDBLink(), formElement)
    .subscribe((response: AddFieldResponse) => {
      this.treeService.updateTree().then(() => {
        const randomId = Math.floor(Math.random() * 1e10 + 1e10);
        this.log.info('this.tabsService.openTab #app0009');
        this.tabsService.openTab({
          formUniqueId: randomId,
          editor: 'layout',
          label: response.title,
          url: response.parent['@id'] + '/' + response.id,
          path: [{
              name: response.title,
              type: 'Forms'
          }]
        });
      });
    });
  }

  private getPloneLink() {
    const dbLink = this.getDBLink();
    return dbLink.split('/').slice(0, -1).join('/')
  }

  private getDBLink() {
    return `${ 
      window.location.pathname
      .replace('++resource++Products.CMFPlomino/ide/', '')
      .replace('/index.html', '')
    }`;
  }

  private resolveData(data: any, resolver: Function): void {
    resolver(null, data);
  }
}

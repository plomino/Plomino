import { FormsService } from './forms.service';
import { Subject, Observable, BehaviorSubject } from 'rxjs/Rx';
import { PlominoActiveEditorService } from './active-editor.service';
import { URLManagerService } from './url-manager.service';
import { PlominoElementAdapterService } from './element-adapter.service';
import { LogService } from './log.service';
import { Injectable, NgZone, ChangeDetectorRef } from '@angular/core';
import { TreeService } from './tree.service';

@Injectable()
export class TabsService {

  public closing: boolean = false;
  public refreshCodeTab: Subject<string> = new Subject<string>();
  public onRefreshCodeTab$ = this.refreshCodeTab.asObservable();

  private activeTab$: BehaviorSubject<PlominoTab> = new BehaviorSubject(null);
  private activeField$: BehaviorSubject<any> = new BehaviorSubject(null);
  private tabs$: BehaviorSubject<any[]> = new BehaviorSubject([]);
  private tree: any;
  
  workflowModeChange: Subject<boolean> = new Subject<boolean>();
  workflowModeChanged$ = this.workflowModeChange.asObservable();

  constructor(
    private treeService: TreeService,
    private adapter: PlominoElementAdapterService,
    private changeDetector: ChangeDetectorRef,
    private urlManager: URLManagerService,
    private formsService: FormsService,
    private activeEditorService: PlominoActiveEditorService,
    private log: LogService, private zone: NgZone
  ) {
    this.treeService.getTree()
      .subscribe((tree) => {
        this.tree = tree;
      });
  }

  selectField(fieldData: any): void {
    let field: any = null;

    this.log.info('selectField', fieldData, this.adapter.getSelectedBefore());

    if (fieldData && fieldData !== 'none' 
      && !fieldData.id && fieldData.type === 'subform') {
      setTimeout(() => {
        const $selected = $(this.activeEditorService.getActive().getBody())
          .find('[data-mce-selected="1"]');
        this.log.info('hacked id', $selected.data('plominoid'));
        fieldData.id = $selected.data('plominoid');

        if (typeof fieldData.id === 'undefined' 
        && $selected.hasClass('plominoSubformClass')) {
          fieldData.id = 'Subform';
        }

        if (fieldData && fieldData !== 'none' && fieldData.id) {
        
          field = Object.assign({}, { 
            id: fieldData.id, 
            url: `${fieldData.parent}/${fieldData.id}`, 
            type: fieldData.type 
          });
        }
    
        this.activeField$.next(field);
      }, 100);
    }
    else {
      if (fieldData && fieldData !== 'none' && fieldData.id) {
        
        field = Object.assign({}, { 
          id: fieldData.id, 
          url: `${fieldData.parent}/${fieldData.id}`, 
          type: fieldData.type 
        });
      }
  
      this.activeField$.next(field);
    }
  }

  selectNonExistingField(fieldData: { url: string, type: string, parent: string }): void {
    let field: any = null;
    
    field = Object.assign({}, {  
      id: `${fieldData.parent}/${ fieldData.url }`, 
      type: fieldData.type 
    });

    this.activeField$.next(field);
  }

  getActiveField(): Observable<PlominoFieldRepresentationObject> {
    return this.activeField$.asObservable().share();
  }

  ping() {
    let tabs = this.tabs$.getValue().slice(0);
    return tabs.map((tab) => tab.isdirty);
  }

  setActiveTabDirty(dirty = true) {
    let tabs = this.tabs$.getValue().slice(0);
    tabs.forEach((tab) => {
      if (tab.active) {
        this.log.info('setActiveTabDirty dirty', tab.url);
        tab.isdirty = dirty;
      }
    });
  }

  setActiveTab(tab: PlominoTab, showAdd = false): void {

    const isWorkflowTab = tab.url.split('/').pop() === 'workflow';
    
    if (tab.active) {
      return;
    }

    let tabs: PlominoTab[] = this.tabs$.getValue().slice(0);

    // const activeTab = <any> this.activeTab$.getValue();
    // if (activeTab && !activeTab.isdirty) {
    //   setTimeout(() => {
    //     activeTab.isdirty = false;
    //     const ed = tinymce.get(activeTab.url);
    //     if (ed) {
    //       ed.setDirty(false);
    //     }
    //   }, 200);
    // }

    this.urlManager.rebuildURL(tabs);
    const normalizedTab: any = Object.assign({}, this.retrieveTab(this.tree, tab), { showAdd: showAdd });

    if (normalizedTab && tab.editor && tab.editor === 'code') {
      normalizedTab.editor = 'code'; // I don't know why the editor field reduced

      if (tab.path && tab.path.length > 1 && tab.path[1].type === 'Fields') {
        normalizedTab.isField = true;
      }
    }

    const selectedTab: any = _.find(tabs, { url: tab.url, editor: tab.editor });
    
    tabs.forEach(tab => { tab.active = (tab.url === selectedTab.url) });

    if (!isWorkflowTab) {
      window.location.hash = `#form=${ tab.url.split('/').pop() }`;
      this.activeTab$.next(normalizedTab);
      this.workflowModeChange.next(false);
    }
    else {
      this.workflowModeChange.next(true);
    }
    this.tabs$.next(tabs);
  }

  openTab(tab: any, showAdd = true): void {
    let tabs: any[] = this.tabs$.getValue();
    let tabIsOpen = _.find(tabs, { url: tab.url, editor: tab.editor });

    const isFormTab = tab.editor !== 'code' && tab.path && Array.isArray(tab.path) 
      && tab.path.length && tab.path[0].type === 'Forms';

    const isActiveForm = isFormTab && this.activeEditorService.getActive()
      && this.activeEditorService.getActive().id === tab.url;

    if (isActiveForm) {
      return;
    }

    if (tabIsOpen) {
      if (tabIsOpen.url !== 'workflow') {
        this.setActiveTab(tab, false);
      }
      else {
        // let tabs = this.tabs$.getValue().slice(0);
        // tabs.forEach(tab => { tab.active = (tab.url === tabIsOpen.url) });
        // this.formsService.changePaletteTab(0);
      }
    } else {
      let builtedTab: PlominoTab = this.buildTab(tab, showAdd);
      tabs.forEach((tab) => tab.active = false);
      tabs.push(builtedTab);
      this.tabs$.next(tabs);
      if (builtedTab.url !== 'workflow') {
        this.setActiveTab(tab, showAdd);
        this.workflowModeChange.next(false);
      }
      else {
        this.formsService.changePaletteTab(0);
        this.workflowModeChange.next(true);
      }
    }
    
  }

  closeTab(tab: any): void {
    let tabs: any[] = this.tabs$.getValue();
    let tabIndex = 0;
    
    tabs.forEach((value, index) => {
      const accepted = value.url === tab.url/* && value.editor === tab.editor*/;
      if (accepted) {
        tabIndex = index;
        return false;
      }
    });

    tabs.splice(tabIndex, 1);
    
    if (tabs.length === 0) {
      this.activeTab$.next(null);
      this.activeField$.next(null);
    }

    this.tabs$.next(tabs);
    this.changeDetector.markForCheck();
    this.changeDetector.detectChanges();
    this.urlManager.rebuildURL(tabs);
  }

  updateTabId(tab: any, newID: number|string): void {
    // console.warn('UPDATE TAB ID', 'tab', tab, 'newID', newID);
    let tabs = this.tabs$.getValue();
    let updateTab: PlominoTab = _.find(tabs, (item:any) => item.url === tab.url);
    updateTab.url = `${this.getParent(updateTab.url)}/${newID}`;
    tab.url = `${this.getParent(updateTab.url)}/${newID}`;

    /**
     * update page hash
     */
    if (updateTab.active) {
      this.urlManager.rebuildURL(tabs);
    }
  }

  updateTab(tabData: any, id: any): void {
    // console.warn('UPDATE TAB', 'tabData', tabData, 'id', id);
    let tabs = this.tabs$.getValue().slice(0);
    let activeTab = Object.assign({}, this.activeTab$.getValue());

    let tabToUpdate = _.find(tabs, (tab: any) => {
      return tab.url === tabData.url;
    });

    tabToUpdate.url = `${this.getParent(tabToUpdate.url)}/${id}`;
    activeTab.url = `${this.getParent(activeTab.url)}/${id}`;

    this.tabs$.next(tabs);
    this.activeTab$.next(activeTab);
  }

  getActiveTab(): Observable<PlominoTab> {
    return this.activeTab$.asObservable();
  }

  getTabs(): Observable<any[]> {
    return this.tabs$.asObservable();
  }

  private retrieveTab(tree: any[], tab: PlominoTab): any {
    if (!tab.path.length) {
      return tab;
    }

    let pindex = this.index(tab.path[0].type);

    for (let elt of tree[pindex].children) {
      if (elt.url.split('/').pop() == tab.url.split('/').pop()) {
        if (tab.path.length > 1) {
          let cindex = this.index(tab.path[1].type, pindex);
          for (let celt of elt.children[cindex].children) {
            if (celt.label == tab.path[1].name) {
              return celt;
            }
          }
        } else {
          return elt;
        }
      }
    }
  }

  private index(type: string, parentIndex?: number) {
    if (parentIndex === undefined) {
      
      switch (type) {
        case 'Forms':
          return 0;
        case 'Views':
          return 1;
        case 'Agents':
          return 2;
        default: 
      }

    } else {
      switch (parentIndex) {
        case 0:
          
          switch (type) {
            case 'Fields':
              return 0;
            case 'Actions':
              return 1;
            case 'Hide Whens':
              return 2;
            default:
          }

          break;
        case 1:
          
          switch (type) {
            case 'Actions':
              return 0;
            case 'Columns':
              return 1;
            default:
          }

          break;
        case 2:
          return 0;
      }
    }
  }

  private buildTab(tab: any, showAdd: boolean): any {
    let newtab = { 
      title: tab.label, 
      editor: tab.editor, 
      path: tab.path, 
      url: tab.url,
      formUniqueId: tab.formUniqueId,
      active: true,
      showAdd: showAdd 
    };
    
    /* if (newtab.editor === 'code') {
     *     this.aceNumber++;
     * }
     * What is this code for ?!
     */ 
    return newtab;
  }

  private getParent(url: string): string { 
    return url.slice(0, url.lastIndexOf('/'));
  }

  private getId(url: string): string {
    return url.slice(url.lastIndexOf('/') + 1);
  }
}

import { 
  Injectable,
  NgZone 
} from '@angular/core';

import { Observable } from 'rxjs/Observable';
import { BehaviorSubject } from 'rxjs/BehaviorSubject';

import { TreeService } from './tree.service';

import 'lodash';
declare let _:any;

@Injectable()
export class TabsService {
  private activeTab$: BehaviorSubject<any> = new BehaviorSubject(null);
  private activeField$: BehaviorSubject<any> = new BehaviorSubject(null);
  private tabs$: BehaviorSubject<any[]> = new BehaviorSubject([]);
  private tree: any;

  constructor(private treeService: TreeService,
              private zone: NgZone) {
    this.treeService.getTree()
      .subscribe((tree) => {
        this.tree = tree;
      });
  }

  setActiveTab(tab: any, showAdd = false): void {
    
    if (tab.active) {
      return;
    }

    let tabs = this.tabs$.getValue().slice(0);
    let normalizedTab: any = Object.assign({}, this.retrieveTab(this.tree, tab), { showAdd: showAdd });
    let selectedTab: any = _.find(tabs, { url: tab.url, editor: tab.editor });
    
    tabs.forEach(tab => { tab.active = (tab.url === selectedTab.url) });

    this.activeTab$.next(normalizedTab);
    this.tabs$.next(tabs);
  }

  openTab(tab: any, showAdd = true): void {
    let tabs: any[] = this.tabs$.getValue();
    let tabIsOpen: boolean = _.find(tabs, { url: tab.url, editor: tab.editor });
    
    if (tabIsOpen) {
      
      this.setActiveTab(tab, false);

    } else {
      let builtedTab: any = this.buildTab(tab, showAdd);
      tabs.forEach((tab) => tab.active = false);
      tabs.push(builtedTab);
      this.tabs$.next(tabs);
      this.setActiveTab(tab, showAdd);
    }
    
  }

  closeTab(tab: any): void {
    let tabs: any[] = this.tabs$.getValue();
    tabs.splice(tabs.indexOf(tab), 1);
    
    if (tabs.length === 0) {
      this.activeTab$.next(null);
      this.activeField$.next(null);
    }

    this.tabs$.next(tabs);
  }

  selectField(fieldData: { id: string, type: string, parent: string }): void {
    let field: any = null;

    if (fieldData && fieldData.id) {
      field = Object.assign({}, { 
        id: fieldData.id, 
        url: `${fieldData.parent}/${fieldData.id}`, 
        type: fieldData.type 
      });
    }

    this.activeField$.next(field);
  }

  getActiveTab(): Observable<any> {
    return this.activeTab$.asObservable();
  }

  getActiveField(): Observable<any> {
    return this.activeField$.asObservable().share();
  }

  getTabs(): Observable<any[]> {
    return this.tabs$.asObservable();
  }

  private retrieveTab(tree: any[], tab: any): any {
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
}
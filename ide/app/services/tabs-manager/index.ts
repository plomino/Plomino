import { Observable, Subject } from 'rxjs/Rx';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoTabsManagerService {

  public workflowModeChange: Subject<boolean> = new Subject<boolean>();
  public workflowModeChanged$ = this.workflowModeChange.asObservable();

  public refreshCodeTab: Subject<string> = new Subject<string>();
  public onRefreshCodeTab$ = this.refreshCodeTab.asObservable();

  public setOpenedTabActive = true;
  public saveClosingTab = true;

  private tabOpenEvents: Subject<PlominoTabUnit> = new Subject();
  private tabIdUpdateEvents: Subject<{prevId: string, nextId: string}> 
    = new Subject<{prevId: string, nextId: string}>();
  private tabIdAfterUpdateEvents: Subject<{prevId: string, nextId: string}> 
    = new Subject<{prevId: string, nextId: string}>();
  private tabActiveChangedEvents: Subject<PlominoTabUnit> = new Subject();
  private tabCloseEvents: Subject<PlominoTabUnit> = new Subject();
  private activeTabDirtyReceiver: Subject<boolean> = new Subject();
  private tabDirtyReceiver: Subject<{tab: PlominoTabUnit, state: boolean}> 
    = new Subject<{tab: PlominoTabUnit, state: boolean}>();

  constructor() { }

  openTab(tab: PlominoTabUnit) {
    this.tabOpenEvents.next(tab);
  }

  setActive(tab: PlominoTabUnit) {
    this.tabActiveChangedEvents.next(tab);
    this.workflowModeChange.next(tab && tab.editor === 'workflow');
  }

  setActiveTabDirty(state: boolean) {
    this.activeTabDirtyReceiver.next(state);
  }

  setTabDirty(tab: PlominoTabUnit, state: boolean) {
    this.tabDirtyReceiver.next({ tab, state });
  }

  closeTab(tab: PlominoTabUnit) {
    this.tabCloseEvents.next(tab);
  }

  updateTabId(prevId: string, nextId: string) {
    this.tabIdUpdateEvents.next({ prevId, nextId });
  }

  tabIdUpdated(prevId: string, nextId: string) {
    this.tabIdAfterUpdateEvents.next({ prevId, nextId });
  }

  /* observables: */
  
  getOpeningTab(): Observable<PlominoTabUnit> {
    return this.tabOpenEvents.asObservable();
  }

  getActiveTab(): Observable<PlominoTabUnit> {
    return this.tabActiveChangedEvents.asObservable();
  }

  getUpdateIdOfTab(): Observable<{prevId: string, nextId: string}> {
    return this.tabIdUpdateEvents.asObservable();
  }

  getAfterUpdateIdOfTab(): Observable<{prevId: string, nextId: string}> {
    return this.tabIdAfterUpdateEvents.asObservable();
  }

  getClosingTab(): Observable<PlominoTabUnit> {
    return this.tabCloseEvents.asObservable();
  }

  getActiveTabDirty(): Observable<boolean> {
    return this.activeTabDirtyReceiver.asObservable();
  }

  getTabDirty(): Observable<{tab: PlominoTabUnit, state: boolean}> {
    return this.tabDirtyReceiver.asObservable();
  }
}

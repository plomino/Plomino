import { Observable, Subject } from "rxjs/Rx";
import { Injectable } from "@angular/core";

@Injectable()
export class PlominoTabsManagerService {
    public workflowModeChange: Subject<boolean> = new Subject<boolean>();
    public workflowModeChanged$ = this.workflowModeChange.asObservable();

    public refreshCodeTab: Subject<string> = new Subject<string>();
    public onRefreshCodeTab$ = this.refreshCodeTab.asObservable();

    public setOpenedTabActive = true;
    public saveClosingTab = true;

    private tabOpenEvents: Subject<PlominoTabUnit> = new Subject();
    private tabIdUpdateEvents: Subject<{ prevId: string; nextId: string }> = new Subject<{
        prevId: string;
        nextId: string;
    }>();
    private tabIdAfterUpdateEvents: Subject<{ prevId: string; nextId: string }> = new Subject<{
        prevId: string;
        nextId: string;
    }>();
    private tabActiveChangedEvents: Subject<PlominoTabUnit> = new Subject();
    private tabCloseEvents: Subject<PlominoTabUnit> = new Subject();
    private activeTabDirtyReceiver: Subject<boolean> = new Subject();
    private tabDirtyReceiver: Subject<{ tab: PlominoTabUnit; state: boolean }> = new Subject<{
        tab: PlominoTabUnit;
        state: boolean;
    }>();

    private tabContentStates: Map<string, { content: string; pattern?: string }> = new Map<
        string,
        { content: string; pattern?: string }
    >();

    private dirtyTabs: Set<string> = new Set();

    constructor() {
        this.getAfterUpdateIdOfTab().subscribe(data => {
            this.dirtyTabs.delete(data.prevId);
            if (this.tabContentStates.has(data.prevId)) {
                // const prevState = this.tabContentStates.get(data.prevId);
                // if (prevState.pattern) {
                //   const patObject = JSON.parse(prevState.pattern);
                //   let tmp = patObject.upload.currentPath.split('/');
                //   tmp[tmp.length - 1] = data.nextId;
                //   patObject.upload.currentPath = tmp.join('/');
                //   tmp = patObject.base_url.split('/');
                //   tmp[tmp.length - 1] = data.nextId;
                //   patObject.base_url = tmp.join('/');
                //   prevState.pattern = JSON.stringify(patObject);
                // }
                // this.tabContentStates.set(data.nextId, prevState);
                this.tabContentStates.delete(data.prevId);
            }
        });

        this.getTabDirty().subscribe(data => {
            const editorId = data.tab.editor === "code" ? this.generateCodeEditorId(data.tab.url) : data.tab.id;
            this.dirtyTabs[data.state ? "add" : "delete"](editorId);
        });
    }

    isTabDirty(tabId: string) {
        return this.dirtyTabs.has(tabId);
    }

    tabIsNotDirty(tabId: string) {
        return !this.isTabDirty(tabId);
    }

    openTab(tab: PlominoTabUnit) {
        this.tabOpenEvents.next(tab);
    }

    setActive(tab: PlominoTabUnit) {
        this.tabActiveChangedEvents.next(tab);
        this.workflowModeChange.next(tab && tab.editor === "workflow");
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

    getUpdateIdOfTab(): Observable<{ prevId: string; nextId: string }> {
        return this.tabIdUpdateEvents.asObservable();
    }

    getAfterUpdateIdOfTab(): Observable<{ prevId: string; nextId: string }> {
        return this.tabIdAfterUpdateEvents.asObservable();
    }

    getClosingTab(): Observable<PlominoTabUnit> {
        return this.tabCloseEvents.asObservable();
    }

    getActiveTabDirty(): Observable<boolean> {
        return this.activeTabDirtyReceiver.asObservable();
    }

    getTabDirty(): Observable<{ tab: PlominoTabUnit; state: boolean }> {
        return this.tabDirtyReceiver.asObservable();
    }

    saveTabContentState(tabId: string, data: { content: string; pattern?: string }) {
        this.tabContentStates.set(tabId, data);
    }

    flushTabContentState(tabId: string) {
        this.tabContentStates.delete(tabId);
    }

    getTabSavedContentState(tabId: string) {
        return this.tabContentStates.has(tabId) ? this.tabContentStates.get(tabId) : null;
    }

    getAllStates() {
        return Array.from(this.tabContentStates);
    }

    generateCodeEditorId(tabURL: string) {
        return "editor" + this.generateHash(tabURL);
    }

    private generateHash(str: string): number {
        let hash = 0,
            i,
            chr;
        if (str.length === 0) return hash;
        for (i = 0; i < str.length; i++) {
            chr = str.charCodeAt(i);
            hash = (hash << 5) - hash + chr;
            hash |= 0; // Convert to 32bit integer
        }
        return hash;
    }
}

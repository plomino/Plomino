import { LogService } from "./../../services/log.service";
import { URLManagerService } from "./../../services/url-manager.service";
import { PlominoTabsManagerService } from "./../../services/tabs-manager/index";
import { ElementService } from "./../../services/element.service";
import { PlominoDBService } from "./../../services/db.service";
import { PlominoSaveManagerService } from "./../../services/save-manager/save-manager.service";
import { PlominoTabComponent } from "./tab/plomino-tab.component";
import { Component, OnInit, ChangeDetectorRef } from "@angular/core";

@Component({
    selector: "plomino-tabs",
    template: require("./plomino-tabs.component.html"),
    styles: [require("./plomino-tabs.component.css")],
    directives: [PlominoTabComponent],
})
export class PlominoTabsComponent implements OnInit {
    activeTab: PlominoTabUnit = null;
    tabsCollection: PlominoTabUnit[] = [];

    constructor(
        private saveManager: PlominoSaveManagerService,
        private dbService: PlominoDBService,
        private elementService: ElementService,
        private tabsManagerService: PlominoTabsManagerService,
        private urlManager: URLManagerService,
        private changeDetector: ChangeDetectorRef,
        private log: LogService
    ) {
        $(window).bind("beforeunload", (eventObject: any) => {
            if (
                tinymce.editors.length &&
                // tinymce.editors
                // .some((editor) =>
                // this.saveManager.isEditorUnsaved(
                //   this.dbService.getDBLink() + '/' + editor.id
                // ))
                // ||
                this.tabsCollection.some(tab => this.isTabDirty(tab))
            ) {
                return "Do you want to close window. The data is unsaved.";
            } else {
                return void 0;
            }
        });

        this.tabsManagerService.getOpeningTab().subscribe(tab => {
            const index = this.findTabIndex(tab);
            if (index === -1) {
                this.tabsCollection.push(tab);
                if (tab.editor === "layout" && this.tabsManagerService.setOpenedTabActive) {
                    this.saveManager.nextEditorSavedState(tab.url);
                }
            }
            if (this.tabsManagerService.setOpenedTabActive) {
                this.setTabActive(tab);
            }
        });

        this.tabsManagerService.getClosingTab().subscribe(tab => {
            this.removeTab(tab);
        });

        this.tabsManagerService.getUpdateIdOfTab().subscribe(data => {
            let updated = false;
            const prevExp = new RegExp(`^(.+?/)${data.prevId}$`);
            this.tabsCollection.forEach((tab, index) => {
                if (tab.id === data.prevId) {
                    updated = true;
                    tab.id = data.nextId;
                    tab.url = tab.url.replace(prevExp, `$1${data.nextId}`);
                }
            });
            if (updated) {
                this.urlManager.rebuildURL(this.tabsCollection);
                this.tabsManagerService.tabIdUpdated(data.prevId, data.nextId);
            }
        });

        this.tabsManagerService.getActiveTabDirty().subscribe(state => {
            this.activeTab.isDirty = state;
        });

        this.tabsManagerService.getTabDirty().subscribe(data => {
            const index = this.findTabIndex(data.tab);
            if (index !== -1) {
                this.tabsCollection[index].isDirty = data.state;
            }
        });
    }

    ngOnInit() {}

    onTabClick(event: MouseEvent, tab: PlominoTabUnit) {
        this.setTabActive(tab);
    }

    onTabRemoveClick(event: MouseEvent, tab: PlominoTabUnit) {
        /* stop event bubbling */
        event.preventDefault();
        event.stopImmediatePropagation();

        if (tab.editor === "layout" && (this.saveManager.isEditorUnsaved(tab.url) || this.isTabDirty(tab))) {
            // There should be a way to cancel this action, not just save or discard the changes
            this.elementService
                .awaitForConfirm({
                    dialogTitle: "Discard changes?",
                    text: "You have unsaved changes in this tab. Would you like to save your changes?",
                    confirmBtnText: "Save",
                    cancelBtnText: "Discard",
                    dialogWidth: "350px",
                })
                .then(() => {
                    this.tabsManagerService.closeTab(tab);
                })
                .catch(() => {
                    this.tabsManagerService.saveClosingTab = false;
                    this.tabsManagerService.closeTab(tab);
                });
        } else {
            this.tabsManagerService.closeTab(tab);
        }
    }

    findTabIndex(tab: PlominoTabUnit) {
        /* find tab's index in tabs collection */
        let index = -1;
        this.tabsCollection.forEach((yetAnotherTab, j) => {
            if (yetAnotherTab.id === tab.id && yetAnotherTab.editor === tab.editor) {
                index = j;
                return false;
            }
        });

        return index;
    }

    removeTab(tab: PlominoTabUnit) {
        /* find tab's index in tabs collection */
        let index = this.findTabIndex(tab);
        if (index === -1) {
            index = 0;
        }

        /** detect a cache of content of this tab and flush it */
        if (tab.editor === "code") {
            const codeId = this.tabsManagerService.generateCodeEditorId(tab.url);
            setTimeout(() => {
                this.tabsManagerService.flushTabContentState(codeId);
                this.log.info("flushTabContentState", codeId);
            }, 1);
        }

        /* if active tab removed - set another tab active */
        if (this.activeTab && this.activeTab.id === tab.id && this.activeTab.editor === tab.editor) {
            if (this.tabsCollection.length >= 2) {
                this.setTabActive(this.tabsCollection[index === 0 ? 1 : index - 1]);
                this.tabsCollection.splice(index, 1);
            } else {
                this.setTabActive(null);
                this.tabsCollection = [];
            }
        } else {
            this.tabsCollection.splice(index, 1);
        }

        /* remove tab from tabs collection */
        this.urlManager.rebuildURL(this.tabsCollection);
    }

    setTabActive(tab: PlominoTabUnit) {
        if (
            this.activeTab &&
            this.activeTab.editor === "layout" &&
            this.saveManager.isEditorUnsaved(this.activeTab.url) &&
            this.tabsManagerService.saveClosingTab
        ) {
            // this.saveManager.enqueueNewFormSaveProcess(this.activeTab.url);
            // this.saveManager.nextEditorSavedState(this.activeTab.url);
            // this.activeTab.isDirty = false;
            // this.tabsCollection.forEach((tab, index) => {
            //   if (tab.id === this.activeTab.id) {
            //     console.warn(this.tabsCollection[index].id, 'isDirty', false);
            //     this.tabsCollection[index].isDirty = false;
            //     this.changeDetector.detectChanges();
            //   }
            // });
        }
        this.tabsManagerService.saveClosingTab = true;
        this.activeTab = tab;
        this.tabsManagerService.setActive(tab);
        this.urlManager.rebuildURL(this.tabsCollection);
    }

    isTabActive(tab: PlominoTabUnit) {
        if (this.activeTab === null) {
            this.setTabActive(tab);
        }
        return this.activeTab.id === tab.id && this.activeTab.editor === tab.editor;
    }

    isTabDirty(tab: PlominoTabUnit) {
        return Boolean(tab.isDirty);
    }

    getTabTypeIconName(editor: string) {
        return {
            workflow: "work",
            layout: "featured_play_list",
            view: "code",
            code: "code",
        }[editor];
    }
}

import { PlominoWorkflowTreeService } from "./editors/workflow/workflow-tree.service";
import { PlominoTabsManagerService } from "./services/tabs-manager/index";
import { PlominoTabComponent } from "./utility/tabs/tab/plomino-tab.component";
import { PlominoTabsComponent } from "./utility/tabs/plomino-tabs.component";
import { PlominoWorkflowChangesNotifyService } from "./editors/workflow/workflow.changes.notify.service";
import { PlominoPaletteManagerService } from "./services/palette-manager/palette-manager";
import { LabelsRegistryService } from "./editors/tiny-mce/services/labels-registry.service";
import { TinyMCEFormContentManagerService } from "./editors/tiny-mce/content-manager/content-manager.service";

// Core
import { Component, NgZone, OnInit, ChangeDetectorRef } from "@angular/core";

// External Components
import { DND_DIRECTIVES } from "ng2-dnd";
// import {DndModule} from 'ng2-dnd';

// Components
import { TreeComponent } from "./tree-view";
import { PaletteComponent, PlominoWorkflowNodeSettingsComponent } from "./palette-view";

import {
    FormsSettingsComponent,
    FieldsSettingsComponent,
    ActionsSettingsComponent,
    HideWhenSettingsComponent,
    ViewsSettingsComponent,
    ColumnsSettingsComponent,
    AgentsSettingsComponent,
} from "./editors";

// Services
import {
    LogService,
    PlominoHTTPAPIService,
    TreeService,
    ElementService,
    ObjService,
    PlominoFormFieldsSelectionService,
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
    PlominoSaveManagerService,
    PlominoDBService,
} from "./services";

// Pipes
import { ExtractNamePipe } from "./pipes";

// Utility Components
import { ResizeDividerComponent, PlominoBlockPreloaderComponent } from "./utility";
import { LoadingComponent } from "./editors/loading/loading.component";

@Component({
    selector: "plomino-app",
    template: require("./app.component.html"),
    styles: [require("./app.component.css")],
    directives: [
        TreeComponent,
        PaletteComponent,
        // TAB_DIRECTIVES,
        DND_DIRECTIVES,
        // TinyMCEComponent,
        // ACEEditorComponent,
        // PlominoModalComponent,
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
        // PlominoWorkflowComponent,
        PlominoWorkflowNodeSettingsComponent,
        // PlominoViewEditorComponent,
        PlominoTabComponent,
        PlominoTabsComponent,
    ],
    providers: [
        LogService,
        PlominoFormFieldsSelectionService,
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
        PlominoSaveManagerService,
        PlominoPaletteManagerService,
        PlominoDBService,
        PlominoTabsManagerService,
        PlominoWorkflowTreeService,
    ],
    pipes: [ExtractNamePipe],
})
export class AppComponent implements OnInit {
    data: any;
    isModalOpen = false;
    modalData: any;

    isDragging = false;
    dragData: any = null;

    /* Should be able to bind value to here: ide/app/app.component.css#L307 */
    wrapperWidth = 600;
    addDialog: HTMLDialogElement;
    dbName = "Plomino IDE";

    constructor(
        private treeService: TreeService,
        private elementService: ElementService,
        private objService: ObjService,
        private tabsService: TabsService,
        private formFieldsSelection: PlominoFormFieldsSelectionService,
        private log: LogService,
        private contentManager: TinyMCEFormContentManagerService,
        private draggingService: DraggingService,
        private formsList: PlominoFormsListService,
        private appLoader: PlominoApplicationLoaderService,
        private activeEditorService: PlominoActiveEditorService,
        private zone: NgZone,
        private paletteManager: PlominoPaletteManagerService,
        private saveManager: PlominoSaveManagerService,
        private dbService: PlominoDBService,
        private changeDetector: ChangeDetectorRef
    ) {
        window["jQuery"] = jQuery;

        this.addDialog = <HTMLDialogElement>document.querySelector("#modal-tab-plus");

        if (!this.addDialog.showModal) {
            window["materialPromise"].then(() => {
                dialogPolyfill.registerDialog(this.addDialog);
            });
        }

        Array.from(this.addDialog.querySelectorAll(".mdl-dialog__actions button")).forEach((btn: HTMLElement) => {
            btn.addEventListener("click", evt => {
                if (btn.dataset.create === "form") {
                    this.addNewForm(evt);
                } else if (btn.dataset.create === "view") {
                    this.addNewView(evt);
                } else if (btn.dataset.create === "view/custom") {
                    this.addNewView(evt, true);
                }
                this.addDialog.close();
            });
        });
    }

    collapseTreeElements(data: any, oldData: any) {
        if (!Array.isArray(data) || Array.isArray(oldData)) {
            return data;
        }

        data.forEach((item: any) => {
            item.collapsed = !(item.label === "Forms" && item.type === "PlominoForm");
            item.children = this.collapseTreeElements(item.children, null);
        });

        return data.slice();
    }

    ngOnInit() {
        // $('#add-new-form-tab').remove();
        // const addNewFormBtn = `<li class="add-new-form-tab" id="add-new-form-tab">
        //   <a href class="nav-link"><span class="icon material-icons">add</span></a>
        //   <div class="mdl-tooltip mdl-tooltip--large" for="add-new-form-tab">
        //   Click to add a new form or view
        //   </div>
        // </li>`;

        // $('div.main-app.panel > tabset > ul').append(addNewFormBtn);
        $("body").delegate("#add-new-form-tab", "click", evt => {
            $("#add-new-form-tab .mdl-tooltip").removeClass("is-active");
            this.addDialog.showModal();
            evt.preventDefault();
            return false;
        });

        this.log.info("waiting designtree event from treeService...");
        this.treeService.getTree().subscribe(tree => {
            this.log.info("designtree event received:", tree);
            let data = this.collapseTreeElements(tree, this.data);
            if (!data) {
                this.log.warn("NO DATA", data);
                return;
            }

            /* little callback hell */
            data = data.filter((dataItem: any) => dataItem.type !== "PlominoAgent");

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
            this.appLoader.markLoaded("app.component");

            /* fix the tooltips */
            topFormsViewsList.forEach((x: any) => {
                $(`[data-mdl-for="tab_${x.url}"]`).html(x.label);
            });
        });

        this.draggingService.getDragging().subscribe((dragData: any) => {
            this.isDragging = !!dragData;
            this.dragData = dragData;
        });

        $(() => {
            $(".palette-wrapper .mdl-tabs__panel").css("height", `${window.innerHeight / 2}px`);

            this.paletteManager.resizeInnerScrollingContainers();

            window["Modal"] = require("mockup-patterns-modal");
            window["TineMCE"] = require("mockup-patterns-tinymce");
            // window['LinkModal'] = require('mockup-patterns-tinymce-links');

            require("./assets/scripts/macros.js");
            require("./assets/scripts/dynamic.js");
            require("./assets/scripts/links.js");
        });

        this.objService.getDB().subscribe(html => {
            //console.log($(html)[0].getElementsByTagName('title'));
            $(html).each((idx, elem) => {
                if (elem.tagName == "TITLE") this.dbName = elem.innerHTML;
            });
        });
    }

    onAdd(event: any) {
        event.isAction = event.type == "PlominoAction";
        this.modalData = event;
        this.isModalOpen = true;
    }

    resizeColumns(amountToDrag: { x: number; y: number }) {
        const $wrapper = $(".well.sidebar");
        const attribute = "width";
        const width = this.wrapperWidth;
        const newWidth = width + amountToDrag.x;

        this.wrapperWidth = newWidth;
        $wrapper.css(attribute, `${newWidth}px`);
    }

    resizeTree(amountToDrag: { x: number; y: number }) {
        const $wrapper = $(".palette-wrapper .mdl-tabs__panel");
        const height = parseInt($wrapper.css("height").replace("px", ""), 10);
        const newHeight = height + amountToDrag.y;

        $wrapper.css("height", `${newHeight}px`);
        this.paletteManager.resizeInnerScrollingContainers();
    }

    indexOf(type: any) {
        const index: any = {};
        let parentToSearch: any;

        if (type.parent === undefined) parentToSearch = type.type;
        else parentToSearch = type.parentType;

        switch (parentToSearch) {
            case "Forms":
                index.parent = 0;
                break;
            case "Views":
                index.parent = 1;
                break;
            case "Agents":
                index.parent = 2;
                break;
        }

        if (type.parent != undefined) {
            index.index = this.searchParentIndex(type.parent, index.parent);
            switch (index.parent) {
                case 0:
                    switch (type.type) {
                        case "Fields":
                            index.child = 0;
                            break;
                        case "Actions":
                            index.child = 1;
                            break;
                    }
                    break;
                case 1:
                    switch (type.type) {
                        case "Actions":
                            index.child = 0;
                            break;
                        case "Columns":
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
        const dataType = this.dragData["@type"];
        return () => dataType === "PlominoForm" || dataType === "PlominoView" || dataType === "PlominoView/custom";
    }

    dropped() {
        this.resolveData(this.dragData, this.dragData.resolver);
    }

    onModalClose(event: any) {
        this.isModalOpen = false;

        const newElement: any = {
            "@type": event.type,
            title: event.name,
        };

        if (event.type == "PlominoAgent") newElement.content = "";
        if (event.type == "PlominoAction") newElement.action_type = event.action_type;

        this.elementService.postElement(event.url, newElement).subscribe(data => this.treeService.updateTree());
    }

    private addNewView(event: MouseEvent, custom = false) {
        event.preventDefault();
        if (custom) this.saveManager.createNewCustomView();
        else this.saveManager.createNewView();
    }

    private addNewForm(event: MouseEvent) {
        event.preventDefault();
        this.saveManager.createNewForm();
    }

    private getPloneLink() {
        const dbLink = this.dbService.getDBLink();
        return dbLink
            .split("/")
            .slice(0, -1)
            .join("/");
    }

    private resolveData(data: any, resolver: Function): void {
        resolver(null, data);
    }

    private getEditor(id: string) {
        const edId = id ? id.split("/").pop() : null;
        return tinymce.get(edId);
    }
}

import { PlominoTabsManagerService } from "./../services/tabs-manager/index";
import { PlominoDBService } from "./../services/db.service";
import { PlominoActiveEditorService } from "./../services/active-editor.service";
import { Component, Input, Output, EventEmitter, ViewChildren, OnInit, ChangeDetectorRef } from "@angular/core";

import { CollapseDirective } from "ng2-bootstrap/ng2-bootstrap";
import { DND_DIRECTIVES } from "ng2-dnd";

import {
    ElementService,
    TabsService,
    FormsService,
    DraggingService,
    LogService,
    PlominoFormFieldsSelectionService,
} from "../services";

import { ExtractNamePipe } from "../pipes";
import { Observable, Subscription } from "rxjs/Rx";

@Component({
    selector: "plomino-tree",
    template: require("./tree.component.html"),
    styles: [require("./tree.component.css")],
    directives: [CollapseDirective, DND_DIRECTIVES],
    pipes: [ExtractNamePipe],
    providers: [ElementService],
})
export class TreeComponent implements OnInit {
    @Input() data: any;
    @Output() add = new EventEmitter();
    @ViewChildren("selectable") element: any;

    @Input() selected: any;
    searchResults: any;
    filtered = false;
    workflowMode = false;
    previousSelected: any;

    private click2DragDelay: Subscription;

    constructor(
        private _elementService: ElementService,
        private tabsService: TabsService,
        private formFieldsSelection: PlominoFormFieldsSelectionService,
        private formsService: FormsService,
        private log: LogService,
        private activeEditorService: PlominoActiveEditorService,
        private changeDetector: ChangeDetectorRef,
        public draggingService: DraggingService,
        private dbService: PlominoDBService,
        private tabsManagerService: PlominoTabsManagerService
    ) {}

    ngOnInit() {
        this.tabsManagerService.getActiveTab().subscribe(tabUnit => {
            const activeTab = tabUnit
                ? {
                      label: tabUnit.label || tabUnit.id,
                      url: tabUnit.url,
                      editor: tabUnit.editor,
                  }
                : null;

            this.log.info("activeTab", activeTab);
            this.log.extra("tree.component.ts ngOnInit");
            this.selected = activeTab;
        });

        this.tabsManagerService.workflowModeChanged$.subscribe((value: boolean) => {
            this.workflowMode = value;
        });
    }

    treeArrowClick(ev: MouseEvent, typeName: any) {
        typeName.collapsed = !this.getCollapseState(
            typeName.collapsed,
            this.selected && typeName.url === this.selected.url
        );

        if (ev.screenX && ev.screenX <= 45 && ev.screenX > 31) {
            ev.preventDefault();
            ev.stopPropagation();
        }
    }

    getCollapseState(collapseVar: any, selected: boolean) {
        return typeof collapseVar === "undefined" && !selected
            ? true
            : collapseVar === null
            ? false
            : collapseVar === true;
    }

    isItSelected(name: any) {
        if (name === this.selected) {
            if (this.selected != this.previousSelected) {
                this.previousSelected = this.selected;
                this.scroll();
            }
            return true;
        } else {
            return false;
        }
    }

    dragSubformToWorkflow(dragEvent: DragEvent, formURL: string, formLabel: string, typeLabel: string) {
        this.draggingService.followDNDType("existing-subform::" + formURL + "::" + formLabel + "::" + typeLabel);
        dragEvent.dataTransfer.setData("text", formURL);
    }

    selectDBSettingsTab() {
        this.formsService.changePaletteTab(3);
    }

    treeFormItemClick(
        selected: any,
        mouseEvent: MouseEvent,
        typeLabel: string,
        typeNameUrl: string,
        typeNameLabel: string,
        formUniqueId: string
    ) {
        if (["PlominoField", "PlominoHidewhen", "PlominoAction"].indexOf(typeLabel) !== -1) {
            mouseEvent.stopImmediatePropagation();
        }
        this.click2DragDelay = Observable.timer(500, 1000).subscribe((t: number) => {
            if (typeLabel === "Forms") {
                this.dragSubform(selected, mouseEvent, typeLabel, typeNameUrl);
            }
            if (["PlominoField", "PlominoHidewhen", "PlominoAction"].indexOf(typeLabel) !== -1) {
                this.dragField(selected, mouseEvent, typeLabel, typeNameUrl);
            }
            this.click2DragDelay.unsubscribe();
        });

        return true;
    }

    dragField(selected: any, mouseEvent: MouseEvent, typeLabel: string, typeNameUrl: string) {
        this.log.info("drag field", selected, mouseEvent, typeLabel, typeNameUrl);
        this.log.extra("tree.component.ts dragField");

        if (
            this.activeEditorService.getActive() &&
            selected &&
            ["PlominoField", "PlominoHidewhen", "PlominoAction"].indexOf(typeLabel) !== -1 &&
            typeNameUrl
                .split("/")
                .slice(0, -1)
                .join("/") === selected.url
        ) {
            this.draggingService.treeFieldDragEvent.next({ mouseEvent, fieldType: typeLabel });
            this.draggingService.followDNDType("tree-field");
        }
    }

    dragSubform(selected: boolean, mouseEvent: MouseEvent, typeLabel: string, typeNameUrl: string) {
        this.log.info("drag subform", selected, mouseEvent, typeLabel, typeNameUrl);
        this.log.extra("tree.component.ts dragSubform");

        if (
            this.activeEditorService.getActive() &&
            selected &&
            typeLabel === "Forms" &&
            typeNameUrl !== `${this.dbService.getDBLink()}/${this.activeEditorService.getActive().id}`
        ) {
            this.draggingService.subformDragEvent.next(mouseEvent);
            this.draggingService.followDNDType("subform");
        }
    }

    getTypeImage(childName: any) {
        return (
            {
                PlominoField: "images/ic_input_black_18px.svg",
                PlominoHidewhen: "images/ic_remove_red_eye_black_18px.svg",
                PlominoAction: "images/ic_gavel_black_18px.svg",
                PlominoForm: "images/ic_featured_play_list_black_18px.svg",
                PlominoView: "images/ic_picture_in_picture_black_18px.svg",
            }[childName.type] || "images/ic_input_black_18px.svg"
        );
    }

    scroll() {
        if (this.element != undefined)
            for (const elt of this.element._results)
                if (elt.nativeElement.className === "selected") elt.nativeElement.scrollIntoView();
    }

    onEdit(event: any) {
        this.tabsManagerService.openTab({
            id: event.url.split("/").pop(),
            url: event.url,
            editor: event.editor,
            label: event.label,
        });
    }

    onAdd(event: any) {
        this.add.emit(event);
    }

    startDrag(data: any): void {
        if (data.type === "PlominoField" || data.type === "PlominoHidewhen") {
            this.draggingService.followDNDType(data.type);
        }
        this.draggingService.setDragging(data);
    }

    endDrag(): void {
        this.draggingService.setDragging(null);
    }

    onTreeFieldClick(fieldData: PlominoFieldTreeObject) {
        this.openFieldSettings(fieldData);
        this.selectFirstOccurenceInCurrentEditor(fieldData);
    }

    selectFirstOccurenceInCurrentEditor(fieldData: PlominoFieldTreeObject) {
        const editor = this.activeEditorService.getActive();
        if (editor) {
            const $body = $(this.activeEditorService.getActive().getBody());
            $body.find("[data-mce-selected]").removeAttr("data-mce-selected");

            const $results = $body.find(`.plominoFieldClass[data-plominoid="${fieldData.name.split("/").pop()}"]`);

            if ($results.length) {
                const $first = $results.first();
                $first.attr("data-mce-selected", "1");
            }
        }
    }

    openFieldSettings(fieldData: PlominoFieldTreeObject): void {
        const id = fieldData.name.slice(fieldData.name.lastIndexOf("/") + 1);
        if ((this.selected && this.selected.url) !== fieldData.parent) {
            const tabLabel = fieldData.parent.slice(fieldData.parent.lastIndexOf("/") + 1);

            this.tabsManagerService.openTab({
                id: fieldData.parent.split("/").pop(),
                url: fieldData.parent,
                editor: "layout",
                label: tabLabel,
            });

            // this.tabsService.openTab({
            //   formUniqueId: this.selected.formUniqueId,
            //   editor: 'layout',
            //   label: tabLabel,
            //   url: fieldData.parent,
            //   path: [
            //       {
            //           name: tabLabel,
            //           type: 'Forms'
            //       }
            //   ],
            // }, false);
        }
        this.formFieldsSelection.selectField({
            id: id,
            type: fieldData.type,
            parent: fieldData.parent,
        });
    }

    sendSearch(query: string) {
        if (query === "") {
            this.searchResults = null;
            this.filtered = false;
        } else
            this._elementService.searchElement(query).subscribe(
                (data: any) => {
                    this.searchResults = data;
                    this.filtered = true;
                },
                (err: any) => console.error(err)
            );
    }
}

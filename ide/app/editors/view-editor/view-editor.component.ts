import { PlominoDBService } from "./../../services/db.service";
import { DraggingService } from "./../../services/dragging.service";
import { PlominoBlockPreloaderComponent } from "./../../utility/block-preloader";
import { FieldsService } from "./../../services/fields.service";
import { DomSanitizationService, SafeHtml } from "@angular/platform-browser";
import { LogService } from "./../../services/log.service";
import { Component, Input, ViewEncapsulation, OnInit, NgZone, ChangeDetectorRef } from "@angular/core";
import { PlominoViewsAPIService } from "./views-api.service";
import { DND_DIRECTIVES } from "ng2-dnd";
import { PlominoFormFieldsSelectionService } from "../../services";

@Component({
    selector: "plomino-view-editor",
    template: require("./plomino-view-editor.component.html"),
    styles: [require("./plomino-view-editor.css")],
    providers: [PlominoViewsAPIService],
    directives: [PlominoBlockPreloaderComponent, DND_DIRECTIVES],
    encapsulation: ViewEncapsulation.None,
})
export class PlominoViewEditorComponent implements OnInit {
    @Input() item: PlominoTab;
    viewSourceTable: SafeHtml;
    loading = true;
    subsetIds: string[] = [];
    columns: HTMLElement[] = [];
    actions: HTMLElement[] = [];

    constructor(
        private api: PlominoViewsAPIService,
        private log: LogService,
        private fieldsService: FieldsService,
        private formFieldsSelection: PlominoFormFieldsSelectionService,
        private zone: NgZone,
        private dragService: DraggingService,
        private changeDetector: ChangeDetectorRef,
        protected sanitizer: DomSanitizationService,
        private dbService: PlominoDBService
    ) {}

    ngOnInit() {
        $("body").undelegate(`[data-url="${this.item.url}"] .actionButtons input[type="button"]`, "click");

        $("body").undelegate(`[data-url="${this.item.url}"] .view-editor__column-header`, "click");

        $("body").delegate(
            `[data-url="${this.item.url}"] .actionButtons input[type="button"]`,
            "click",
            (event: JQueryMouseEventObject) => {
                this.onActionClick(event.target);
            }
        );

        $("body").delegate(
            `[data-url="${this.item.url}"] .view-editor__column-header`,
            "click",
            (event: JQueryMouseEventObject) => {
                this.onColumnClick(<HTMLElement>event.target);
            }
        );

        this.reloadView();

        this.fieldsService
            .onColumnCreated()
            .subscribe((response: { oldId: string; newId: string; newTitle: string; fieldURL: string }) => {
                const viewColumnElement = $(`[data-url="${this.item.url}"] [data-column="${response.oldId}"]`).get(0);
                const newId = response.newId;
                const newTitle = response.newTitle;
                const fieldURL = response.fieldURL;

                viewColumnElement.classList.remove("view-editor__column-header--virtual");
                viewColumnElement.dataset.column = newId;
                viewColumnElement.innerHTML = newTitle;
                viewColumnElement.draggable = true;

                this.columns.push(viewColumnElement);

                if (viewColumnElement.dataset.unsortedDelta) {
                    const delta = parseInt(viewColumnElement.dataset.unsortedDelta, 10);
                    const subsetIds = JSON.parse(viewColumnElement.dataset.unsortedSubset);
                    const viewURL = window.location.href
                        .replace(
                            fieldURL
                                .split("/")
                                .slice(0, 2)
                                .join("/"),
                            fieldURL
                        )
                        .split("/")
                        .slice(0, 6)
                        .join("/");
                    subsetIds.push(newId);
                    this.api.reOrderItem(viewURL, newId, delta - 1, subsetIds).subscribe(() => {
                        this.fieldsService.viewReIndex.next(this.item.url);
                        // this.fieldsService.viewActionInserted.next(viewURL);
                        // this.reloadView();
                    });
                } else {
                    this.fieldsService.viewReIndex.next(this.item.url);
                }
            });

        this.fieldsService.onNewColumn().subscribe((response: string) => {
            // this.log.warn('onNewColumn, response', response);
            if (response === this.item.url) {
                if ($(`[data-url="${this.item.url}"] [data-column="++add++PlominoColumn"]`).length) {
                    return;
                }
                /* here you can add new virtual, use replace of virtual for dnd */
                const $column = $(
                    `<th data-column="++add++PlominoColumn"
              class="view-editor__column-header view-editor__column-header--virtual">
              new column
            </th>`
                );
                const $firstColumn = $(`[data-url="${this.item.url}"] th[data-column]:last`);
                if ($firstColumn.length) {
                    $firstColumn.after($column);
                } else {
                    $(`[data-url="${this.item.url}"] thead tr`).append($column);
                }
                $column.click();
                this.afterLoad();
            }
        });

        this.fieldsService.onReIndexItems().subscribe((response: string) => {
            // this.reIndexItems();
            if (response === this.item.url) {
                this.reloadView();
            }
        });

        this.fieldsService.onNewAction().subscribe((response: string) => {
            // this.log.warn('onNewColumn, response', response);
            if (response === this.item.url) {
                this.reloadView();
            }
        });

        this.fieldsService.onColumnUpdated().subscribe((response: string) => {
            // this.log.warn('onNewColumn, response', response);
            if (response === this.item.url) {
                this.reloadView();
            }
        });

        this.fieldsService.onDeleteSelectedViewColumn().subscribe((url: string) => {
            if (this.item.url.indexOf(url) !== -1) {
                this.deleteSelectedColumn();
            }
        });

        this.fieldsService.onDeleteSelectedViewAction().subscribe((url: string) => {
            if (this.item.url.indexOf(url) !== -1) {
                this.deleteSelectedAction();
            }
        });
    }

    reloadView() {
        this.subsetIds = [];
        this.loading = true;

        this.api
            .fetchViewTable(this.item.url, true)
            .subscribe((fetchResult: [string, PlominoVocabularyViewData, PlominoViewData]) => {
                const html = fetchResult[0];
                // const columns = fetchResult[1];
                const rows = fetchResult[2];

                // this.subsetIds = columns.results.map(r => r.id);

                let $html = $(html);
                $html = $html.find("article");

                const $h1 = $html.find(".documentFirstHeading");
                $h1.replaceWith(`<h3>${$h1.html()}</h3>`);

                $html
                    .find(".formControls")
                    .addClass("view-editor__actions")
                    .removeClass("formControls");

                const columns: Array<HTMLElement> = [];
                let index = 1;
                $html.find("th[data-column]").each((i, columnElement: HTMLElement) => {
                    columnElement.classList.add("view-editor__column-header");
                    columnElement.draggable = true;
                    columnElement.dataset.index = (index++).toString();
                    columns.push(columnElement);
                });
                this.subsetIds = columns.map(r => r.dataset.column);

                $html
                    .find('.actionButtons input[type="button"]')
                    .addClass("mdl-button mdl-js-button mdl-button--primary mdl-button--raised")
                    .attr("draggable", true)
                    .removeAttr("onclick");

                $html.find('.actionButtons input[type="button"]:not([id])').attr("disabled", "disabled");

                $html
                    .find("table")
                    .removeAttr("class")
                    .prepend("<thead></thead>");

                this.viewSourceTable = this.sanitizer.bypassSecurityTrustHtml($html.html());

                try {
                    this.changeDetector.markForCheck();
                    this.changeDetector.detectChanges();
                } catch (e) {}

                setTimeout(() => {
                    // this.log.warn('new html received', $html.html());

                    /* attach indexes */
                    //          columns.results.forEach((result, index) => {
                    //            const element: HTMLElement = (() => {
                    //              if (result.Type === 'PlominoColumn') {
                    //                return $(
                    //                  `[data-url="${ this.item.url }"] th[data-column="${ result.id }"]`
                    //                );
                    //              }
                    //              else if (result.Type === 'PlominoAction') {
                    //                return $(
                    //                  `[data-url="${ this.item.url }"] input#${ result.id }`
                    //                );
                    //              }
                    //            })()
                    //            .get(0);
                    //
                    //            if (element) {
                    //              element.dataset.index = (index + 1).toString();
                    //            }
                    //          });

                    const $thead = $(`[data-url="${this.item.url}"] table thead`);
                    const $headRow = $(`[data-url="${this.item.url}"] .header-row:first`);
                    const totalColumns = $headRow.find("th").length;

                    $headRow.appendTo($thead);

                    rows.rows.forEach((row, rowIndex) => {
                        if (!row.length) {
                            return;
                        }

                        const writeId = row[0];

                        if (row.length === 1) {
                            /* should be empty row here? */
                            return;
                        }

                        row.slice(1).forEach((cellData, columnIndex) => {
                            let $cell = $(
                                `[data-url="${this.item.url}"] tbody tr:eq(${rowIndex}) td:eq(${columnIndex})`
                            );

                            if (!$cell.length) {
                                /* create new cell */
                                const $column = $(`[data-url="${this.item.url}"] th:eq(${columnIndex})`);

                                if (!$column.length) {
                                    /* something wrong here */
                                    return;
                                }

                                const $row = $(`[data-url="${this.item.url}"] tbody tr:eq(${rowIndex})`);

                                if (!$row.length) {
                                    /* create new row here */
                                    $(`[data-url="${this.item.url}"] tbody`).append(
                                        '<tr class="header-row count"><td></td></tr>'
                                    );
                                }

                                $cell = $(
                                    `[data-url="${this.item.url}"] tbody tr:eq(${rowIndex}) td:eq(${columnIndex})`
                                );

                                if (!$cell.length) {
                                    $row.append("<td></td>");
                                    $cell = $(
                                        `[data-url="${this.item.url}"] tbody tr:eq(${rowIndex}) td:eq(${columnIndex})`
                                    );
                                }
                            }

                            if (columnIndex === 0) {
                                const href = `${this.dbService.getDBLink()}/document/${writeId}`;
                                cellData = `<a href="${href}" target="_blank">${cellData}</a>`;
                            }

                            /* write the data to the cell */
                            $cell.html(cellData);
                        });
                    });
                    //
                    //          $(`[data-url="${ this.item.url }"] table tbody tr`).each((t, trElement) => {
                    //            const missed = totalColumns - $(trElement).find('td').length;
                    //
                    //            if (missed) {
                    //              for (let i = 0; i < missed; i++) {
                    //                $(trElement).append('<td></td>');
                    //              }
                    //            }
                    //          });

                    $(`[data-url="${this.item.url}"] table`).addClass(
                        "mdl-data-table mdl-js-data-table " + "mdl-shadow--2dp"
                    );

                    this.zone.runOutsideAngular(() => {
                        try {
                            componentHandler.upgradeDom();
                        } catch (e) {}
                    });
                }, 200);

                setTimeout(() => this.afterLoad(), 300);
            });
    }

    deleteSelectedColumn() {
        const $x = $(`[data-url="${this.item.url}"] .view-editor__column-header--selected`);
        const index = $x.index();
        $(`[data-url="${this.item.url}"] table tr`)
            .find("th:eq(" + index + "),td:eq(" + index + ")")
            .remove();
        this.afterLoad();
    }

    deleteSelectedAction() {
        const $x = $(`[data-url="${this.item.url}"] .view-editor__action--selected`);
        $x.remove();
        this.afterLoad();
    }

    reIndexItems() {
        this.api.fetchViewTableColumnsJSON(this.item.url).subscribe(json => {
            this.subsetIds = json.results.map(r => r.id);

            json.results.forEach((result, index) => {
                (() => {
                    if (result.Type === "PlominoColumn") {
                        return $(`[data-url="${this.item.url}"] th[data-column="${result.id}"]`);
                    } else if (result.Type === "PlominoAction") {
                        return $(`[data-url="${this.item.url}"] input#${result.id}`);
                    }
                })().get(0).dataset.index = (index + 1).toString();
            });

            this.afterLoad();
        });
    }

    onDragEnter(dropData: { dragData: { type: string }; mouseEvent: DragEvent }) {
        if (dropData.dragData.type && dropData.dragData.type === "column") {
            $(".view-editor__column-header--virtual").remove();
            this.formFieldsSelection.selectField(null);

            const $tr = $(`[data-url="${this.item.url}"] table thead tr`);
            $tr.append(
                `<th class="view-editor__column-header--drop-preview">
          new column
        </th>`
            );
            return true;
        } else if (dropData.dragData.type && dropData.dragData.type === "action") {
            $(".view-editor__action--drop-preview").remove();
            this.formFieldsSelection.selectField(null);

            const $x = $(`[data-url="${this.item.url}"] .view-editor__actions .actionButtons`);
            $x.append(
                ` <input class="context mdl-button mdl-js-button
          view-editor__action--drop-preview
          mdl-button--primary mdl-button--raised"
          value="default-action"
          type="button">`
            );
            return true;
        }
    }

    onDragLeave(dropData: { dragData: { type: string }; mouseEvent: DragEvent }) {
        if (dropData.dragData.type && dropData.dragData.type === "column") {
            const $th = $(`[data-url="${this.item.url}"] table thead tr th.view-editor__column-header--drop-preview`);
            $th.remove();
            return true;
        } else if (dropData.dragData.type && dropData.dragData.type === "action") {
            const $x = $(`[data-url="${this.item.url}"] .view-editor__action--drop-preview`);
            $x.remove();
            return true;
        }
    }

    onDropSuccess(dropData: { dragData: { type: string }; mouseEvent: DragEvent }) {
        if (dropData.dragData.type && dropData.dragData.type === "column") {
            const $_ = $(`[data-url="${this.item.url}"] [data-column="++add++PlominoColumn"]`);
            if ($_.length) {
                $_.remove(); // todo remove tdis
                this.formFieldsSelection.selectField(null);
            }

            const droppedColumn = $(".view-editor__column-header--drop-preview").get(0);
            droppedColumn.classList.remove("view-editor__column-header--drop-preview");
            droppedColumn.classList.add("view-editor__column-header");
            droppedColumn.classList.add("view-editor__column-header--virtual");
            droppedColumn.classList.add("view-editor__column-header--selected");
            droppedColumn.dataset.column = "++add++PlominoColumn";

            droppedColumn.click();
        } else if (dropData.dragData.type && dropData.dragData.type === "action") {
            this.loading = true;
            this.api.addNewAction(this.item.url).subscribe(response => {
                this.subsetIds.push(response.id);
                this.reloadView();
            });
        }
    }

    afterLoad() {
        let draggable: HTMLElement = null;
        this.columns = [];
        this.actions = [];

        $(
            `[data-url="${this.item.url}"] .view-editor__column-header` +
                `, [data-url="${this.item.url}"] ` +
                `.actionButtons input[type="button"]`
        ).each((i, element: HTMLElement) => {
            if (element.tagName === "INPUT" && element.id) {
                /* action button */
                const actionElement = <HTMLInputElement>element;

                this.actions.push(actionElement);

                actionElement.ondragstart = (ev: DragEvent) => {
                    $(".view-editor__action--drop-target").removeClass("view-editor__action--drop-target");
                    ev.dataTransfer.setData("text", "a:" + (<HTMLElement>ev.target).id);
                    draggable = actionElement;

                    this.dragService.followDNDType("existing-action");

                    return true;
                };

                actionElement.ondrop = (ev: DragEvent) => {
                    const dndType = this.dragService.dndType;
                    if (dndType !== "action" && dndType !== "existing-action") {
                        return true;
                    }
                    if (dndType === "action") {
                        /* insert action and do some math */
                        const currentIndex = parseInt(actionElement.dataset.index, 10);
                        const delta = (this.subsetIds.length - currentIndex) * -1;

                        this.loading = true;
                        this.api.addNewAction(this.item.url).subscribe(response => {
                            this.subsetIds.push(response.id);
                            this.api.reOrderItem(this.item.url, response.id, delta, this.subsetIds).subscribe(() => {
                                this.reloadView();
                            });
                        });
                    }
                    const transfer = ev.dataTransfer.getData("text");

                    if (transfer.indexOf("a:") !== -1) {
                        // this.loading = false;

                        const $from = $(draggable);
                        const $to = $(actionElement);

                        const $swapFrom = $from.clone();
                        const $swapTo = $to.clone();

                        $from.replaceWith($swapTo);
                        $to.replaceWith($swapFrom);

                        $(`.view-editor__action--drop-target`).removeClass("view-editor__action--drop-target");

                        this.api
                            .reOrderItem(
                                this.item.url,
                                draggable.id,
                                parseInt(actionElement.dataset.index, 10) - parseInt(draggable.dataset.index, 10),
                                this.subsetIds
                            )
                            .subscribe(() => {
                                this.reIndexItems();
                            });
                    }

                    return true;
                };

                actionElement.ondragover = (ev: DragEvent) => {
                    ev.preventDefault();
                };

                actionElement.ondragenter = (ev: DragEvent) => {
                    const dndType = this.dragService.dndType;
                    if (dndType !== "action" && dndType !== "existing-action") {
                        return true;
                    }
                    if (dndType === "action") {
                        /* insert shadow column after this btn */
                        const $btn = $(ev.target);
                        $btn.after(
                            ` <input class="context mdl-button mdl-js-button
                  view-editor__action--drop-preview
                  mdl-button--primary mdl-button--raised"
                  value="default-action"
                  type="button">`
                        );
                    }
                    $(".view-editor__action--drop-target").removeClass("view-editor__action--drop-target");
                    actionElement.classList.add("view-editor__action--drop-target");
                    return true;
                };

                actionElement.ondragleave = (ev: DragEvent) => {
                    const dndType = this.dragService.dndType;
                    if (dndType !== "action" && dndType !== "existing-action") {
                        return true;
                    }
                    if (dndType === "action") {
                        /* remove shadow action after this btn */
                        const $btn = $(ev.target);
                        $btn.next().remove();
                    }
                    actionElement.classList.remove("view-editor__action--drop-target");
                    return true;
                };
            } else if (element.tagName === "TH") {
                /* view column */
                const columnElement = element;

                this.columns.push(columnElement);

                columnElement.ondragstart = (ev: DragEvent) => {
                    $(".view-editor__column-header--drop-target").removeClass(
                        "view-editor__column-header--drop-target"
                    );
                    ev.dataTransfer.setData("text", "c:" + (<HTMLElement>ev.target).dataset.column);
                    draggable = columnElement;

                    this.dragService.followDNDType("existing-column");

                    return true;
                };

                columnElement.ondrop = (ev: DragEvent) => {
                    const dndType = this.dragService.dndType;
                    if (dndType !== "column" && dndType !== "existing-column") {
                        return true;
                    }
                    if (dndType === "column") {
                        const $_ = $(`[data-url="${this.item.url}"] [data-column="++add++PlominoColumn"]`);
                        if ($_.length) {
                            $_.remove(); // todo remove tdis
                            this.formFieldsSelection.selectField(null);
                        }

                        /* insert column and do some math */
                        const currentIndex = parseInt(columnElement.dataset.index, 10);
                        const delta = (this.subsetIds.length + 1 - currentIndex) * -1;

                        // this.loading = true;

                        const droppedColumn = <HTMLElement>columnElement.nextElementSibling;

                        droppedColumn.classList.remove("view-editor__column-header--drop-preview");
                        droppedColumn.classList.add("view-editor__column-header");
                        droppedColumn.classList.add("view-editor__column-header--virtual");
                        droppedColumn.classList.add("view-editor__column-header--selected");
                        droppedColumn.dataset.column = "++add++PlominoColumn";
                        droppedColumn.dataset.unsortedDelta = delta.toString();
                        droppedColumn.dataset.unsortedSubset = JSON.stringify(this.subsetIds);

                        columnElement.classList.remove("view-editor__column-header--selected");
                        columnElement.classList.remove("view-editor__column-header--drop-target");

                        droppedColumn.click();

                        // this.loading = false;

                        // this.subsetIds.push(newId);
                        // this.api.reOrderItem(this.item.url, newId, delta, this.subsetIds)
                        //   .subscribe(() => {
                        //     this.reloadView();
                        //   });
                    }
                    const transfer = ev.dataTransfer.getData("text");

                    if (transfer.indexOf("c:") !== -1) {
                        this.loading = true;

                        this.api
                            .reOrderItem(
                                this.item.url,
                                draggable.dataset.column,
                                parseInt(columnElement.dataset.index, 10) - parseInt(draggable.dataset.index, 10),
                                this.subsetIds
                            )
                            .subscribe(() => {
                                this.reloadView();
                            });
                    }

                    return true;
                };

                columnElement.ondragover = (ev: DragEvent) => {
                    ev.preventDefault();
                };

                columnElement.ondragenter = (ev: DragEvent) => {
                    const dndType = this.dragService.dndType;
                    if (dndType !== "column" && dndType !== "existing-column") {
                        return true;
                    }
                    if (dndType === "column") {
                        /* insert shadow column after this td */
                        const $td = $(ev.target);
                        $td.after(
                            `<th class="view-editor__column-header--drop-preview">
                  new column
                </th>`
                        );
                    }
                    $(".view-editor__column-header--drop-target").removeClass(
                        "view-editor__column-header--drop-target"
                    );
                    columnElement.classList.add("view-editor__column-header--drop-target");
                    return true;
                };

                columnElement.ondragleave = (ev: DragEvent) => {
                    const dndType = this.dragService.dndType;
                    if (dndType !== "column" && dndType !== "existing-column") {
                        return true;
                    }
                    if (dndType === "column") {
                        /* remove shadow column after this td */
                        const $td = $(ev.target);
                        $td.next().remove();
                    }
                    columnElement.classList.remove("view-editor__column-header--drop-target");
                    return true;
                };
            }
        });

        this.loading = false;
        // this.changeDetector.markForCheck();
        // this.changeDetector.detectChanges();
    }

    onActionClick(actionElement: Element) {
        $(".view-editor__column-header--selected").removeClass("view-editor__column-header--selected");
        $(".view-editor__action--selected").removeClass("view-editor__action--selected");
        actionElement.classList.add("view-editor__action--selected");
        this.log.info("view action selected", actionElement);
        this.formFieldsSelection.selectField({
            id: `${this.item.url.split("/").pop()}/${actionElement.id}`,
            type: "PlominoAction",
            parent: this.dbService.getDBLink(),
        });
    }

    onColumnClick(columnElement: HTMLElement) {
        $(".view-editor__column-header--virtual")
            .filter((i, column) => {
                return column !== columnElement;
            })
            .remove();

        $(".view-editor__column-header--selected").removeClass("view-editor__column-header--selected");
        $(".view-editor__action--selected").removeClass("view-editor__action--selected");

        columnElement.classList.add("view-editor__column-header--selected");
        this.log.info("view column selected", columnElement);
        this.formFieldsSelection.selectField({
            id: `${this.item.url.split("/").pop()}/${columnElement.dataset.column}`,
            type: "PlominoColumn",
            parent: this.dbService.getDBLink(),
        });
    }
}

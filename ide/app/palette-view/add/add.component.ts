import { PlominoTabsManagerService } from "./../../services/tabs-manager/index";
import { PlominoDBService } from "./../../services/db.service";
import { PlominoWorkflowChangesNotifyService } from "./../../editors/workflow/workflow.changes.notify.service";
import { WF_ITEM_TYPE } from "./../../editors/workflow/tree-builder";
import { Observable, Subject } from "rxjs/Rx";
import { PlominoActiveEditorService } from "./../../services/active-editor.service";
import { PlominoViewsAPIService } from "./../../editors/view-editor/views-api.service";
import { PlominoBlockPreloaderComponent } from "./../../utility/block-preloader";
import { LabelsRegistryService } from "./../../editors/tiny-mce/services/labels-registry.service";
import {
    Component,
    OnInit,
    AfterViewInit,
    ChangeDetectorRef,
    ElementRef,
    ChangeDetectionStrategy,
} from "@angular/core";

import { DND_DIRECTIVES } from "ng2-dnd";

import {
    ElementService,
    TreeService,
    TabsService,
    FieldsService,
    LogService,
    DraggingService,
    TemplatesService,
    WidgetService,
    PlominoSaveManagerService,
} from "../../services";

interface TemplateClickEvent {
    eventData: MouseEvent;
    target: any;
    templateId: string;
}

@Component({
    selector: "plomino-palette-add",
    template: require("./add.component.html"),
    styles: [require("./add.component.css")],
    directives: [DND_DIRECTIVES, PlominoBlockPreloaderComponent],
    providers: [ElementService, PlominoViewsAPIService, PlominoSaveManagerService],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AddComponent implements OnInit, AfterViewInit {
    activeTab: PlominoTab;
    templates: PlominoFormGroupTemplate[] = [];
    addableComponents: Array<any> = [];
    workflowComponents: Array<any> = [];
    mouseDownTemplateId: string;
    mouseDownTime: number;

    private tClickSubject: Subject<TemplateClickEvent> = new Subject<TemplateClickEvent>();
    public tClickFlow$: Observable<TemplateClickEvent> = this.tClickSubject.asObservable();
    private aClickSubject: Subject<string> = new Subject<string>();
    public aClickFlow$: Observable<string> = this.aClickSubject.asObservable();

    /**
     * display block preloader
     */
    loading = false;

    workflowMode = false;

    constructor(
        private elementService: ElementService,
        private treeService: TreeService,
        private tabsService: TabsService,
        private tabsManagerService: PlominoTabsManagerService,
        private log: LogService,
        private dbService: PlominoDBService,
        private viewsAPIService: PlominoViewsAPIService,
        private labelsRegistry: LabelsRegistryService,
        private fieldsService: FieldsService,
        private draggingService: DraggingService,
        private elementRef: ElementRef,
        private activeEditorService: PlominoActiveEditorService,
        private changeDetector: ChangeDetectorRef,
        private wfChange: PlominoWorkflowChangesNotifyService,
        private templatesService: TemplatesService,
        private widgetService: WidgetService,
        private saveManager: PlominoSaveManagerService
    ) {
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

    isWorkflowMode() {
        return this.workflowMode;
        // return Boolean(
        //   $('.nav-link.active span.tab-name:contains("workflow")')
        //   .filter((i, e) => $(e).text() === 'workflow')
        //   .length
        // );
    }

    getAddableComponents() {
        return this.isWorkflowMode() ? [] : this.addableComponents;
    }

    ngOnInit() {
        this.tabsManagerService.workflowModeChanged$.subscribe((value: boolean) => {
            this.workflowMode = value;
            setTimeout(() => {
                $(".nav-item:has(#tab_workflow)").css({ height: "42px", display: "flex", "align-items": "flex-end" });
            }, 200);
            this.changeDetector.markForCheck();
            this.changeDetector.detectChanges();
        });

        this.workflowComponents = [
            {
                title: "Form Task",
                type: WF_ITEM_TYPE.FORM_TASK,
            },
            {
                title: "View Task",
                type: WF_ITEM_TYPE.VIEW_TASK,
            },
            {
                title: "External Task",
                type: WF_ITEM_TYPE.EXT_TASK,
            },
            // {
            //   title: 'Process',
            //   type: WF_ITEM_TYPE.PROCESS
            // },
            {
                title: "Branch",
                type: WF_ITEM_TYPE.CONDITION,
            },
            {
                title: "Goto",
                type: WF_ITEM_TYPE.GOTO,
            },
        ];

        // Set up the addable components
        this.addableComponents = [
            {
                title: "Form",
                components: [
                    { title: "Label", icon: "", type: "PlominoLabel", addable: true },
                    { title: "Field", icon: "tasks", type: "PlominoField", addable: true },
                    { title: "Pagebreak", icon: "tasks", type: "PlominoPagebreak", addable: true },
                    { title: "Hide When", icon: "sunglasses", type: "PlominoHidewhen", addable: true },
                    { title: "Action", icon: "cog", type: "PlominoAction", addable: true },
                    { title: "Subform", icon: "cog", type: "PlominoSubform", addable: true },
                ],
                hidden: (tab: any) => {
                    if (!tab) return true;
                    return tab.editor !== "layout";
                },
            },
            {
                title: "View",
                components: [
                    {
                        title: "Column",
                        icon: "stats",
                        type: "column",
                        addable: true,
                        dragData: { type: "column" },
                    },
                    {
                        title: "Action",
                        icon: "cog",
                        type: "action",
                        addable: true,
                        dragData: { type: "action" },
                    },
                ],
                hidden: (tab: any) => {
                    if (!tab) return true;
                    return tab.editor === "layout";
                },
            },
            {
                title: "DB",
                components: [
                    { title: "Form", icon: "th-list", type: "PlominoForm", addable: true },
                    { title: "Empty View", icon: "list-alt", type: "PlominoView", addable: true },
                    { title: "All Form View", icon: "list-alt", type: "PlominoView/custom", addable: true },
                ],
                hidden: () => {
                    return false;
                },
            },
        ];

        this.tabsManagerService.getAfterUpdateIdOfTab().subscribe(updateData => {
            if (this.activeTab && this.activeTab.url && this.activeTab.url.split("/").pop() === updateData.prevId) {
                const split = this.activeTab.url.split("/");
                split[split.length - 1] = updateData.nextId;
                this.activeTab.url = split.join("/");
            }
        });

        // this.tabsService.getActiveTab()
        // .subscribe((tab) => {
        this.tabsManagerService.getActiveTab().subscribe(tabUnit => {
            const tab = tabUnit
                ? {
                      label: tabUnit.label || tabUnit.id,
                      url: tabUnit.url,
                      editor: tabUnit.editor,
                  }
                : null;

            this.log.info("tab", tab);
            this.log.extra("add.component.ts this.tabsService.getActiveTab()");

            this.templates = [];
            this.loading = true;
            this.activeTab = tab;
            this.changeDetector.markForCheck();
            this.changeDetector.detectChanges();

            this.workflowMode = false;
            if (tab && tab.editor !== "layout") {
                this.loading = false;
                if (tab.editor === "workflow") {
                    this.workflowMode = true;
                }
                this.changeDetector.markForCheck();
                this.changeDetector.detectChanges();
            } else if (tab && tab.url) {
                this.log.info("tab && tab.url", tab, tab.url);
                this.templatesService
                    .getTemplates(tab.url, tab.editor)
                    .subscribe((templates: PlominoFormGroupTemplate[]) => {
                        componentHandler.upgradeDom();
                        this.templates = templates.map(template => {
                            this.templatesService.buildTemplate(tab.url, template);

                            return Object.assign({}, template, {
                                url: `${tab.url.slice(0, tab.url.lastIndexOf("/"))}/${template.id}`,
                                hidewhen: (tab: any) => {
                                    if (!tab) return true;
                                    return tab.editor !== "layout";
                                },
                            });
                        });

                        $(
                            "#PlominoHidewhen, #PlominoAction, " +
                                "#PlominoField, #PlominoLabel, #PlominoPagebreak, #PlominoSubform"
                        ).each((i, element) => {
                            const $element = $(element);
                            const $id = $element.attr("id");

                            $element
                                .removeAttr("dnd-draggable")
                                .removeAttr("draggable")
                                .unbind()
                                .bind("mousedown", $event => {
                                    this.simulateDrag(<MouseEvent>$event.originalEvent, $id);
                                });
                        });

                        this.draggingService.subformDragEvent$.subscribe(mouseEvent => {
                            $("#drag-data-cursor").remove();
                            this.simulateDrag(mouseEvent, "PlominoSubform");
                        });

                        this.draggingService.treeFieldDragEvent$.subscribe(
                            (e: { mouseEvent: MouseEvent; fieldType: string }) => {
                                $("#drag-data-cursor").remove();
                                this.simulateDrag(e.mouseEvent, e.fieldType);
                            }
                        );

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

    add(type: string, target?: HTMLElement | true, treeSubform?: boolean) {
        const clickTime = new Date().getTime();

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
        const randomId: number = Math.round(Math.random() * 999 - 0);
        let field: InsertFieldEvent;

        const existingId = this.draggingService.currentDraggingData
            ? this.draggingService.currentDraggingData.existingElementId || null
            : null;

        switch (type) {
            case "PlominoForm":
                this.saveManager.createNewForm();
                break;
            case "PlominoView":
                this.saveManager.createNewView();
                break;
            case "PlominoView/custom":
                this.saveManager.createNewCustomView();
                break;
            case "PlominoLabel":
                this.log.startTimer("create_new_label_hold");
                let field: InsertFieldEvent = {
                    "@type": "PlominoLabel",
                    title: "defaultLabel",
                    name: `${this.activeTab.url}/defaultLabel`,
                    target,
                };
                this.fieldsService.insertField(field);
                this.log.stopTimer("create_new_label_hold");
                break;
            case "PlominoField":
                if (!existingId) {
                    this.log.startTimer("create_new_field_hold");
                    field = {
                        title: "defaultField",
                        "@type": "PlominoField",
                        target,
                    };
                    this.elementService
                        .postElement(this.activeTab.url, field)
                        .subscribe((response: AddFieldResponse) => {
                            const extendedField: InsertFieldEvent = Object.assign({}, field, {
                                name: `${this.activeTab.url}/${response.created}`,
                            });

                            this.labelsRegistry.update(
                                `${this.activeTab.url}/${response.created}`,
                                field.title,
                                "title"
                            );

                            this.fieldsService.insertField(extendedField);
                            this.log.stopTimer("create_new_field_hold");

                            this.treeService.updateTree().then(() => {});
                        });
                } else {
                    const url = `${this.activeTab.url}/${existingId}`;
                    this.fieldsService.insertField({
                        title: this.labelsRegistry.get(url),
                        "@type": "PlominoField",
                        name: url,
                        target,
                    });
                }
                break;
            case "PlominoPagebreak":
                field = {
                    name: `${this.activeTab.url}/defaultPagebreak`,
                    title: "defaultPagebreak",
                    "@type": "PlominoPagebreak",
                    target,
                };
                this.fieldsService.insertField(field);
                break;
            case "PlominoSubform":
                /**
                 * should be similar as on subform settings
                 */
                this.mouseDownTemplateId;
                this.draggingService.currentDraggingTemplateCode;

                const getSubformLayout$ = this.mouseDownTemplateId
                    ? this.widgetService.getGroupLayout(
                          `${this.dbService.getDBLink()}/${this.activeEditorService.getActive().id}`,
                          {
                              id: this.mouseDownTemplateId,
                              layout: $(this.draggingService.currentDraggingTemplateCode).html(),
                          }
                      )
                    : Observable.of("");

                getSubformLayout$.subscribe((result: string) => {
                    let subformHTML: string = null;

                    if (result) {
                        const $result = $(result);
                        $result
                            .find("input,textarea,button")
                            .removeAttr("name")
                            .removeAttr("id");
                        $result
                            .find("span")
                            .removeAttr("data-plominoid")
                            .removeAttr("data-mce-resize");
                        $result.removeAttr("data-groupid");
                        $result.find("div").removeAttr("data-groupid");
                        subformHTML = $($result.html()).html();
                    }

                    field = {
                        name: `${this.activeTab.url}/defaultSubform`,
                        title: this.mouseDownTemplateId || "defaultSubform",
                        "@type": "PlominoSubform",
                        subformHTML,
                        target,
                    };

                    this.fieldsService.insertField(field);
                });
                break;
            case "PlominoHidewhen":
                if (!existingId) {
                    field = {
                        title: "defaultHidewhen",
                        "@type": "PlominoHidewhen",
                    };
                    /**
                     * here the code does HTTP POST query to create a new field/etc
                     * and returns its widget code
                     */
                    this.elementService
                        .postElement(this.activeTab.url, field)
                        .subscribe((response: AddFieldResponse) => {
                            const extendedField = Object.assign({}, field, {
                                name: response["@id"],
                                target,
                            });

                            this.log.info("extendedField", extendedField);
                            this.fieldsService.insertField(extendedField);

                            this.treeService.updateTree().then(() => {});
                        });
                } else {
                    const url = `${this.activeTab.url}/${existingId}`;
                    this.fieldsService.insertField({
                        title: this.labelsRegistry.get(url),
                        "@type": "PlominoHidewhen",
                        name: url,
                        target,
                    });
                }
                break;
            case "PlominoAction":
                if (!existingId) {
                    field = {
                        title: "defaultAction",
                        action_type: "OPENFORM",
                        "@type": "PlominoAction",
                        target,
                    };
                    this.elementService
                        .postElement(this.activeTab.url, field)
                        .subscribe((response: AddFieldResponse) => {
                            const extendedField = Object.assign({}, field, {
                                name: response["@id"],
                            });
                            this.fieldsService.insertField(extendedField);
                            this.treeService.updateTree().then(() => {});
                        });
                } else {
                    const url = `${this.activeTab.url}/${existingId}`;
                    this.fieldsService.insertField({
                        title: this.labelsRegistry.get(url),
                        "@type": "PlominoAction",
                        name: url,
                        target,
                    });
                }
                break;
            case "column":
                this.fieldsService.viewColumnInserted.next(this.activeTab.url);
                break;
            case "action":
                field = {
                    title: "default-action",
                    action_type: "OPENFORM",
                    "@type": "PlominoAction",
                };
                this.viewsAPIService.addNewAction(this.activeTab.url).subscribe((response: AddFieldResponse) => {
                    this.fieldsService.viewActionInserted.next(this.activeTab.url);
                    const extendedField = Object.assign({}, field, {
                        name: response["@id"],
                    });

                    const url = this.activeTab.url;
                    const newAction = `<input class="context mdl-button
                  mdl-js-button mdl-button--primary mdl-button--raised"
                  type="button" id="${response.id}" name="${response.id}"
                  value="${response.title}">`;
                    $(`[data-url="${url}"] .actionButtons`).append(newAction);

                    componentHandler.upgradeDom();
                    $(`[data-url="${url}"] .actionButtons #${response.id}`).click();

                    this.fieldsService.insertField(extendedField);
                    this.treeService.updateTree().then(() => {});
                });
                break;
            default:
                console.log(type + " not handled yet");
        }
    }

    runAddTemplate(eventData: MouseEvent, target: any, templateId: string) {
        this.activeEditorService.turnActiveEditorToLoadingState();
        this.tClickSubject.next({ eventData, target, templateId });
    }

    runWfAdd(comp: string) {
        this.wfChange.runAdd.next(comp);
    }

    runAdd(comp: string) {
        this.activeEditorService.turnActiveEditorToLoadingState();
        this.aClickSubject.next(comp);
    }

    addTemplate(eventData: MouseEvent, target: any, templateId: string) {
        this.log.startTimer("create_new_template_hold");

        const a = $(eventData.currentTarget).data("templateId");
        const b = templateId;
        const c = this.mouseDownTemplateId;
        const clickTime = new Date().getTime();

        // 1. form insert: undefined, template-text, template-text
        // 2. form drag and return to blank: no
        // 3. form drag and return to keyboard: template_radio template_radio template_text
        // 4. click: template_long_text template_long_text template_long_text

        if (clickTime > this.mouseDownTime + 500 && typeof a !== "undefined" && c !== b) {
            return false;
        }

        this.templatesService
            .addTemplate(this.activeTab.url, templateId)
            .subscribe((response: PlominoFormGroupTemplate) => {
                response = this.templatesService.fixCustomTemplate(response);
                this.widgetService.getGroupLayout(this.activeTab.url, response).subscribe((layout: string) => {
                    layout = this.templatesService.fixBuildedTemplate(layout);

                    this.templatesService.insertTemplate(
                        <InsertTemplateEvent>Object.assign({}, response, {
                            parent: this.activeTab.url,
                            target: target,
                            group: layout,
                        })
                    );

                    this.log.stopTimer("create_new_template_hold");
                    this.activeEditorService.turnActiveEditorToLoadingState(false);
                    this.treeService.updateTree().then(() => {});
                });
            });
    }

    simulateDrag(eventData: MouseEvent, type: any, template?: PlominoFormGroupTemplate) {
        this.mouseDownTemplateId = template ? template.id : null;
        this.mouseDownTime = new Date().getTime();
        this.startDrag(eventData, type, template);
    }

    wfStartDrag(eventData: MouseEvent, type: any) {
        this.draggingService.followDNDType(type);
    }

    wfStopDrag() {}

    // Refactor this code, put switch into separated fn
    startDrag(eventData: MouseEvent, type: any, template?: PlominoFormGroupTemplate) {
        const draggingData: PlominoDraggingData = {
            "@type": type === "template" ? "PlominoTemplate" : type,
            resolver: () => {},
            resolved: false,
            eventData: eventData,
        };

        /* @Resolved & @Resolver are needed,
         * because we have 2 types of drag data for now
         * 1 type is drag data from tree, which is already
         * populated with server data, and drag data from
         * palette, which needs to be populated!
         * @Resolver will be called on drop event in tinymce.component
         */
        if (type !== "PlominoForm" && type !== "PlominoView" && type !== "PlominoView/custom") {
            draggingData.parent = this.activeTab.url;
        }

        let treeSubform = false;
        if (!template && eventData.target) {
            const eventTarget = <HTMLElement>eventData.target;
            const $target = eventTarget.classList.contains("tree-node--name")
                ? $(eventData.target)
                : $(eventData.target).find(".tree-node--name");
            let text = $target.text().trim();
            if (text) {
                this.mouseDownTemplateId = text;
                treeSubform = true;
            } else if (eventTarget.classList.contains("tree-node__child--name")) {
                text = $target.prevObject.text().trim();
                if (text) {
                    this.mouseDownTemplateId = text;
                    draggingData.existingElementId = text;
                    treeSubform = true;
                }
            }
        }

        if (type !== "template") {
            draggingData.resolver = (target, data = { "@type": "" }) => {
                this.add(data["@type"], target, treeSubform);
            };
        } else {
            draggingData.templateId = template.id;
            draggingData.template = template;
            draggingData.resolver = target => {
                this.addTemplate(eventData, target, template.id);
            };
        }

        this.draggingService.currentDraggingData = draggingData;
        this.draggingService.setDragging(draggingData);

        if (draggingData["@type"] && !draggingData.existingElementId) {
            this.draggingService.followDNDType(draggingData["@type"]);
        }
    }

    endDrag(): void {
        this.draggingService.setDragging(false);
    }

    private getDBOptionsLink(link: string) {
        return `${window.location.pathname
            .replace("++resource++Products.CMFPlomino/ide/", "")
            .replace("/index.html", "")}/${link}`;
    }
}

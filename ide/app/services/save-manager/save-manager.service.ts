import { ObjService } from "./../obj.service";
import { PlominoTabsManagerService } from "./../tabs-manager/index";
import { LogService } from "./../log.service";
import { PlominoFormsListService } from "./../forms-list.service";
import { PlominoDBService } from "./../db.service";
import { TabsService } from "./../tabs.service";
import { TreeService } from "./../tree.service";
import { PlominoViewSaveProcess } from "./view-save-process";
import { FakeFormData } from "./../../utility/fd-helper/fd-helper";
import { Observable, Subject } from "rxjs/Rx";
import { PlominoFormSaveProcess } from "./form-save-process";
import { TinyMCEFormContentManagerService } from "./../../editors/tiny-mce/content-manager/content-manager.service";
import { Injectable } from "@angular/core";
import { PlominoHTTPAPIService, ElementService, WidgetService, PlominoActiveEditorService } from "../";
import { LabelsRegistryService } from "../../editors/tiny-mce/services";
import { Response } from "@angular/http";

@Injectable()
export class PlominoSaveManagerService {
    private savedStates: Map<string, string> = new Map<string, string>();
    private saveStack: Array<Observable<any>> = [];
    private saveNotifier: Subject<string> = new Subject<string>();
    private currentFormIsUnsaved = false;
    private createCustomViewDialog: HTMLDialogElement;
    private $createCustomViewDialog: JQuery;
    private addCustomView: Subject<any> = new Subject<any>();
    private addCustomView$: Observable<any> = this.addCustomView.asObservable();

    constructor(
        private contentManager: TinyMCEFormContentManagerService,
        private http: PlominoHTTPAPIService,
        private objService: ObjService,
        private elementService: ElementService,
        private treeService: TreeService,
        private widgetService: WidgetService,
        private tabsService: TabsService,
        private tabsManagerService: PlominoTabsManagerService,
        private labelsRegistry: LabelsRegistryService,
        private activeEditorService: PlominoActiveEditorService,
        private dbService: PlominoDBService,
        private log: LogService,
        private formsList: PlominoFormsListService
    ) {
        Observable.interval(500)
            .flatMap(() => (this.saveStack.length ? this.saveStack.pop() : Observable.of(null)))
            .subscribe(data => {
                if (data) {
                    this.saveNotifier.next(data.url);
                }
            });

        this.listenDocumentClicks();
        this.listenFormInnerChangeProcesses();
    }

    onBackgroundSaveProcessComplete() {
        return this.saveNotifier.asObservable();
    }

    nextEditorSavedState(editorId: string, state: string = null): void {
        try {
            this.savedStates.set(editorId, state || this.contentManager.getContent(editorId));
        } catch (e) {
            /**
             * if there were some problems ontop
             * like the state is null and getContent didn't find the editor
             * we will wait 3 second to be sure that all is ok
             */
            setTimeout(() => {
                this.savedStates.set(editorId, state || this.contentManager.getContent(editorId));
                this.log.warn("there were some errors prevented");
                this.log.extra("save-manager.service.ts nextEditorSavedState");
            }, 3000);
        }
    }

    isEditorUnsaved(editorId: string): boolean {
        if (this.savedStates.has(editorId)) {
            return this.savedStates.get(editorId) !== this.contentManager.getContent(editorId);
        } else {
            return true;
        }
    }

    createNewForm(callback: (url: string, label: string) => void = null, callbackBeforeOpeningTab = false) {
        const formElement: InsertFieldEvent = {
            "@type": "PlominoForm",
            title: "New Form",
        };
        this.elementService
            .postElement(this.dbService.getDBLink(), formElement)
            .subscribe((response: AddFieldResponse) => {
                this.treeService.updateTree().then(() => {
                    const callCallback = () => {
                        this.log.info("new form created");
                        this.log.extra("save-manager.service.ts createNewForm callCallback");
                        if (callback !== null) {
                            callback(response.parent["@id"] + "/" + response.id, response.title);
                        }
                    };

                    if (callbackBeforeOpeningTab) {
                        callCallback();
                    }

                    this.tabsManagerService.openTab({
                        editor: "layout",
                        label: response.title,
                        id: response.id,
                        url: response.parent["@id"] + "/" + response.id,
                    });

                    if (!callbackBeforeOpeningTab) {
                        setTimeout(() => callCallback(), 100);
                    }
                });
            });
    }

    createNewView(callback: (url: string, label: string) => void = null, callbackBeforeOpeningTab = false) {
        const viewElement: InsertFieldEvent = {
            "@type": "PlominoView",
            title: "New View",
        };
        this.elementService
            .postElement(this.dbService.getDBLink(), viewElement)
            .subscribe((response: AddFieldResponse) => {
                this.treeService.updateTree().then(() => {
                    const callCallback = () => {
                        if (callback !== null) {
                            callback(response.parent["@id"] + "/" + response.id, response.title);
                        }
                    };

                    if (callbackBeforeOpeningTab) {
                        callCallback();
                    }

                    this.tabsManagerService.openTab({
                        editor: "view",
                        label: response.title,
                        url: response.parent["@id"] + "/" + response.id,
                        id: response.id,
                    });

                    if (!callbackBeforeOpeningTab) {
                        setTimeout(() => callCallback(), 100);
                    }
                });
            });
    }

    createNewCustomView(callback: (url: string, label: string) => void = null, callbackBeforeOpeningTab = false) {
        this.setupCreateCustomViewDialog();
        const error = this.createCustomViewDialog.querySelector("span.mdl-dialog__error");
        const formSelect = this.createCustomViewDialog.querySelector("#new-view-dialog__form");
        const fieldSelect = this.createCustomViewDialog.querySelector("#new-view-dialog__field");
        const viewIdInput = this.createCustomViewDialog.querySelector("#new-view-dialog__id");
        const viewTitleInput = this.createCustomViewDialog.querySelector("#new-view-dialog__title");
        formSelect.innerHTML = this.formsList
            .getForms()
            .map((form: any) => `<option value="${form.url.split("/").pop()}">${form.label}</option>`)
            .join("");

        $(error).attr("display", "none");
        // bind event to select input
        $(formSelect).change(evt => {
            $(fieldSelect).val([]);
            const formId = $(formSelect).val();
            this.formsList.getForms().forEach(form => {
                if (form.url.split("/").pop() == formId) {
                    // select all field of that form
                    fieldSelect.innerHTML = form.children
                        .map((field: any) => `<option value="${field.url.split("/").pop()}">${field.label}  </option>`)
                        .join("");

                    $(fieldSelect.querySelectorAll("option")).attr("selected", "selected");
                    // update viewId and view title
                    $(viewIdInput).val("all" + formId.replace("_", "").replace("-", ""));
                    $(viewTitleInput).val(form.label);
                }
            });
        });
        // select the first form
        $(formSelect.querySelector("option:first-child")).attr("selected", "selected");
        $(formSelect).change();

        this.$createCustomViewDialog.modal({
            show: true,
            backdrop: false,
        });
        this.addCustomView$.subscribe(() => {
            const formData = new FormData();
            formData.append("_authenticator", this.getCSRFToken());
            Array.from(this.createCustomViewDialog.querySelectorAll("[data-key]")).forEach(
                (input: HTMLInputElement) => {
                    formData.append(input.dataset.key, $(input).val());
                }
            );
            this.http
                .postWithOptions(
                    `${this.dbService.getDBLink()}/${$(formSelect).val()}/manage_generateView`,
                    formData,
                    {}
                )
                .subscribe((response: Response) => {
                    const resp = response.json();
                    console.log(resp);
                    if (!resp.success) {
                        $(error).attr("display", "block");
                        error.innerHTML = `<span>${resp.message}</span>`;
                        return;
                    }
                    this.treeService.updateTree().then(() => {
                        const callCallback = () => {
                            if (callback !== null) {
                                callback(`${this.dbService.getDBLink()}/${$(formSelect).val()}/${resp.id}`, resp.title);
                            }
                        };

                        if (callbackBeforeOpeningTab) {
                            callCallback();
                        }

                        this.tabsManagerService.openTab({
                            editor: "view",
                            label: resp.title,
                            url: `${this.dbService.getDBLink()}/${$(formSelect).val()}/${resp.id}`,
                            id: resp.id,
                        });

                        if (!callbackBeforeOpeningTab) {
                            setTimeout(() => callCallback(), 100);
                        }
                        this.$createCustomViewDialog.modal("hide");
                    });
                });
        });
    }

    getCSRFToken() {
        const authenticator = document.getElementsByName("_authenticator");
        const token = (<HTMLInputElement>authenticator[0]).value;
        return token;
    }

    setupCreateCustomViewDialog() {
        const self = this;
        self.createCustomViewDialog = <HTMLDialogElement>document.querySelector("#new-view-dialog");
        self.$createCustomViewDialog = $(self.createCustomViewDialog);

        Array.from(self.createCustomViewDialog.querySelectorAll('input[type="text"], select')).forEach(
            (input: HTMLInputElement | HTMLSelectElement) => {
                $(input).keyup(evd => {
                    if (evd.keyCode === 13) {
                        self.addCustomView.next();
                    }
                });
            }
        );

        Array.from(self.createCustomViewDialog.querySelectorAll("button")).forEach((btn: HTMLElement) => {
            $(btn)
                .unbind("click")
                .bind("click", evt => {
                    if (btn.classList.contains("new-view-dialog__create-btn")) {
                        self.addCustomView.next();
                    } else self.$createCustomViewDialog.modal("hide");
                });
        });
        const error = self.createCustomViewDialog.querySelector("span.mdl-dialog__error");
        $(error).attr("display", "none");
    }

    createViewSaveProcess(viewURL: string, formData: FakeFormData = null) {
        viewURL = viewURL.replace(/^(.+?)\/?$/, "$1");

        if (formData === null) {
            const $form = $('form[action="' + viewURL + '/@@edit"]');

            if (!$form.length) {
                return null;
            }

            formData = new FakeFormData(<HTMLFormElement>$form.get(0));
            formData.set("form.buttons.save", "Save");
        }

        const process = new PlominoViewSaveProcess({
            immediately: false,
            formURL: viewURL,
            formData: formData,
            labelsRegistryLink: this.labelsRegistry,
            httpServiceLink: this.http,
            activeEditorServiceLink: this.activeEditorService,
            widgetServiceLink: this.widgetService,
            objServiceLink: this.objService,
            tabsManagerServiceLink: this.tabsManagerService,
        });

        return process;
    }

    createFormSaveProcess(formURL: string, formData: FakeFormData = null) {
        formURL = formURL.replace(/^(.+?)\/?$/, "$1");

        if (formData === null) {
            const $form = $('form[action="' + formURL + '/@@edit"]');

            if (!$form.length) {
                return null;
            }

            formData = new FakeFormData(<HTMLFormElement>$form.get(0));
            formData.set("form.buttons.save", "Save");
            formData.set("form.widgets.form_layout", this.contentManager.getContent(formURL));
        }

        const process = new PlominoFormSaveProcess({
            immediately: false,
            formURL: formURL,
            formData: formData,
            labelsRegistryLink: this.labelsRegistry,
            httpServiceLink: this.http,
            activeEditorServiceLink: this.activeEditorService,
            widgetServiceLink: this.widgetService,
            objServiceLink: this.objService,
            tabsManagerServiceLink: this.tabsManagerService,
        });

        return process;
    }

    enqueueNewFormSaveProcess(formURL: string) {
        const process = this.createFormSaveProcess(formURL);
        if (process === null) {
            this.log.error("cannot create save process for formURL", formURL);
        } else {
            this.saveStack.unshift(process.start());
        }
    }

    detectNewIFrameInnerClick(ev: MouseEvent) {
        return this.onOutsideClick((<any>$).event.fix(ev), true);
    }

    detectNewFormSave() {
        this.currentFormIsUnsaved = false;
        this.cleanOutsideArea();
    }

    private listenDocumentClicks() {
        $("body").delegate("*", "mousedown", $event => {
            const isFormClick = Boolean($($event.currentTarget).closest("form:visible[data-pat-autotoc]").length);
            $event.stopPropagation();
            if (!isFormClick) {
                this.onOutsideClick($event, false).then(
                    () => {},
                    () => {}
                );
            }
        });
    }

    private listenFormInnerChangeProcesses() {
        $("body").delegate('form[id!="plomino_form"]', "keydown input change paste", $event => {
            const isFormInnerEvent = $($event.currentTarget).is("form:visible[data-pat-autotoc]");
            const isFieldTypeChange = $event.target.id === "form-widgets-field_type";
            $event.stopPropagation();
            if (
                !isFieldTypeChange &&
                isFormInnerEvent &&
                !($event.type === "keydown" && $event.keyCode === 9) &&
                !this.currentFormIsUnsaved
            ) {
                this.currentFormIsUnsaved = true;
                this.hackOutsideArea();
            }
        });
    }

    private hackOutsideArea() {
        /* ngx-bootstrap tab switch */
        const $tabset = $("div.main-app.panel > plomino-tabs");
        const $tsb = $('<div id="tab-switch-block"></div>');

        $tsb.css({
            background: "transparent",
            height: "50px",
            position: "absolute",
            "z-index": 99999,
            width: "100%",
            top: 0,
            left: 0,
        });

        $tabset.prepend($tsb);

        /* palette tab change */
        const $tabset2 = $("plomino-palette > div > div.mdl-tabs__tab-bar");
        const $tsb2 = $('<div id="tab-switch-block-2"></div>');

        $tsb2.css({
            background: "transparent",
            height: "60px",
            position: "absolute",
            "z-index": 99999,
            width: "100%",
            top: 0,
            left: 0,
        });

        $tabset2.prepend($tsb2);

        /* tree field click */
        const $treeWrapperView = $("div.tree-wrapper > div > plomino-tree > div");
        const $tsb3 = $('<div id="tree-switch-block"></div>');

        $tsb3.css({
            background: "transparent",
            height: "100%",
            position: "absolute",
            // 'z-index': 99999,
            width: "100%",
            top: "20px",
            left: 0,
        });

        $treeWrapperView.prepend($tsb3);
    }

    private cleanOutsideArea() {
        $("#tab-switch-block,#tab-switch-block-2,#tree-switch-block").remove();
    }

    private onOutsideClick($event: JQueryEventObject, iframe: boolean): Promise<any> {
        /* here is outside click - check that form is changed or not */

        return new Promise((resolve, reject) => {
            const showUnsavedConfirmDialog = () => {
                return this.elementService.awaitForConfirm({
                    dialogTitle: "Discard changes?",
                    text:
                        "You have selected another field but the current field has unsaved changes. Would you like to discard the changes?",
                    confirmBtnText: "Discard changes",
                    cancelBtnText: "Continue editing",
                    dialogWidth: "500px",
                });
            };

            const resolveAndConfirm = (_iframe: boolean) => {
                this.currentFormIsUnsaved = false;
                this.cleanOutsideArea();
                if (!iframe) {
                    try {
                        const elementFromPoint = <HTMLElement>document.elementFromPoint($event.pageX, $event.pageY);
                        elementFromPoint.click();
                    } catch (e) {}
                }
                resolve();
            };

            const $currentTarget = $($event.currentTarget);

            if (!this.currentFormIsUnsaved) {
                resolve();
            } else if (iframe || $currentTarget.is("#tab-switch-block, #tab-switch-block-2, #tree-switch-block")) {
                showUnsavedConfirmDialog()
                    .then(() => resolveAndConfirm(iframe))
                    .catch(() => reject("cancelled"));
            }
        });

        /**
         * 1. check that current form has got some edit processes
         * 2. if true -> in all touch points prevent it before confirmation
         * 3. on confirmation -> throw event
         *
         * touch points:
         * 1. iframe inner mousedown
         * - prevent test: OK
         * 2. ngx-bootstrap tab switch
         * - prevent test: can't be prevented, hack - create up transparent div, OK
         * 3. palette tab change
         * - prevent test: can't be prevented, hack - create up transparent div, OK
         * 4. tree field click
         * - prevent test: can't be prevented, hack - create up transparent div, OK
         */
    }
}

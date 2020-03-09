import { PlominoTabsManagerService } from "./../tabs-manager/index";
import { ObjService } from "./../obj.service";
import { FakeFormData } from "./../../utility/fd-helper/fd-helper";
import { WidgetService } from "./../widget.service";
import { PlominoActiveEditorService } from "./../active-editor.service";
import { PlominoHTTPAPIService } from "./../http-api.service";
import { LabelsRegistryService } from "./../../editors/tiny-mce/services/labels-registry.service";
import { Observable, Observer } from "rxjs/Rx";
import { Response } from "@angular/http";
import { updateRelatedSubformsAfterFormSave } from "./subform-update.helper";

/**
 * the process divided on the parts:
 * 1. build layout
 * 2. save the form
 * 3. return Observable of html (content) and url
 */
export class PlominoFormSaveProcess {
    /**
     * the process id
     */
    protected id: number;

    /**
     * is the process started
     */
    protected started = false;

    /**
     * is the process prevented
     */
    protected prevented = false;

    /**
     * the FormData js-object from form-settings html form
     */
    protected savingFormData: FakeFormData;

    /**
     * the form layout
     */
    private $layout: JQuery;

    /**
     * the form url before save
     */
    protected originalFormURL: string;

    /**
     * the form url after save
     */
    protected nextFormURL: string;

    /**
     * the form id before save
     */
    protected originalFormID: string;

    /**
     * the form id after save
     */
    protected nextFormID: string;

    /**
     * the promise object of the process
     */
    protected finishPromise: Promise<any>;
    protected broadcastFinish: (value?: {} | PromiseLike<{}>) => void;
    protected broadcastReject: (reason: any) => void;

    /**
     * link to LabelsRegistryService instance
     */
    protected labelsRegistry: LabelsRegistryService;

    /**
     * link to PlominoHTTPAPIService instance
     */
    protected http: PlominoHTTPAPIService;

    /**
     * link to PlominoActiveEditorService instance
     */
    protected activeEditorService: PlominoActiveEditorService;

    /**
     * link to WidgetService instance
     */
    protected widgetService: WidgetService;

    /**
     * link to ObjService instance
     */
    protected objService: ObjService;

    /**
     * link to PlominoTabsManagerService instance
     */
    protected tabsManagerService: PlominoTabsManagerService;

    constructor(options: PlominoFormSaveProcessOptions) {
        this.setup(options);
    }

    protected setup(options: PlominoFormSaveProcessOptions) {
        this.savingFormData = options.formData;
        this.originalFormURL = options.formURL;
        this.labelsRegistry = options.labelsRegistryLink;
        this.http = options.httpServiceLink;
        this.activeEditorService = options.activeEditorServiceLink;
        this.widgetService = options.widgetServiceLink;
        this.objService = options.objServiceLink;
        this.tabsManagerService = options.tabsManagerServiceLink;

        this.nextFormID = this.savingFormData.get("form.widgets.IShortName.id");
        this.originalFormID = this.originalFormURL.split("/").pop();

        this.id = Math.floor(Math.random() * 1e10 + 1e10);
        const layoutContent: string = this.savingFormData
            .get("form.widgets.form_layout")
            .replace(/\r/g, "")
            .replace(/\xa0/g, " "); // remove UTF-8 and WIN-1251 artefacts

        this.$layout = $(`<div id="tmp-layout-${this.id}" style="display: none">${layoutContent}</div>`);

        this.finishPromise = new Promise((resolve, reject) => {
            this.broadcastFinish = resolve;
            this.broadcastReject = reject;
        });

        if (options.immediately) {
            this.start();
        }
    }

    start() {
        if (this.started) {
            return;
        }
        if (this.prevented) {
            return;
        }
        this.started = true;

        $("body").append(this.$layout);

        return this.buildLayout().flatMap(() => this.submitFormData());
    }

    processFinished(): Promise<any> {
        return this.finishPromise;
    }

    prevent(): void {
        if (this.prevented) {
            return;
        }
        this.prevented = true;
        this.broadcastReject("prevented");
    }

    isStarted(): boolean {
        return this.started;
    }

    isWorking(): boolean {
        return this.started && !this.prevented;
    }

    protected detectPrevention(observer: Observer<any>) {
        if (!this.isWorking()) {
            observer.error("prevented");
        }
    }

    private buildLayout() {
        if (!this.isWorking()) {
            return;
        }

        return this.buildHideWhensAndCachesOnLayout()
            .flatMap(() => this.buildLabelsOnLayout())
            .flatMap(() => this.buildOtherPlominoElementsOnLayout())
            .flatMap(() => this.fixBrokenLabelsOnLayout())
            .flatMap(() => this.removeGarbageOnLayout());
    }

    private buildHideWhensAndCachesOnLayout(): Observable<boolean> {
        return Observable.create((observer: Observer<boolean>) => {
            this.detectPrevention(observer);
            this.$layout.find(".plominoHidewhenClass,.plominoCacheClass").each(function() {
                const $element = $(this);
                const position = $element.attr("data-plomino-position");
                const hwid = $element.attr("data-plominoid");

                if (position && hwid) {
                    $element.text(`${position}:${hwid}`);
                }

                $element
                    .removeAttr("data-plominoid")
                    .removeAttr("data-present-method")
                    .removeAttr("data-plomino-position");

                if (position === "end" && $element.next().length && $element.next().prop("tagName") === "BR") {
                    $element.next().remove();
                }
            });

            observer.next(true);
            observer.complete();
        });
    }

    private buildLabelsOnLayout(): Observable<boolean> {
        if (!this.isWorking()) {
            return Observable.of(true);
        }
        return Observable.of(true)
            .flatMap(() => {
                this.$layout.find("span.mceEditable").each((i, mceEditable) => {
                    const $mceEditable = $(mceEditable);
                    if (
                        $mceEditable
                            .children()
                            .last()
                            .prop("tagName") === "BR"
                    ) {
                        $mceEditable
                            .children()
                            .last()
                            .remove();
                        $mceEditable.replaceWith(`<p>${$mceEditable.html()}</p>`);
                    }
                });

                const labels$: Observable<string>[] = [];
                const context = this;

                this.$layout.find(".plominoLabelClass").each(function() {
                    const $element = $(this);
                    const tag = $element.prop("tagName");
                    const id = $element.attr("data-plominoid");
                    const theLabelIsAdvanced = Boolean($element.attr("data-advanced"));

                    if (id && !theLabelIsAdvanced) {
                        /**
                         * the label is not advanced - save its field title
                         */

                        /* current element (label) text */
                        const title = $element.html();
                        const labelURL = `${context.originalFormURL}/${id}`;
                        const relatedFieldTitle = context.labelsRegistry.get(labelURL, "title");
                        const relatedFieldTemporaryTitle = context.labelsRegistry.get(labelURL);

                        if (relatedFieldTemporaryTitle !== relatedFieldTitle) {
                            /**
                             * save the field title
                             */
                            labels$.push(
                                <Observable<string>>context.http.patch(labelURL, { title: relatedFieldTemporaryTitle })
                            );
                            $element.html(relatedFieldTemporaryTitle);
                        }
                    }

                    if (tag === "SPAN") {
                        $element
                            .removeAttr("data-plominoid")
                            .html(theLabelIsAdvanced ? `${id}:${$element.html().trim()}` : id);
                    }

                    if (tag === "DIV") {
                        const html = $element
                            .find(".plominoLabelContent")
                            .html()
                            .replace(/<.?p.?>/g, " ");
                        $(this).replaceWith(`<span class="plominoLabelClass">${id}:${html}</span>`);
                    }
                });

                return labels$.length ? Observable.forkJoin(labels$) : Observable.of([""]);
            })
            .map(() => true);
    }

    private buildOtherPlominoElementsOnLayout(): Observable<boolean> {
        return Observable.create((observer: Observer<boolean>) => {
            this.detectPrevention(observer);

            this.$layout.find("*[data-plominoid]").each(function() {
                const $element = $(this).removeClass("mceNonEditable");
                const id = $element.attr("data-plominoid");
                $(this).replaceWith(`<span class="${$element.attr("class")}">${id}</span>`);
            });

            observer.next(true);
            observer.complete();
        });
    }

    private fixBrokenLabelsOnLayout(): Observable<boolean> {
        return Observable.create((observer: Observer<boolean>) => {
            this.detectPrevention(observer);

            const $errLabels = this.$layout.find('.plominoLabelClass:contains(":") > .plominoLabelClass');

            $errLabels.each((i, errLabel) => {
                const $errLabel = $(errLabel);
                $errLabel.parent().html($errLabel.html());
            });

            observer.next(true);
            observer.complete();
        });
    }

    private removeGarbageOnLayout(): Observable<boolean> {
        return Observable.create((observer: Observer<boolean>) => {
            this.detectPrevention(observer);

            this.$layout
                .find(
                    ".mceNonEditable,.mceEditable,.plominoFieldClass--selected," +
                        ".plominoLabelClass--selected, [data-event-unique], .drag-autopreview"
                )
                .removeClass("mceNonEditable")
                .removeClass("mceEditable")
                .removeClass("plominoFieldClass--selected")
                .removeClass("drag-autopreview")
                .removeAttr("data-event-unique")
                .removeClass("plominoLabelClass--selected");

            observer.next(true);
            observer.complete();
        });
    }

    protected submitFormData() {
        const url = `${this.originalFormURL}/@@edit`;
        this.savingFormData.set("form.widgets.form_layout", this.$layout.html());
        this.$layout.remove(); // flush memory
        return this.http
            .postWithOptions(url, this.savingFormData.build(), {})
            .map((data: Response) => {
                this.nextFormURL = data.url
                    .split("/")
                    .slice(0, -2)
                    .join("/");
                const nextFormURLAfterPloneUpdate = data.url
                    .split("/")
                    .slice(0, -1)
                    .join("/");
                const dbURL = this.originalFormURL.replace(this.originalFormID, "").replace(/^(.+?)\/$/, "$1");

                if (this.nextFormURL === dbURL || nextFormURLAfterPloneUpdate === dbURL) {
                    this.nextFormURL = this.originalFormURL;
                }

                this.nextFormID = this.nextFormURL.split("/").pop();

                if (this.activeEditorService.editorURL === this.originalFormURL) {
                    this.activeEditorService.setActive(this.nextFormURL);
                }

                return updateRelatedSubformsAfterFormSave(this).map(() => {
                    return {
                        html: data.text(),
                        url: data.url.indexOf("@") !== -1 ? data.url.slice(0, data.url.indexOf("@") - 1) : data.url,
                    };
                });
            })
            .flatMap(saveResult$ => {
                this.broadcastFinish();
                return saveResult$;
            });
    }
}

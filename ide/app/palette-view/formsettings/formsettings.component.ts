import { PlominoTabsManagerService } from "./../../services/tabs-manager/index";
import { PlominoPaletteManagerService } from "./../../services/palette-manager/palette-manager";
import { PlominoSaveManagerService } from "./../../services/save-manager/save-manager.service";
import { LabelsRegistryService } from "./../../editors/tiny-mce/services/labels-registry.service";
import { PlominoActiveEditorService } from "./../../services/active-editor.service";
import {
    Component,
    OnInit,
    ChangeDetectorRef,
    NgZone,
    ViewChild,
    ElementRef,
    ChangeDetectionStrategy,
} from "@angular/core";

import { Observable } from "rxjs/Observable";

import {
    ObjService,
    TabsService,
    TreeService,
    LogService,
    FormsService,
    PlominoElementAdapterService,
    PlominoFormFieldsSelectionService,
} from "../../services";
import { PloneHtmlPipe } from "../../pipes";
import { ElementService } from "../../services/element.service";
import { WidgetService } from "../../services/widget.service";
import { PlominoBlockPreloaderComponent } from "../../utility";

@Component({
    selector: "plomino-palette-formsettings",
    template: require("./formsettings.component.html"),
    styles: [require("./formsettings.component.css")],
    directives: [PlominoBlockPreloaderComponent],
    providers: [],
    pipes: [PloneHtmlPipe],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FormSettingsComponent implements OnInit {
    @ViewChild("formElem") formElem: ElementRef;

    tab: PlominoTab;
    macrosWidgetTimer: number = null;

    // This needs to handle both views and forms
    heading: string;
    formSettings = "";

    /**
     * display block preloader
     */
    loading = false;

    private formLayout = "";

    constructor(
        private objService: ObjService,
        private log: LogService,
        private changeDetector: ChangeDetectorRef,
        private tabsService: TabsService,
        private tabsManagerService: PlominoTabsManagerService,
        private formFieldsSelection: PlominoFormFieldsSelectionService,
        private treeService: TreeService,
        private adapter: PlominoElementAdapterService,
        private labelsRegistry: LabelsRegistryService,
        private activeEditorService: PlominoActiveEditorService,
        private saveManager: PlominoSaveManagerService,
        private zone: NgZone,
        private elementService: ElementService,
        private widgetService: WidgetService,
        private formsService: FormsService,
        private paletteManager: PlominoPaletteManagerService
    ) {
        this.tabsManagerService.getAfterUpdateIdOfTab().subscribe(data => {
            if (this.tab && this.tab.url.split("/").pop() === data.prevId) {
                const prevExp = new RegExp(`^(.+?/)${data.prevId}$`);
                this.tab.url = this.tab.url.replace(prevExp, `$1${data.nextId}`);
            }
        });
    }

    ngOnInit() {
        this.getSettings();

        let onSaveFinishCb: any = null;

        this.formsService.formSettingsSave$.subscribe(data => {
            if (this.tab.url !== data.url) {
                return;
            }

            onSaveFinishCb = data.cb;

            if (this.tab.url === data.url && (this.tab.editor === "view" || this.tab.editor === "code")) {
                this.saveFormSettings(onSaveFinishCb);
            } else {
                this.formsService.getFormContentBeforeSave(data.url);
            }
        });

        this.formsService.onFormContentBeforeSave$.subscribe((data: { id: any; content: any }) => {
            if (this.tab.url !== data.id) return;

            this.saveFormSettings(onSaveFinishCb);
        });
    }

    private hasAuthPermissions() {
        return !(this.formSettings.indexOf("You do not have sufficient privileges to view this page") !== -1);
    }

    saveFormSettings(cb: any) {
        const isViewURL = this.tab.editor === "view";
        this.log.startTimer("save_" + isViewURL ? "view" : "form" + "_hold");
        let newUrl: string;

        const flatMapCallback = ((responseData: { html: string; url: string }) => {
            if (responseData.html !== "<div id='ajax_success'/>") {
                return Observable.of(responseData.html);
            } else {
                // const $oldFormId = this.tab.url.slice(responseData.url.lastIndexOf('/') + 1);
                const $formId = responseData.url.slice(responseData.url.lastIndexOf("/") + 1);
                newUrl = this.tab.url.slice(0, this.tab.url.lastIndexOf("/") + 1) + $formId;
                const oldUrl = this.tab.url;

                if (newUrl && oldUrl && newUrl !== oldUrl) {
                    this.formsService.changeFormId({
                        newId: newUrl,
                        oldId: oldUrl,
                    });

                    this.tabsManagerService.updateTabId(oldUrl.split("/").pop(), $formId);
                    this.changeDetector.markForCheck();
                }

                this.formsService.formSaving = false;
                this.changeDetector.markForCheck();
                return this.objService.getFormSettings(newUrl, true);
            }
        }).bind(this);

        const process = isViewURL
            ? this.saveManager.createViewSaveProcess(this.tab.url)
            : this.saveManager.createFormSaveProcess(this.tab.url);

        this.loading = true;
        this.formsService.latestTinyMCEPatternData = null;
        this.log.info("fst pattern flushed");

        this.log.info(this.tab.url, "loading fst process started...");
        process
            .start()
            .flatMap((responseData: { html: string; url: string }) => flatMapCallback(responseData))
            .map((settingsHTML: string) => {
                this.log.info(this.tab.url, "fst response received...");
                /** get data pattern and store it to window */
                if (settingsHTML && settingsHTML.indexOf("data-pat-tinymce") !== -1) {
                    const data = settingsHTML.match(/data-pat-tinymce="(.+?)"/)[1].replace(/&quot;/g, '"');
                    const formId = newUrl.split("/").pop();
                    this.formsService.newTinyMCEPatternData({ formId, data });
                    this.formsService.latestTinyMCEPatternData = { formId, data };
                    this.log.info(formId, "fst pattern loaded");
                } else {
                    this.log.info("there is no any settingsHTML");
                }
                return settingsHTML;
            })
            .map(this.parseTabs)
            .subscribe(
                (responseHtml: string) => {
                    this.log.info("saveFormSettings");
                    this.log.extra("formsettings.component.ts");

                    this.formSettings = responseHtml;
                    this.updateMacroses();
                    this.loading = false;
                    this.log.stopTimer("save_" + isViewURL ? "view" : "form" + "_hold");
                    this.activeEditorService.turnActiveEditorToLoadingState(false);
                    this.changeDetector.markForCheck();

                    window["materialPromise"].then(() => {
                        componentHandler.upgradeDom();

                        setTimeout(() => {
                            componentHandler.upgradeDom();

                            $(".form-settings-wrapper form").submit(submitEvent => {
                                submitEvent.preventDefault();
                                this.submitForm();
                                return false;
                            });

                            this.loading = false;
                            this.changeDetector.markForCheck();
                            this.changeDetector.detectChanges();
                        }, 400);
                    });

                    if (cb) {
                        cb();
                    }

                    this.treeService.updateTree().then(() => {
                        this.log.info("updateTree() figured out");
                    });
                },
                err => {
                    console.error(err);
                }
            );
    }

    submitForm() {
        this.formsService.saveForm(this.tab.url);
        this.changeDetector.markForCheck();
        this.saveManager.detectNewFormSave();
    }

    saveForm(data: { content: any; cb: any }) {
        this.log.info("saveForm CALLED!");
        // let $form: any = $(this.formElem.nativeElement);
        // let form: HTMLFormElement = $form.find('form').get(0);
        // let formData: any = new FormData(form);

        // this.treeService.updateTree();

        // formData.append('form.buttons.save', 'Save');

        this.saveFormSettings(data.cb);
    }

    cancelForm() {
        this.getSettings();
    }

    openFormCode(tab: any): void {
        const eventData = {
            formUniqueId: tab.formUniqueId,
            editor: "code",
            label: tab.label,
            path: [{ name: tab.label, type: "Forms" }],
            url: tab.url,
        };
        this.log.info("this.tabsService.openTab #frs0001 with showAdd");
        this.formFieldsSelection.selectField("none");
        this.adapter.select(null);
        this.tabsManagerService.openTab({
            id: eventData.url.split("/").pop(),
            url: eventData.url,
            label: eventData.label,
            editor: "code",
        });
    }

    openFormPreview(formUrl: string, tabType: string): void {
        if (tabType === "PlominoForm") {
            ((): Promise<any> => {
                // const anyChanges = tinymce.get(formUrl).isDirty();
                const anyChanges = this.saveManager.isEditorUnsaved(formUrl);

                /* TODO: control sum to check the change is real */

                if (anyChanges) {
                    /**
                     * warn the user of any unsaved changes
                     */
                    return this.elementService.awaitForConfirm({
                        text: "This form has unsaved changes, do you want to show the preview anyway?",
                        confirmBtnText: "Preview",
                        cancelBtnText: "Cancel",
                    });
                }

                return Promise.resolve();
            })()
                .then(() => {
                    window.open(`${formUrl}/OpenForm`);
                })
                .catch(() => null);
        } else {
            window.open(`${formUrl}/view`);
        }
    }

    private deleteForm(tabData: PlominoTab) {
        const tab = this.tab;
        this.elementService
            .awaitForConfirm({
                dialogTitle: "Delete form?",
                text: "This will permanently delete the current form. Do you wish to continue?",
                confirmBtnText: "Delete form",
                cancelBtnText: "Cancel",
            })
            .then(() => {
                const editor = tinymce.get(tabData.url.split("/").pop());
                if (editor && editor.selection) {
                    editor.selection.collapse();
                }
                this.elementService.deleteElement(tabData.url).subscribe(() => {
                    this.tabsManagerService.closeTab({
                        id: tab.url.split("/").pop(),
                        url: tab.url,
                        editor: tab.editor,
                        label: tab.label,
                    });
                    this.tab = null;
                    this.formSettings = "";
                    this.formLayout = "";
                    /* remove all cache */
                    if (this.activeEditorService.editorURL && this.activeEditorService.editorURL === tabData.url) {
                        this.activeEditorService.editorURL = null;
                    }
                    this.labelsRegistry.removeForm(tabData.url);
                    this.formsService.removeForm(tabData.url);
                    this.changeDetector.detectChanges();
                    this.treeService.updateTree();
                    this.changeDetector.markForCheck();
                });
            })
            .catch(() => null);
    }

    private updateMacroses() {
        if (this.formSettings) {
            /** get possible code editor id */
            const codeId = this.tabsManagerService.generateCodeEditorId(this.tab.url);
            /** if tab state is not dirty */
            if (this.tabsManagerService.tabIsNotDirty(codeId)) {
                /** flush the code cache of this form if needed */
                this.tabsManagerService.flushTabContentState(codeId);
                this.log.info("cache of", codeId, "flushed");
            }

            window["MacroWidgetPromise"].then((MacroWidget: any) => {
                if (this.macrosWidgetTimer !== null) {
                    clearTimeout(this.macrosWidgetTimer);
                }

                this.macrosWidgetTimer = <any>setTimeout(() => {
                    // for exclude bugs
                    const $el = $(
                        ".form-settings-wrapper " + "#formfield-form-widgets-IHelpers-helpers > ul.plomino-macros"
                    );
                    if ($el.length) {
                        this.zone.runOutsideAngular(() => {
                            try {
                                new MacroWidget($el);
                            } catch (e) {
                                setTimeout(() => {
                                    const $el = $(
                                        ".form-settings-wrapper " +
                                            "#formfield-form-widgets-IHelpers-helpers > ul.plomino-macros"
                                    );
                                    new MacroWidget($el);
                                }, 100);
                            }
                        });
                    }
                }, 200);
            });

            let formulasSelector = "";
            formulasSelector += "#formfield-form-widgets-document_title";
            formulasSelector += ",#formfield-form-widgets-document_id";
            formulasSelector += ",#formfield-form-widgets-search_formula";
            formulasSelector += ",#fieldset-events";
            setTimeout(() => {
                $(formulasSelector).remove();
                $(".plomino-formula")
                    .parent("div.field")
                    .remove();
                $("#content").css("margin-bottom", 0);
            }, 500);
        }
    }

    private parseTabs(settingsHTML: string): string {
        const $settings = $(`<div>${settingsHTML}</div>`);
        $settings.find("form").prepend(`<div class="mdl-tabs__tab-bar default"></div>`);
        $settings.find("#content").css("margin-bottom", "0");
        $settings.find("form").wrap(`<div class="mdl-tabs mdl-js-tabs default mdl-js-ripple-effect"></div>`);
        $settings
            .find("fieldset")
            .filter((i, element) => {
                return (
                    $(element)
                        .find("legend")
                        .text()
                        .trim() !== "Events"
                );
            })
            .each((i, element) => {
                const $element = $(element);
                $element.css("margin-top", "10px");
                const tabId = Math.floor(Math.random() * 10e10) + 10e10 - 1;
                const $legend = $element.find("legend");
                const legend = $legend.text().trim();

                $settings.find(".mdl-tabs__tab-bar").append(`
          <a href="#fs-tab-${tabId}" style="width: 50%"
            class="mdl-tabs__tab default ${i === 0 ? "is-active" : ""}">
            ${legend}
          </a>
        `);

                $legend.remove();

                $element.replaceWith(`
        <div class="mdl-tabs__panel ${i === 0 ? "is-active" : ""}"
          id="fs-tab-${tabId}">
          ${element.outerHTML}
        </div>
        `);
            });

        return $settings.get(0).outerHTML;
    }

    private getSettings() {
        this.log.warn("getSettings");
        this.log.extra("formsettings.component.ts");
        this.tabsManagerService
            .getActiveTab()
            .map(tabUnit => {
                const tab = tabUnit
                    ? {
                          label: tabUnit.label || tabUnit.id,
                          url: tabUnit.url,
                          editor: tabUnit.editor,
                      }
                    : null;

                if (!(this.tab && tab && !tab.url)) {
                    /**
                     * save previous form settings cache
                     */
                    this.objService.updateFormSettingsCache();

                    this.tab = tab;
                    this.log.info("formsettings -> set tab allowed to", tab);
                } else {
                    this.log.info("formsettings -> set tab prohibited to", tab);
                }

                return tab;
            })
            .flatMap(tab => {
                // this.log.info('tab', tab, tab && tab.url ? tab.url : null);
                // this.log.extra('formsettings.component.ts getSettings -> flatMap');

                if (tab && (tab.editor === "workflow" || tab.editor === "code")) {
                    this.formSettings = "";
                    try {
                        this.changeDetector.markForCheck();
                        this.changeDetector.detectChanges();
                    } catch (e) {}
                    return Observable.of("");
                } else if (tab && tab.url) {
                    this.formSettings = `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
                    componentHandler.upgradeDom();

                    this.formsService.latestTinyMCEPatternData = null;
                    this.log.info("fst pattern flushed");

                    this.log.info(this.tab.url, "loading fst process started...");

                    return this.objService
                        .getFormSettings(tab.url)
                        .map((settingsHTML: string) => {
                            /** get data pattern and store it to window */
                            if (settingsHTML && settingsHTML.indexOf("data-pat-tinymce") !== -1) {
                                const data = settingsHTML.match(/data-pat-tinymce="(.+?)"/)[1].replace(/&quot;/g, '"');
                                if (this.tab === null) {
                                    this.tab = tab;
                                }
                                const formId = this.tab.url.split("/").pop();
                                this.formsService.newTinyMCEPatternData({ formId, data });
                                this.formsService.latestTinyMCEPatternData = { formId, data };
                                this.log.info(formId, "fst pattern loaded");
                            } else {
                                this.log.info("there is no any settingsHTML");
                            }
                            return settingsHTML;
                        })
                        .map(this.parseTabs);
                } else {
                    return Observable.of("");
                }
            })
            .subscribe(template => {
                if (this.tab && template.indexOf(`action="${this.tab.url}/@@edit"`) === -1) {
                    return;
                }

                this.formSettings = template;

                this.updateMacroses();
                this.loading = false;
                try {
                    this.changeDetector.markForCheck();
                    this.changeDetector.detectChanges();
                } catch (e) {}
                window["materialPromise"].then(() => {
                    componentHandler.upgradeDom();
                    this.paletteManager.resizeInnerScrollingContainers();

                    setTimeout(() => {
                        componentHandler.upgradeDom();

                        $(".form-settings-wrapper form").submit(submitEvent => {
                            submitEvent.preventDefault();
                            this.submitForm();
                            return false;
                        });
                    }, 400);
                });
            });
    }
}

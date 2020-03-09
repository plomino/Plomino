import { PlominoTabsManagerService } from "./../../services/tabs-manager/index";
import { TabsService } from "./../../services/tabs.service";
import { PlominoSaveManagerService } from "./../../services/save-manager/save-manager.service";
import { FakeFormData } from "./../../utility/fd-helper/fd-helper";
import { LogService } from "./../../services/log.service";
import { PlominoHTTPAPIService } from "./../../services/http-api.service";
import { Component, ViewChild, ElementRef, ChangeDetectorRef, ChangeDetectionStrategy } from "@angular/core";

import { Headers, Response, RequestOptions } from "@angular/http";

import { Observable } from "rxjs/Rx";
import { ObjService } from "../../services/obj.service";
import { PloneHtmlPipe } from "../../pipes";
import { PlominoBlockPreloaderComponent } from "../../utility";

@Component({
    selector: "plomino-palette-dbsettings",
    template: require("./dbsettings.component.html"),
    styles: [require("./dbsettings.component.css")],
    directives: [PlominoBlockPreloaderComponent],
    providers: [ObjService],
    pipes: [PloneHtmlPipe],
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DBSettingsComponent {
    @ViewChild("dbform") el: ElementRef;

    dbForm = "";
    importExportDialog: HTMLDialogElement;
    aclDialog: HTMLDialogElement;
    okDialog: HTMLDialogElement;
    confirmDialog: HTMLDialogElement;
    userHasDesignPermissions: boolean = null;

    /**
     * display block preloader
     */
    loading = false;

    constructor(
        private objService: ObjService,
        private saveManager: PlominoSaveManagerService,
        private changeDetector: ChangeDetectorRef,
        private http: PlominoHTTPAPIService,
        private tabsService: TabsService,
        private tabsManagerService: PlominoTabsManagerService,
        private log: LogService
    ) {
        this.importExportDialog = <HTMLDialogElement>document.querySelector("#db-import-export-dialog");
        this.aclDialog = <HTMLDialogElement>document.querySelector("#db-acl-dialog");
        this.okDialog = <HTMLDialogElement>document.querySelector("#ok-dialog");
        this.confirmDialog = <HTMLDialogElement>document.querySelector("#confirm-dialog");

        if (!this.importExportDialog.showModal) {
            window["materialPromise"].then(() => {
                dialogPolyfill.registerDialog(this.importExportDialog);
            });
        }

        if (!this.aclDialog.showModal) {
            window["materialPromise"].then(() => {
                dialogPolyfill.registerDialog(this.aclDialog);
            });
        }

        if (!this.confirmDialog.showModal) {
            window["materialPromise"].then(() => {
                dialogPolyfill.registerDialog(this.confirmDialog);
            });
        }

        this.importExportDialog.querySelector(".mdl-dialog__actions button").addEventListener("click", () => {
            this.importExportDialog.close();
        });

        this.aclDialog.querySelector(".mdl-dialog__actions button").addEventListener("click", () => {
            this.aclDialog.close();
        });
    }

    submitForm() {
        // this.el is the div that contains the Edit Form
        // We want to seralize the data in the form, submit it to the form
        // action. If the response is <div class="ajax_success">, we re-fetch
        // the form. Otherwise we update the displayed form with the response
        // (which may have validation failures etc.)
        const form: HTMLFormElement = <HTMLFormElement>$(this.el.nativeElement)
            .find("form")
            .get(0);
        const formData: FormData = new FormData(form);

        formData.append("form.buttons.save", "Save");
        this.loading = true;
        this.saveManager.detectNewFormSave();

        this.objService
            .submitDB(formData)
            .flatMap((responseHtml: string) => {
                if (responseHtml.indexOf("dl.error") > -1) {
                    return Observable.of(responseHtml);
                } else {
                    return this.objService.getDB();
                }
            })
            .subscribe(
                responseHtml => {
                    this.dbForm = responseHtml;

                    setTimeout(() => {
                        $(".db-settings-wrapper form").submit(submitEvent => {
                            submitEvent.preventDefault();
                            this.submitForm();
                            return false;
                        });

                        this.loading = false;
                        this.changeDetector.markForCheck();
                    }, 300);
                    this.changeDetector.markForCheck();
                },
                err => {
                    console.error(err);
                }
            );
    }

    cancelForm() {
        this.getDbSettings();
    }

    ngOnInit() {
        this.getDbSettings();
    }

    awaitForConfirm(question: string): Promise<boolean> {
        this.confirmDialog.querySelector(".mdl-dialog__content").innerHTML = question;
        this.confirmDialog.showModal();
        return new Promise((resolve, reject) => {
            $(this.confirmDialog)
                .find(".close")
                .off("click.confirm")
                .on("click.confirm", () => {
                    reject(false);
                    this.confirmDialog.close();
                });
            $(this.confirmDialog)
                .find(".agree")
                .off("click.confirm")
                .on("click.confirm", () => {
                    resolve(true);
                    this.confirmDialog.close();
                });
        });
    }

    private parseFieldsets(content: string) {
        const $parsedVD = $(content);
        const $importExportPlominoForm = $parsedVD.find("#content .pat-autotoc.autotabs");
        $importExportPlominoForm.find("legend").remove();
        return $importExportPlominoForm.find("fieldset");
    }

    private getDBOptionsLink(link: string) {
        return `${window.location.pathname
            .replace("++resource++Products.CMFPlomino/ide/", "")
            .replace("/index.html", "")}/${link}`;
    }

    private showACL() {
        const contentBlock = this.aclDialog.querySelector(".mdl-dialog__content");
        const accessRightsBlock = contentBlock.querySelector("#acl-access-rights");
        const accessUserRolesBlock = contentBlock.querySelector("#acl-user-roles");
        const accessSpcActionBlock = contentBlock.querySelector("#acl-spc-action-rights");

        const prepareACLContent = () => {
            accessRightsBlock.innerHTML = `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
            accessUserRolesBlock.innerHTML = `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
            accessSpcActionBlock.innerHTML = `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;

            componentHandler.upgradeDom();
        };

        prepareACLContent();

        const updateACLContent = (content: string) => {
            const $fieldSets = this.parseFieldsets(content);
            const accessRightsBlockHTML = $fieldSets.first().html();
            const accessUserRolesBlockHTML = $fieldSets
                .slice(1, 2)
                .first()
                .html();
            const accessSpcActionBlockHTML = $fieldSets.last().html();

            accessRightsBlock.innerHTML = `<p>${accessRightsBlockHTML}</p>`;
            accessUserRolesBlock.innerHTML = `<p>${accessUserRolesBlockHTML}</p>`;
            accessSpcActionBlock.innerHTML = `<p>${accessSpcActionBlockHTML}</p>`;

            $(this.aclDialog)
                .find("form")
                .submit((submitEvent: Event) => {
                    submitEvent.preventDefault();
                    submitEvent.stopPropagation();

                    const form = <HTMLFormElement>submitEvent.currentTarget;
                    const formData = new FormData(form);

                    this.http
                        .postWithOptions(
                            form.action.replace("++resource++Products.CMFPlomino/ide/", ""),
                            formData,
                            new RequestOptions({
                                headers: new Headers({}),
                            })
                        )
                        .subscribe((response: Response) => {
                            const result = response.text();
                            updateACLContent(result);
                        });
                });
        };

        this.aclDialog.showModal();

        this.http.get(this.getDBOptionsLink("DatabaseACL")).subscribe((response: Response) => {
            updateACLContent(response.text());
        });
    }

    private designWorkflow() {
        this.tabsManagerService.openTab({
            id: "workflow",
            url: "workflow",
            label: "Workflow",
            editor: "workflow",
        });
    }

    private showImportExport() {
        const contentBlock = this.importExportDialog.querySelector(".mdl-dialog__content");

        const CSVImportationBlock = contentBlock.querySelector("#csv-importation");
        const JSONImportExportBlock = contentBlock.querySelector("#json-import-export");
        const DesignManageBlock = contentBlock.querySelector("#design-manage");
        const DesignImportExportBlock = contentBlock.querySelector("#design-import-export");

        CSVImportationBlock.innerHTML = `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
        JSONImportExportBlock.innerHTML = `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
        DesignManageBlock.innerHTML = `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;
        DesignImportExportBlock.innerHTML = `<p><div class="mdl-spinner mdl-js-spinner is-active"></div></p>`;

        componentHandler.upgradeDom();
        this.importExportDialog.showModal();

        /**
         * load import/export form
         */
        this.http.get(this.getDBOptionsLink("DatabaseReplication")).subscribe((response: Response) => {
            const $fieldSets = this.parseFieldsets(response.text());
            const CSVImportationBlockHTML = $fieldSets.first().html();
            const JSONImportExportBlockHTML = $fieldSets.last().html();

            CSVImportationBlock.innerHTML = `<p>${CSVImportationBlockHTML}</p>`;
            JSONImportExportBlock.innerHTML = `<p>${JSONImportExportBlockHTML}</p>`;

            $(this.importExportDialog).find(".actionButtons input#import_csv").replaceWith(`
            <input type="hidden" name="import_csv" value="Import">
            <button type="submit"
              class="mdl-button mdl-button-js
                mdl-color-text--white
                mdl-button--raised mdl-color--blue-900">
              Import
            </button>
          `);

            componentHandler.upgradeDom();

            $(this.importExportDialog)
                .find("#csv-importation form, #json-import-export form")
                .submit((submitEvent: Event) => {
                    submitEvent.preventDefault();
                    submitEvent.stopPropagation();

                    const form = <HTMLFormElement>submitEvent.currentTarget;
                    const formData = new FakeFormData(form);

                    if (/^.+?manage_importation$/.test(form.action)) {
                        formData.set("actionType", "import");
                    }

                    this.http
                        .postWithOptions(
                            form.action.replace("++resource++Products.CMFPlomino/ide/", ""),
                            formData.build(),
                            new RequestOptions({
                                headers: new Headers({}),
                            })
                        )
                        .subscribe((response: Response) => {
                            let result = response.text();
                            if (response.url.indexOf("AsJSON") !== -1) {
                                window.URL = window.URL || (<any>window).webkitURL;
                                const jsonString = JSON.stringify(response.json(), undefined, 2);
                                const link = document.createElement("a");
                                link.download = "data.json";
                                const blob = new Blob([jsonString], { type: "text/plain" });
                                link.href = window.URL.createObjectURL(blob);
                                link.click();
                            } else {
                                let start = result.indexOf('<div class="outer-wrapper">');
                                let end = result.indexOf("<!--/outer-wrapper -->");
                                result = result.slice(start, end);
                                start = result.indexOf('<aside id="global_statusmessage">');
                                end = result.indexOf("</aside>");
                                result = result.slice(start, end + "</aside>".length);

                                this.okDialog.querySelector(".mdl-dialog__content").innerHTML = `<p>${$(
                                    result
                                ).text()}</p>`;

                                // this.importExportDialog.close();
                                this.okDialog.showModal();
                            }
                        });
                });

            /**
             * load design settings
             */
            this.http.get(this.getDBOptionsLink("DatabaseDesign")).subscribe((response: Response) => {
                const $fieldSets = this.parseFieldsets(response.text());

                const DesignManageBlockHTML = $fieldSets
                    .slice(1, 2)
                    .first()
                    .html();
                const DesignImportExportBlockHTML = $fieldSets.last().html();

                DesignManageBlock.innerHTML = `<p>${DesignManageBlockHTML}</p>`;
                DesignImportExportBlock.innerHTML = `<p>${DesignImportExportBlockHTML}</p>`;

                $(this.importExportDialog)
                    .find('#design-import-export input[name="submit_refresh_import"]')
                    .remove();

                $(this.importExportDialog)
                    .find("#design-manage a.standalone")
                    .each((i, element: HTMLAnchorElement) => {
                        element.target = "_new";
                        element.href = this.getDBOptionsLink(element.href.replace(/^.*\/(\S+\/\S+)$/i, "$1"));
                    });

                $(this.importExportDialog)
                    .find("#design-manage form, #design-import-export form")
                    .submit((submitEvent: Event) => {
                        const form = <HTMLFormElement>submitEvent.currentTarget;
                        const formData = new FakeFormData(form);
                        let targetFiletype: string = null;
                        let targetFiletypeMime: string = null;

                        // this.log.warn('!!!', form.innerHTML); // submit_import Import

                        if (form.innerHTML.indexOf('value="Import" name="submit_import">') !== -1) {
                            formData.set("submit_import", "Import");
                        }

                        const importDesignFormSubmitted = form.name === "ImportDesign";

                        if (form.action.indexOf("exportDesign") !== -1) {
                            targetFiletype = formData.get("targettype") === "file" ? "json" : "zip";
                            targetFiletypeMime = formData.get("targettype") === "file" ? "text/plain" : "octet/stream";
                        }

                        if (targetFiletypeMime === "octet/stream") {
                            form.action = form.action.replace("++resource++Products.CMFPlomino/ide/", "");
                            form.submit();
                            return true;
                        }

                        submitEvent.preventDefault();
                        submitEvent.stopPropagation();

                        ((): Promise<any> => {
                            if (importDesignFormSubmitted) {
                                const anyChanges = tinymce.editors.some(editor => editor.isDirty());

                                if (anyChanges) {
                                    /**
                                     * warn the user of any unsaved changes
                                     */
                                    return this.awaitForConfirm("Do you agree to undo all unsaved changes?");
                                }
                            }

                            return Promise.resolve();
                        })()
                            .then(() => {
                                /* post started */
                                this.importExportDialog.close();
                                $(document.body).prepend(`
                <div id="application-loader">
                  <div class="sk-cube-grid">
                    <div class="sk-cube sk-cube1"></div>
                    <div class="sk-cube sk-cube2"></div>
                    <div class="sk-cube sk-cube3"></div>
                    <div class="sk-cube sk-cube4"></div>
                    <div class="sk-cube sk-cube5"></div>
                    <div class="sk-cube sk-cube6"></div>
                    <div class="sk-cube sk-cube7"></div>
                    <div class="sk-cube sk-cube8"></div>
                    <div class="sk-cube sk-cube9"></div>
                  </div>
                </div>
              `);
                                this.http
                                    .postWithOptions(
                                        form.action.replace("++resource++Products.CMFPlomino/ide/", ""),
                                        formData.build(),
                                        new RequestOptions({
                                            headers: new Headers({}),
                                        })
                                    )
                                    .subscribe((response: Response) => {
                                        $("#application-loader").remove();
                                        let result = response.text();
                                        if (targetFiletype !== null) {
                                            window.URL = window.URL || (<any>window).webkitURL;
                                            const jsonString = JSON.stringify(response.json(), undefined, 2);
                                            const link = document.createElement("a");
                                            link.download = "data." + targetFiletype;
                                            const blob = new Blob([jsonString], { type: targetFiletypeMime });
                                            link.href = window.URL.createObjectURL(blob);
                                            link.click();
                                        } else {
                                            /** @todo: new plone support */
                                            let start = result.indexOf('<div class="outer-wrapper">');
                                            let end = result.indexOf("<!--/outer-wrapper -->");
                                            result = result.slice(start, end);
                                            start = result.indexOf('<aside id="global_statusmessage">');
                                            end = result.indexOf("</aside>");
                                            result = result.slice(start, end + "</aside>".length);

                                            this.okDialog.querySelector(".mdl-dialog__content").innerHTML = `<p>${$(
                                                result
                                            ).text()}</p>`;

                                            // this.importExportDialog.close();

                                            if (importDesignFormSubmitted) {
                                                window["reloadAccepted"] = true;
                                                window.location.reload();
                                            } else {
                                                this.okDialog.showModal();
                                            }
                                        }
                                    });
                            })
                            .catch(() => null);
                    });
            });
        });
    }

    private hasAuthPermissions() {
        return !(this.dbForm.indexOf("You do not have sufficient privileges to view this page") !== -1);
    }

    private hasDesignPermissions() {
        if (this.userHasDesignPermissions === null) {
            this.userHasDesignPermissions = false;
            this.http.get(this.getDBOptionsLink("DatabaseDesign")).subscribe((response: Response) => {
                this.userHasDesignPermissions = !(
                    response.text().indexOf("You do not have sufficient privileges to view this page") !== -1
                );
                this.changeDetector.markForCheck();
                this.log.info("hasDesignPermissions", this.userHasDesignPermissions);
            });
        }
        return this.userHasDesignPermissions;
    }

    private getDbSettings() {
        this.loading = true;
        this.objService.getDB().subscribe(
            html => {
                this.dbForm = html;

                setTimeout(() => {
                    $(".db-settings-wrapper form").submit(submitEvent => {
                        submitEvent.preventDefault();
                        this.submitForm();
                        return false;
                    });

                    this.loading = false;
                    this.changeDetector.markForCheck();
                }, 300);
                this.changeDetector.markForCheck();
            },
            err => {
                console.error(err);
            }
        );
    }
}

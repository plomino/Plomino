import { PlominoElementAdapterService } from "./element-adapter.service";
import { LogService } from "./log.service";
import { PlominoHTTPAPIService } from "./http-api.service";
import { Injectable } from "@angular/core";

import { Headers, Response, RequestOptions } from "@angular/http";

import { Observable } from "rxjs/Rx";

interface ConfirmationDialogOptions {
    text: string;
    dialogTitle?: string;
    cancelBtnText?: string;
    confirmBtnText?: string;
    dialogWidth?: string;
}

@Injectable()
export class ElementService {
    headers: Headers;
    confirmDialog: HTMLDialogElement;

    constructor(
        private http: PlominoHTTPAPIService,
        private log: LogService,
        private adapter: PlominoElementAdapterService
    ) {
        this.headers = new Headers();
        this.headers.append("Accept", "application/json");
        this.headers.append("Content-Type", "application/json");

        this.confirmDialog = <HTMLDialogElement>document.querySelector("#confirm-dialog");
    }

    awaitForConfirm(options: ConfirmationDialogOptions): Promise<boolean> {
        const dialogTitle = options.dialogTitle ? options.dialogTitle : "Confirm?";
        const confirmButtonText = options.confirmBtnText ? options.confirmBtnText : "Agree";
        const cancelButtonText = options.cancelBtnText ? options.cancelBtnText : "Disagee";
        const dialogWidth = options.dialogWidth ? options.dialogWidth : "280px";

        this.confirmDialog.querySelector(".mdl-dialog__content").innerHTML = options.text;
        this.confirmDialog.querySelector(".mdl-dialog__title").innerHTML = dialogTitle;
        this.confirmDialog.querySelector("button.close").innerHTML = cancelButtonText;
        this.confirmDialog.querySelector("button.agree").innerHTML = confirmButtonText;
        this.confirmDialog.style.width = dialogWidth;
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

    getElement(id: string): Observable<PlominoFieldDataAPIResponse> {
        if (!id) {
            return Observable.of(null);
        }
        // console.warn(console.trace());
        if (id.split("/").pop() === "defaultLabel") {
            return Observable.of(null);
        }
        return this.http
            .getWithOptions(id, { headers: this.headers }, "element.service.ts getElement")
            .map((res: Response) => res.json())
            .catch((err: any) => {
                return Observable.of(null);
            });
    }

    // Had some issues with TinyMCEComponent, had to do this instead of using getElement() method
    // XXX: This should really call the getForm_layout method on the Form object?
    getElementFormLayout(formUrl: string): Observable<PlominoFormDataAPIResponse> {
        // if (this.http.recentlyChangedFormURL !== null
        //   && this.http.recentlyChangedFormURL[0] === formUrl
        //   && $('.tab-name').toArray().map((e) => e.innerText)
        //   .indexOf(formUrl.split('/').pop()) === -1
        // ) {
        //   formUrl = this.http.recentlyChangedFormURL[1];
        //   this.log.info('patched formUrl!', this.http.recentlyChangedFormURL);
        //   this.log.extra('element.service.ts getElementFormLayout');
        // }
        return this.http
            .getWithOptions(formUrl, { headers: this.headers }, "element.service.ts getElementFormLayout")
            .map((res: Response) => {
                this.log.info("response from getElementFormLayout received");
                return res.json();
            });
    }

    getElementCode(url: string) {
        return this.http.get(url, "element.service.ts getElementCode").map((res: Response) => res.text());
    }

    renameGroup(formURL: string, id: string, newId: string, groupContents: string[]) {
        const f = new FormData();
        f.append("id", id);
        f.append("newid", newId);
        f.append("group_contents", JSON.stringify(groupContents));

        return this.http
            .postWithOptions(`${formURL}/rename-group`, f, new RequestOptions({}), "element.service.ts renameGroup")
            .map((res: Response) => res.json());
    }

    postElementCode(url: string, type: string, id: string, code: string) {
        const headers = new Headers();
        headers.append("Content-Type", "application/json");
        return this.http
            .postWithOptions(
                url,
                JSON.stringify({ Type: type, Id: id, Code: code }),
                { headers },
                "element.service.ts postElementCode"
            )
            .map((res: Response) => res.json());
    }

    updateDBSettings(updateObject: any) {
        const url = this.getDBLink();
        return this.http.patch(url, updateObject, "saving workflow");
    }

    getDBLink() {
        return `${window.location.pathname
            .replace("++resource++Products.CMFPlomino/ide/", "")
            .replace("/index.html", "")}`;
    }

    patchElement(id: string, element: any) {
        return this.http.patch(id, element, "element.service.ts patchElement");
    }

    // XXX: Docs for debugging:
    // http://plonerestapi.readthedocs.io/en/latest/content.html#creating-a-resource-with-post

    postElement(url: string, newElement: InsertFieldEvent): Observable<AddFieldResponse> {
        const headers = new Headers();
        headers.append("Content-Type", "application/json");
        if (newElement["@type"] == "PlominoField") {
            url = url + "/@@add-field";
            headers.append("Accept", "*/*");
        } else {
            headers.append("Accept", "application/json");
        }

        // A form must have an empty layout
        if (newElement["@type"] == "PlominoForm") {
            newElement.form_layout = "";
        }

        return this.http
            .postWithOptions(url, JSON.stringify(newElement), { headers }, "element.service.ts postElement")
            .map((res: Response) => res.json());
    }

    deleteElement(url: string) {
        return this.http.delete(url, "element.service.ts deleteElement");
    }

    searchElement(query: string) {
        return this.http
            .getWithOptions(
                "../../search?SearchableText=" + query + "*",
                { headers: this.headers },
                "element.service.ts searchElement"
            )
            .map((res: Response) => res.json());
    }

    getWidget(base: string, type: string, id: string, newTitle?: string): Observable<string> {
        this.log.info("type", type, "id", id, "newTitle", newTitle);
        this.log.extra("element.service.ts getWidget");
        if (type === "label") {
            return Observable.of(
                this.adapter.endPoint(
                    "label",
                    `<span class="plominoLabelClass mceNonEditable"
          ${id ? `data-plominoid="${id}"` : ""}>${newTitle || "Untitled"}</span>`
                )
            );
        }
        return this.http
            .post(
                `${base}/@@tinyform/example_widget`,
                JSON.stringify({ widget_type: type, id: id ? id : "" }),
                "element.service.ts getWidget"
            )
            .map((response: any) => response.json());
    }
}

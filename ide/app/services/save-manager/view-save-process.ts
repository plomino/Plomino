import { PlominoFormSaveProcess } from "./form-save-process";
import { Response } from "@angular/http";

export class PlominoViewSaveProcess extends PlominoFormSaveProcess {
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

        return this.submitFormData();
    }

    protected submitFormData() {
        const url = `${this.originalFormURL}/@@edit`;

        return this.http.postWithOptions(url, this.savingFormData.build(), {}).map((data: Response) => {
            this.nextFormURL = data.url
                .split("/")
                .slice(0, -2)
                .join("/");
            const dbURL = this.originalFormURL.replace(this.originalFormID, "").replace(/^(.+?)\/$/, "$1");

            if (this.nextFormURL === dbURL) {
                this.nextFormURL = this.originalFormURL;
            }

            this.nextFormID = this.nextFormURL.split("/").pop();

            if (this.activeEditorService.editorURL === this.originalFormURL) {
                this.activeEditorService.setActive(this.nextFormURL);
            }

            this.broadcastFinish();

            return {
                html: data.text(),
                url: data.url.indexOf("@") !== -1 ? data.url.slice(0, data.url.indexOf("@") - 1) : data.url,
            };
        });
    }
}

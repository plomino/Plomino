import { LogService } from "./log.service";
import { PlominoHTTPAPIService } from "./http-api.service";
import { WidgetService } from "./widget.service";
import { Injectable } from "@angular/core";
import { Response } from "@angular/http";
import { Observable, Subject } from "rxjs/Rx";

@Injectable()
export class TemplatesService {
    $insertion: Subject<InsertTemplateEvent> = new Subject<InsertTemplateEvent>();
    templatesRegistry = {};
    templatesCache: PlominoFormGroupTemplate[] = null;

    constructor(private http: PlominoHTTPAPIService, private widgetService: WidgetService, private log: LogService) {}

    addTemplate(formUrl: string, templateId: string): Observable<any> {
        return templateId
            ? this.http
                  .get(`${formUrl}/add-template?id=${templateId}`, "templates.service.ts addTemplate")
                  .map(this.extractData)
            : Observable.of("");
    }

    fixCustomTemplate(template: PlominoFormGroupTemplate) {
        /**
         * this code fixing custom templates and removing groups from them
         */
        const $layout = $(`<div>${template.layout}</div>`);
        $layout.find("[data-groupid]").each((i, divGroup) => {
            const $divGroup = $(divGroup);
            $divGroup.replaceWith($divGroup.html());
        });

        $layout.find("span.mceEditable").each((i, mceEditable) => {
            const $mceEditable = $(mceEditable);
            $mceEditable.replaceWith($mceEditable.html());
        });

        // $layout.find('input,textarea,button')
        //   .removeAttr('name').removeAttr('id');

        template.layout = $layout.html();

        // template.group_contents = template.group_contents.map((groupContent) => {
        //   const $contentLayout = $(`<div>${groupContent.layout}</div>`);
        //   $contentLayout.find('input,textarea,button')
        //     .removeAttr('name').removeAttr('id');
        //   groupContent.layout = $contentLayout.html();
        //   return groupContent;
        // });

        return template;
    }

    fixBuildedTemplate(templateHTML: string) {
        const $result = $(templateHTML);
        $result.find(".plominoLabelClass").each((i, pLabel) => {
            const $pLabel = $(pLabel);
            const $pLabelParent = $pLabel.parent();

            // $pLabelParent.attr('contenteditable', 'false');
            $pLabelParent.removeAttr("contenteditable");

            if (
                $pLabelParent.hasClass("mceEditable") &&
                $pLabel.next().length &&
                $pLabel.next().prop("tagName") === "BR" &&
                $pLabelParent.next().length &&
                $pLabelParent.next().prop("tagName") === "BR"
            ) {
                $pLabelParent.next().remove();
            }
        });

        return $result.get(0).outerHTML;
    }

    buildTemplate(formUrl: string, template: PlominoFormGroupTemplate): void {
        if (!this.templatesRegistry.hasOwnProperty(formUrl)) {
            this.templatesRegistry[formUrl] = {};
        }

        template = this.fixCustomTemplate(template);

        this.widgetService.loadAndParseTemplatesLayout(formUrl, template).subscribe((result: string) => {
            const $result = $(result);
            $result.addClass("drag-autopreview");
            $result
                .find("input,textarea,button")
                .removeAttr("name")
                .removeAttr("id");
            $result
                .find("span")
                .removeAttr("data-plominoid")
                .removeAttr("data-mce-resize");
            $result.removeAttr("data-groupid");

            this.templatesRegistry[formUrl][template.id] = this.fixBuildedTemplate($result.get(0).outerHTML);
        });
    }

    getTemplate(formUrl: string, templateId: string, subform?: boolean): Observable<string> {
        if (!this.templatesRegistry.hasOwnProperty(formUrl)) {
            this.templatesRegistry[formUrl] = {};
        }
        if (this.templatesRegistry[formUrl][templateId]) {
            return Observable.of(this.templatesRegistry[formUrl][templateId]);
        } else if (subform) {
            return this.widgetService.getWidget(formUrl, "subform", templateId).map((result: string) => {
                const $result = $(`<div>${result}</div>`);
                $result.addClass("drag-autopreview");
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

                this.templatesRegistry[formUrl][templateId] = this.fixBuildedTemplate($result.get(0).outerHTML);

                return $result.get(0).outerHTML;
            });
        }
        return Observable.of(
            this.templatesRegistry[formUrl][templateId]
                ? this.templatesRegistry[formUrl][templateId]
                : `<div class="drag-autopreview plominoGroupClass mceNonEditable"
        contenteditable="false">
        <span class="mceEditable" contenteditable="false">
          <span class="plominoLabelClass mceNonEditable"
            contenteditable="false">
            Untitled
          </span><br>
        </span>
        <span class="plominoFieldClass mceNonEditable"
          data-present-method="convertFormFields_1"
          contenteditable="false"> <input type="text"> 
        </span>
      </div>
    `
        );
    }

    getTemplates(formUrl: string, formEditor: string): Observable<any> {
        if (this.templatesCache !== null && formEditor === "layout") {
            this.http
                .get(`${formUrl}/@@list-templates`, "templates.service.ts getTemplates lazy")
                .map(this.extractData)
                .subscribe(data => {
                    if (data && data.length) {
                        this.templatesCache = data;
                    }
                });
            return Observable.of(this.templatesCache);
        }

        return this.http
            .get(`${formUrl}/@@list-templates`, "templates.service.ts getTemplates")
            .map(this.extractData)
            .map(data => {
                if (data && data.length && formEditor === "layout") {
                    this.templatesCache = data;
                }
                return data;
            });
    }

    insertTemplate(templateData: InsertTemplateEvent): void {
        this.$insertion.next(templateData);
    }

    getInsertion(): Observable<InsertTemplateEvent> {
        return this.$insertion.asObservable();
    }

    private extractData(response: Response) {
        if (response.text().indexOf("You do not have sufficient privileges to view this page") !== -1) {
            return [];
        }

        return response.json();
    }
}

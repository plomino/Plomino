import { LogService } from "./../../../services/log.service";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs/Rx";
import { ElementService } from "../../../services";

@Injectable()
export class UpdateFieldService {
    constructor(private elementService: ElementService, private log: LogService) {}

    /**
     * this function calling in map case, for each element selected
     * by *[data-plominoid="OLD_ID"] while field updating
     *
     * calling from tiny-mce.component.ts updateField method
     */
    updateField(item: PlominoUpdatingItemData): Observable<PlominoLayoutElementReplaceData> {
        if (item.type === "Hidewhen") {
            const result = Object.assign(
                {},
                {
                    newTemplate: this.wrapHidewhen2(item.type, item.newId, item.oldTemplate),
                    item: item,
                },
                {
                    oldTemplate: item.oldTemplate,
                }
            );

            return Observable.of(result);
        }

        // TODO: Replace assign with passing data through operators in sequence
        // tiny-mce.component.ts 307 -> 323

        /**
         * @param {string} itemTemplate - element's new html-source string, coming from server
         */
        const elLayoutCallback = (itemTemplate: string): PlominoLayoutElementReplaceData => {
            this.log.info("itemTemplate", itemTemplate);
            this.log.extra("update-field.service.ts elLayoutCallback");

            if (item.type === "Field" || "Action") {
                return Object.assign(
                    {},
                    {
                        newTemplate: this.wrapFieldOrAction(item.type, item.newId, itemTemplate),
                        item: item,
                    },
                    {
                        oldTemplate: item.oldTemplate,
                    }
                );
            } else if (item.type === "Label") {
                return Object.assign(
                    {},
                    {
                        newTemplate: itemTemplate,
                    },
                    {
                        oldTemplate: item.oldTemplate,
                    }
                );
            }
        };

        return this.getElementLayout(item).map(elLayoutCallback);
    }

    private getElementLayout(element: PlominoUpdatingItemData): Observable<string> {
        return element.newTitle
            ? this.elementService.getWidget(element.base, element.type.toLowerCase(), element.newId, element.newTitle)
            : this.elementService.getWidget(element.base, element.type.toLowerCase(), element.newId);
    }

    private wrapElement(elType: string, id: string, content: string) {
        switch (elType) {
            case "plominoField":
            case "plominoAction":
                return this.wrapFieldOrAction(elType, id, content);
            case "plominoHidewhen":
                return this.wrapHidewhen(elType, id, content);
            default:
        }
    }

    private wrapFieldOrAction(elType: string, id: string, contentString: string) {
        const $response = $(contentString);
        const $class = `plomino${elType}Class`;

        let container = "span";
        let content = "";

        // if ($response.is('.plominoLabelClass')) {
        //   const $labelsInside = $response.find('.plominoLabelClass');

        //   // if ($labelsInside.length
        //   //   && $labelsInside.attr('data-plominoid') === $response.attr('data-plominoid')) {
        //   //   $response.replaceWith($labelsInside);
        //   //   contentString = $response.get(0).outerHTML;
        //   // }
        // }

        if ($response.is("div,table,p") || $response.find("div,table,p").length) {
            container = "div";
        }

        if (contentString != undefined) {
            content = `
        <${container} class="${$class} mceNonEditable" 
          data-mce-resize="false" 
          data-plominoid="${id}">
          ${contentString}    
        </${container}>`;
        } else {
            content = `<span class="${$class}">${id}</span>`;
        }

        return content;
    }

    private wrapHidewhen2(elType: string, id: string, contentString: HTMLElement) {
        const $element = $(contentString);
        const $class = $element.attr("class");
        const $position = $element.data("plominoPosition");

        const container = "span";
        const content = `
      <${container} class="${$class}"
        data-present-method="convertFormHidewhens" 
        data-mce-resize="false"
        content-editable="false"
        data-plomino-position="${$position}" 
        data-plominoid="${id}">
        &nbsp;
      </${container}>`;

        return content;
    }

    private wrapHidewhen(elType: string, id: string, contentString: string) {
        const $element = $(contentString);
        const $class = $element.attr("class");
        const $position = $element.text().split(":")[0];
        const $id = $element.text().split(":")[1];

        const container = "span";
        const content = `
      <${container} class="${$class}"
        data-present-method="convertFormHidewhens" 
        data-mce-resize="false"
        content-editable="false"
        data-plomino-position="${$position}" 
        data-plominoid="${$id}">
        &nbsp;
      </${container}>${$position === "start" ? "" : "<br />"}`;

        return content;
    }
}

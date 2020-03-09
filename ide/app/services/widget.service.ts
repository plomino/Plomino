import { LabelsRegistryService } from "./../editors/tiny-mce/services/labels-registry.service";
import { PlominoElementAdapterService } from "./element-adapter.service";
import { LogService } from "./log.service";
import { PlominoHTTPAPIService } from "./http-api.service";
import { Subject, Observable } from "rxjs/Rx";
import { Injectable } from "@angular/core";
import { Response } from "@angular/http";

@Injectable()
export class WidgetService {
    isTemplate = true;

    widgetsCache: {
        [formUrl: string]: {
            [id: string]: {
                [widget_type: string]: string;
            };
        };
    } = {};

    zombiesInformation: {
        [formUrl: string]: {
            [id: string]: {
                [widget_type: string]: boolean;
            };
        };
    } = {};

    constructor(
        private http: PlominoHTTPAPIService,
        private adapter: PlominoElementAdapterService,
        private labelsRegistry: LabelsRegistryService,
        private log: LogService
    ) {}

    getWidgetCacheData(formUrl: string, widgetType: string, id: string): string {
        if (!this.widgetsCache.hasOwnProperty(formUrl)) {
            return null;
        }

        if (!this.widgetsCache[formUrl].hasOwnProperty(id)) {
            return null;
        }

        if (!this.widgetsCache[formUrl][id].hasOwnProperty(widgetType)) {
            return null;
        }

        return this.widgetsCache[formUrl][id][widgetType];
    }

    detectZombie(formUrl: string, widgetType: string, id: string) {
        if (!this.zombiesInformation.hasOwnProperty(formUrl)) {
            this.zombiesInformation[formUrl] = {};
        }
        if (!this.zombiesInformation[formUrl].hasOwnProperty(id)) {
            this.zombiesInformation[formUrl][id] = {};
        }

        this.zombiesInformation[formUrl][id][widgetType] = true;
        this.log.warn("zombie detected", id, widgetType);
    }

    isItAZombie(formUrl: string, widgetType: string, id: string): boolean {
        if (!this.zombiesInformation.hasOwnProperty(formUrl)) {
            return false;
        }

        if (!this.zombiesInformation[formUrl].hasOwnProperty(id)) {
            return false;
        }

        if (!this.zombiesInformation[formUrl][id].hasOwnProperty(widgetType)) {
            return false;
        }

        return this.zombiesInformation[formUrl][id][widgetType];
    }

    setWidgetCacheData(formUrl: string, widgetType: string, id: string, data: string) {
        if (!this.widgetsCache.hasOwnProperty(formUrl)) {
            this.widgetsCache[formUrl] = {};
        }
        if (!this.widgetsCache[formUrl].hasOwnProperty(id)) {
            this.widgetsCache[formUrl][id] = {};
        }

        this.widgetsCache[formUrl][id][widgetType] = data;
    }

    getGroupLayout(baseUrl: string, input: PlominoFormGroupTemplate, templateMode?: boolean): Observable<string> {
        // this.log.info('getGroupLayout');
        // this.log.extra('widget.service.ts getGroupLayout');
        /**
         * decided to use the DOM
         */
        let $groupLayout = $(
            `<div id="tmp-group-layout-id${input.id}" role="group"
        style="visibility: hidden; position: absolute;top:0;left:0"
        >${input.layout}</div>`
        );

        $("body").append($groupLayout);
        $groupLayout = $(`#tmp-group-layout-id${input.id}`);

        const $elements = $groupLayout.find(
            ".plominoFieldClass, .plominoHidewhenClass, " +
                ".plominoActionClass, .plominoLabelClass, .plominoSubformClass"
        );
        const resultingElementsString = "";
        const contents = input.group_contents;
        const items$: PlominoIteratingLayoutElement[] = [];

        $elements.each((index: number, element: HTMLElement) => {
            const $element = $(element);
            let itemPromiseResolve: (value?: {} | PromiseLike<{}>) => void;
            const itemPromise = new Promise((resolve, reject) => {
                itemPromiseResolve = resolve;
            });

            switch ($element.attr("class")) {
                case "plominoFieldClass":
                case "plominoActionClass":
                    items$.push({
                        type: "field",
                        contents: contents,
                        baseUrl: baseUrl,
                        el: $element,
                        templateMode: Boolean(templateMode),
                        itemPromise,
                        itemPromiseResolve,
                    });
                    break;
                case "plominoHidewhenClass":
                    items$.push({
                        type: "hidewhen",
                        contents: contents,
                        baseUrl: baseUrl,
                        el: $element,
                        templateMode: Boolean(templateMode),
                        itemPromise,
                        itemPromiseResolve,
                    });
                    break;
                case "plominoLabelClass":
                    items$.push({
                        type: "label",
                        contents: contents,
                        baseUrl: baseUrl,
                        el: $element,
                        templateMode: Boolean(templateMode),
                        itemPromise,
                        itemPromiseResolve,
                    });
                    break;
                case "plominoSubformClass":
                    items$.push({
                        baseUrl: baseUrl,
                        type: "subform",
                        el: $element,
                        templateMode: Boolean(templateMode),
                        itemPromise,
                        itemPromiseResolve,
                    });
                    break;
                default:
            }
        });

        items$.forEach((item: PlominoIteratingLayoutElement) => {
            ({
                field: (item: PlominoIteratingLayoutElement) =>
                    this.convertGroupFields(item.contents, item.baseUrl, item.el),
                hidewhen: (item: PlominoIteratingLayoutElement) =>
                    this.convertGroupHidewhens(item.contents, item.baseUrl, item.el),
                label: (item: PlominoIteratingLayoutElement) =>
                    this.convertLabel(item.baseUrl, item.el, "group", item.contents),
                subform: (item: PlominoIteratingLayoutElement) => this.convertFormSubform(item.baseUrl, item.el),
            }
                [item.type](item)
                .subscribe((result: string) => {
                    item.el.replaceWith($(result));

                    $groupLayout.find("p > span.mceEditable > .plominoLabelClass").each((i, lElement) => {
                        const $tmpLabel = $(lElement);
                        if ($tmpLabel.next().length && $tmpLabel.next().prop("tagName") === "BR") {
                            const $parentPTag = $tmpLabel.parent().parent();
                            $parentPTag.replaceWith($parentPTag.html());
                        }
                    });

                    item.itemPromiseResolve(result);
                }));
        });

        return Observable.from(items$)
            .map(item$ => {
                return Observable.fromPromise(item$.itemPromise);
            })
            .concatAll()
            .concatMap((result: string) => result)
            .reduce((formString: string, formItem: string) => {
                return (formString += formItem);
            }, "")
            .map((formString: string) => {
                const $wrongLabels = $groupLayout.find("span.mceEditable > span.mceEditable > .plominoLabelClass");

                $wrongLabels.each((i, wLabelElement) => {
                    const $label = $(wLabelElement);
                    $label
                        .parent()
                        .parent()
                        .replaceWith($label.parent());
                });

                const result = $groupLayout.html();
                $groupLayout.remove();
                return this.wrapIntoGroup(result, input.groupid);
            });
    }

    loadAndParseTemplatesLayout(baseUrl: string, template: PlominoFormGroupTemplate) {
        return this.getGroupLayout(baseUrl, template, true);
    }

    getFormLayout(baseUrl: string, $edIFrame: JQuery) {
        // this.log.info('getFormLayout called', baseUrl);
        // const $edIFrame = $(`iframe[id="${ baseUrl }_ifr"]`).contents();
        $edIFrame.css("opacity", 0);
        const $elements = $edIFrame.find(
            ".plominoGroupClass, .plominoSubformClass, " +
                ".plominoFieldClass:not(.plominoGroupClass .plominoFieldClass), " +
                ".plominoHidewhenClass:not(.plominoGroupClass .plominoHidewhenClass), " +
                ".plominoActionClass:not(.plominoGroupClass .plominoActionClass)," +
                " .plominoLabelClass:not(.plominoGroupClass .plominoLabelClass)"
        );

        const context = this;
        const promiseList: any[] = [];

        const widgetQueryData: { widget_type: string; id: string }[] = [];
        const widgetQuerySet: Set<string> = new Set();

        const $widgets = $edIFrame.find(
            ".plominoFieldClass, .plominoHidewhenClass, " + ".plominoActionClass, .plominoSubformClass"
        );

        $widgets.each(function() {
            const $widget = $(this);
            if ($widget.hasClass("mceNonEditable")) {
                return true;
            }

            const id = $widget.text();
            const widget_type = $widget
                .attr("class")
                .split(" ")[0]
                .replace("plomino", "")
                .replace("Class", "")
                .toLowerCase();

            widgetQueryData.push({ widget_type, id });
            widgetQuerySet.add(id);
        });

        this.log.info("widgetQuerySet original", Array.from(widgetQuerySet.values()));

        /**
         * insert additionally all elements for current form
         */
        const formItems = this.labelsRegistry.getAllForFormID(baseUrl);
        formItems.forEach(itemURL => {
            /* if item is not in widgetQueryData then */
            const itemId = itemURL.replace(baseUrl + "/", "");
            if (!widgetQuerySet.has(itemId)) {
                const itemWidgetTypeFull = this.labelsRegistry.get(itemURL, "@type");
                if (itemWidgetTypeFull) {
                    const itemWidgetType = itemWidgetTypeFull.replace("Plomino", "").toLowerCase();
                    widgetQueryData.push({ widget_type: itemWidgetType, id: itemId });
                    widgetQuerySet.add(itemId);
                }
            }
        });

        const widgetsFromServer = new Subject<any>();
        const widgetsObservable$: Observable<any> = widgetsFromServer.asObservable();
        const labelsRegistry = this.labelsRegistry.getRegistry();

        $elements.each(function() {
            const $element = $(this);
            const $class = $element.attr("class").split(" ")[0];
            let $groupId = "";

            if ($class === "plominoGroupClass") {
                $groupId = $element.attr("data-groupid");
                promiseList.push(
                    new Promise((resolve, reject) => {
                        widgetsObservable$.subscribe(() => {
                            context
                                .convertFormGroups(baseUrl, $element, $groupId, labelsRegistry)
                                .subscribe((result: any) => {
                                    $element.replaceWith(result);
                                    resolve();
                                });
                        });
                    })
                );
            } else if ($class === "plominoFieldClass" || $class === "plominoActionClass") {
                promiseList.push(
                    new Promise((resolve, reject) => {
                        widgetsObservable$.subscribe(() => {
                            context.convertFormFields(baseUrl, $element).subscribe((result: any) => {
                                $element.replaceWith(result);
                                resolve();
                            });
                        });
                    })
                );
            } else if ($class === "plominoSubformClass") {
                promiseList.push(
                    new Promise((resolve, reject) => {
                        widgetsObservable$.subscribe(() => {
                            context.convertFormSubform(baseUrl, $element).subscribe((result: any) => {
                                $element.replaceWith(result);
                                resolve();
                            });
                        });
                    })
                );
            } else if ($class === "plominoHidewhenClass") {
                promiseList.push(
                    new Promise((resolve, reject) => {
                        widgetsObservable$.subscribe(() => {
                            context.convertFormHidewhens(baseUrl, $element).subscribe((result: any) => {
                                $element.replaceWith(result);
                                resolve();
                            });
                        });
                    })
                );
            } else if ($class === "plominoLabelClass") {
                promiseList.push(
                    new Promise((resolve, reject) => {
                        widgetsObservable$.subscribe(() => {
                            context
                                .convertLabel(baseUrl, $element, "form", [], labelsRegistry)
                                .subscribe((result: any) => {
                                    $element.replaceWith(result);
                                    resolve();
                                });
                        });
                    })
                );
            }
        });

        if (widgetQueryData.length) {
            this.http
                .post(
                    `${baseUrl}/@@tinyform/example_widget`,
                    JSON.stringify({ widgets: widgetQueryData }),
                    "widget.service.ts getFormLayout"
                )
                .subscribe((response: Response) => {
                    response.json().forEach((result: any) => {
                        this.setWidgetCacheData(baseUrl, result.widget_type, result.id, result.html);
                        if (result.html === null) {
                            this.detectZombie(baseUrl, result.widget_type, result.id);
                        }
                    });
                    widgetsFromServer.next("loaded succeed");
                });
        } else {
            widgetsFromServer.next("blank form");
        }

        return promiseList;
    }

    private convertFormGroups(
        base: string,
        element: any,
        groupId: any,
        labelsRegistry?: Map<string, Record<string, any>>
    ): Observable<any> {
        // this.log.info('convertFormGroups');
        const $groupId = element.attr("data-groupid");
        const fields$: any[] = [];

        const randomId = Math.floor(Math.random() * 1e5) + 1e4 + 1;

        /**
         * decided to use the DOM
         */
        let $groupLayout = $(
            `<div id="tmp-cgroup-layout-id${randomId}" role="group"
        style="visibility: hidden; position: absolute"
        >${element.html()}</div>`
        );

        $("body").append($groupLayout);
        $groupLayout = $(`#tmp-cgroup-layout-id${randomId}`);

        const $elements = $groupLayout.find(
            ".plominoGroupClass, .plominoSubformClass, " +
                ".plominoFieldClass:not(.plominoGroupClass .plominoFieldClass), " +
                ".plominoHidewhenClass:not(.plominoGroupClass .plominoHidewhenClass), " +
                ".plominoActionClass:not(.plominoGroupClass .plominoActionClass), " +
                ".plominoLabelClass:not(.plominoGroupClass .plominoLabelClass)"
        );

        $elements.each((index: number, element: any) => {
            const $element = $(element);
            let itemPromiseResolve: any;
            const itemPromise = new Promise((resolve, reject) => {
                itemPromiseResolve = resolve;
            });
            const $class = $element.attr("class").split(" ")[0];
            let $groupId = "";

            if ($class === "plominoGroupClass") {
                $groupId = $element.attr("data-groupid");
            }

            switch ($element.attr("class")) {
                case "plominoGroupClass":
                    fields$.push({
                        type: "group",
                        url: base,
                        groupId: $groupId,
                        el: $element,
                        itemPromise,
                        itemPromiseResolve,
                    });
                case "plominoFieldClass":
                case "plominoActionClass":
                    fields$.push({
                        type: "field",
                        url: base,
                        el: $element,
                        itemPromise,
                        itemPromiseResolve,
                    });
                    break;
                case "plominoHidewhenClass":
                    fields$.push({
                        type: "hidewhen",
                        url: base,
                        el: $element,
                        itemPromise,
                        itemPromiseResolve,
                    });
                    break;
                case "plominoLabelClass":
                    fields$.push({
                        url: base,
                        type: "label",
                        el: $element,
                        itemPromise,
                        itemPromiseResolve,
                    });
                    break;
                case "plominoSubformClass":
                    fields$.push({
                        url: base,
                        type: "subform",
                        el: $element,
                        itemPromise,
                        itemPromiseResolve,
                    });
                    break;
                default:
            }
        });

        fields$.forEach((item: any) => {
            ({
                group: (item: any) => this.convertFormGroups(item.url, item.el, item.groupId, labelsRegistry),
                field: (item: any) => this.convertFormFields(item.url, item.el),
                hidewhen: (item: any) => this.convertFormHidewhens(item.url, item.el),
                label: (item: any) => this.convertLabel(item.url, item.el, "group", [], labelsRegistry),
                subform: (item: any) => this.convertFormSubform(item.url, item.el),
            }
                [item.type](item)
                .subscribe((result: string) => {
                    item.el.replaceWith($(result));

                    $groupLayout.find("p > span.mceEditable > .plominoLabelClass").each((i, lElement) => {
                        const $tmpLabel = $(lElement);
                        if ($tmpLabel.next().length && $tmpLabel.next().prop("tagName") === "BR") {
                            const $parentPTag = $tmpLabel.parent().parent();
                            $parentPTag.replaceWith($parentPTag.html());
                        }
                    });

                    item.itemPromiseResolve(result);
                }));
        });

        return Observable.from(fields$)
            .map(item$ => {
                return Observable.fromPromise(item$.itemPromise);
            })
            .concatAll()
            .concatMap((result: string) => result)
            .reduce((formString: any, formItem: any) => {
                return (formString += formItem);
            }, "")
            .map(groupString => {
                const $wrongLabels = $groupLayout.find("span.mceEditable > span.mceEditable > .plominoLabelClass");

                $wrongLabels.each((i, wLabelElement) => {
                    const $label = $(wLabelElement);
                    $label
                        .parent()
                        .parent()
                        .replaceWith($label.parent());
                });

                const result = $groupLayout.html();
                $groupLayout.remove();
                return this.wrapIntoGroup(result, $groupId);
            });
    }

    private convertGroupFields(ids: PlominoFormGroupContent[], base: string, element: JQuery): Observable<string> {
        // this.log.info('convertGroupFields', ids);
        const classList = element.get(0).classList;
        const $class = classList.length ? classList[0] : "";
        const $type = $class.slice(7, -5).toLowerCase();

        const $idData = this.findId(ids, element.text());
        let $id: any;
        let template: PlominoFormGroupContent = null;

        if ($idData && $idData.layout) {
            template = $idData;
            $id = $idData.id;
        } else {
            $id = null;
        }

        return (template ? this.getWidget(base, $type, $id, template) : this.getWidget(base, $type, $id)).map(
            response => {
                const $response = $(response);
                let container = "span";
                let content = "";

                if ($response.is("div,table,p") || $response.find("div,table,p").length) {
                    container = "div";
                }

                if (response !== undefined) {
                    content = `<${container} data-present-method="convertGroupFields_1"
                  class="${$class}" data-mce-resize="false"
                  data-plominoid="${$id}">
                      ${response}
                   </${container}>`;
                } else {
                    content = `<span data-present-method="convertGroupFields_2" class="${$class}">${$id}</span>`;
                }

                return template ? content : this.wrapIntoEditable(content);
            }
        );
    }

    private convertGroupHidewhens(
        ids: PlominoFormGroupContent[],
        base: string,
        element: JQuery,
        template?: PlominoFormGroupTemplate
    ): Observable<string> {
        const classList = element.get(0).classList;
        const $class = classList.length ? classList[0] : "";
        const $type = $class.slice(7, -5).toLowerCase();
        const $position = element.text().split(":")[0];
        const $id = element.text().split(":")[1];
        const $newId = this.findId(ids, $id).id;

        const container = "span";
        const content = `<${container} class="${$class} mceNonEditable" 
                              data-present-method="convertGroupHidewhens"
                              data-mce-resize="false"
                              data-plomino-position="${$position}" 
                              data-plominoid="${$newId}">
                    &nbsp;
                  </${container}>`;
        return Observable.of(this.wrapIntoEditable(content));
    }

    private convertFormFields(base: string, $element: JQuery): Observable<string> {
        // this.log.info('convertFormFields');
        const classList = $element.get(0).classList;
        let fieldClass = classList.length ? classList[0] : "";
        const fieldType = fieldClass.slice(7, -5).toLowerCase();
        const fieldId = $element.text();
        const template: PlominoFormGroupContent = null;

        return (template
            ? this.getWidget(base, fieldType, fieldId, template)
            : this.getWidget(base, fieldType, fieldId)
        ).map(response => {
            const $response = $(response);
            let container = "span";
            let content = "";

            if ($response.is("div,table,p") || $response.find("div,table,p").length) {
                container = "div";
            }

            if (response != undefined) {
                const isInnerGroup =
                    Boolean($element.closest(".plominoGroupClass").length) ||
                    Boolean($element.closest('div[role="group"]').length);
                if (!isInnerGroup) {
                    fieldClass += " mceNonEditable";
                }
                content = `<${container} data-present-method="convertFormFields_1" 
                      class="${fieldClass}" data-mce-resize="false"
                      data-plominoid="${fieldId}">
                        ${response}
                     </${container}>`;
            } else {
                content = `<span data-present-method="convertFormFields_2"
            class="${fieldClass}">${fieldId}</span>`;
            }

            return content;
        });
    }

    private convertFormHidewhens(base: string, element: any, template?: PlominoFormGroupTemplate): Observable<string> {
        const classList = element.get(0).classList;
        const $class = classList.length ? classList[0] : "";
        const $position = element.text().split(":")[0];
        const $id = element.text().split(":")[1];

        const container = "span";
        const content = `<${container} class="${$class} mceNonEditable" 
                              data-mce-resize="false"
                              data-present-method="convertFormHidewhens"
                              data-plomino-position="${$position}" 
                              data-plominoid="${$id}">
                    &nbsp;
                  </${container}>`;

        return Observable.of(content);
    }

    private convertFormSubform(base: string, element: JQuery): Observable<string> {
        const classList = element.get(0).classList;
        const $class = classList.length ? classList[0] : "";
        const $id = element.text().trim();

        return this.getWidget(base, "subform", $id === "Subform" ? null : $id).map(response => {
            let $response = $(response);
            if ($response.length > 1) {
                $response = $(`<div>${response}</div>`);
            }
            const result = $response
                .addClass("mceNonEditable")
                .addClass($class)
                .attr("data-plominoid", $id)
                .get(0);
            return result
                ? result.outerHTML
                : '<div class="mceNonEditable" data-plominoid="' + $id + '"><h2>Subform</h2><input value="..."/></div>';
        });
    }

    private convertLabel(
        base: string,
        element: JQuery,
        type: "form" | "group",
        ids: PlominoFormGroupContent[] = [],
        labelsRegistry?: Map<string, Record<string, any>>
    ): Observable<string> {
        const classList = element.get(0).classList;
        const $class = classList.length ? classList[0] : "";
        const $type = $class.slice(7, -5).toLowerCase();

        // if (element.parent().attr('contenteditable') !== 'false') {
        //   element.parent().attr('contenteditable', 'false');
        // }

        if (element.parent().attr("contenteditable") === "false") {
            element.parent().removeAttr("contenteditable");
        }

        let $id: string = null;
        let template: PlominoFormGroupContent = null;

        let tmpId = element.html();
        const tmpIdSplit = tmpId.split(":");
        const hasAdvancedTitle = tmpId.indexOf(":") !== -1 && tmpIdSplit.length > 1 && tmpIdSplit[1];

        if (hasAdvancedTitle) {
            tmpId = tmpIdSplit[0];
        }

        if (ids.length) {
            const $idData = this.findId(ids, tmpId);

            if ($idData && $idData.layout) {
                template = $idData;
                $id = $idData.id;
            } else {
                $id = null;
            }
        } else {
            $id = tmpId;
        }

        // this.log.info('convertLabel', $class, $id, `${ base }/${ $id }`,
        //   labelsRegistry ? labelsRegistry.get(`${ base }/${ $id }`) : null, template);
        // this.log.extra('widget.service.ts convertLabel');

        if (!template && $id && labelsRegistry && labelsRegistry.has(`${base}/${$id}`)) {
            template = { id: $id, title: labelsRegistry.get(`${base}/${$id}`)["title"] };
            // labelsRegistry.delete(`${ base }/${ $id }`); // just in case
        }

        if (template && hasAdvancedTitle) {
            template.title = element.html();
        }

        return (template ? this.getWidget(base, $type, $id, template) : this.getWidget(base, $type, $id)).map(
            response => {
                const $response = $(response);
                const result = type === "group" ? $response.get(0).outerHTML : `${response}`;
                const endPoint = this.adapter.endPoint("label", result);
                return endPoint;
            }
        );
    }

    private wrapIntoEditable(content: string): string {
        const $wrapper = $("<span />");
        return $wrapper
            .html(content)
            .addClass("mceEditable")
            .wrap("<div />")
            .parent()
            .html();
    }

    private wrapIntoGroup(content: string, groupId: string): string {
        // console.info('wrap', content, groupId);
        const $wrapper = $("<div />");
        return (
            $wrapper
                .html(content)
                .addClass("plominoGroupClass mceNonEditable")
                .attr("data-groupid", groupId)
                // .attr('contenteditable', 'false')
                .wrap("<div />")
                .parent()
                // .append('<br />')
                .html()
        );
    }

    private findId(newIds: PlominoFormGroupContent[], id: string) {
        return _.find(newIds, (newId: PlominoFormGroupContent) => {
            return newId.id.indexOf(id) > -1;
        });
    }

    getWidget(baseUrl: string, type: string, id: string, content?: PlominoFormGroupContent): Observable<string> {
        // this.log.info('type', type, 'id', id, 'content', content);
        // this.log.extra('widget.service.ts getWidget');
        if (content && type === "label") {
            const splitTitle = content.title.split(":");
            const advancedTitleExists = splitTitle.length >= 2 && splitTitle[1] && splitTitle[0] === id;
            if (advancedTitleExists) {
                content.title = splitTitle.slice(1).join(":");
            }
            return Observable.of(
                `<span class="plominoLabelClass mceNonEditable"
          ${advancedTitleExists ? ` data-advanced="1"` : ""}
          ${id ? ` data-plominoid="${id}"` : ""}>${content.title}</span>`
            );
        }
        const splitId = id ? id.split(":") : [];
        if (!content && id && type === "label" && splitId.length >= 2 && splitId[1]) {
            return Observable.of(
                `<span class="plominoLabelClass mceNonEditable"
          data-advanced="1"
          data-plominoid="${splitId[0]}">${splitId.slice(1).join(":")}</span>`
            );
        }
        if (content && type === "field") {
            return Observable.of(content.layout);
        }

        const cachedResult = this.getWidgetCacheData(baseUrl, type, id);
        if (cachedResult) {
            return Observable.of(cachedResult);
        }
        // else if (!cachedResult && type === 'hidewhen') {
        //   return this.convertFormHidewhens();
        // }

        return this.http
            .post(
                `${baseUrl}/@@tinyform/example_widget`,
                JSON.stringify({ widget_type: type, id: id ? id : "" }),
                "widget.service.ts getWidget"
            )
            .map((response: Response) => {
                const result = response.json();
                this.setWidgetCacheData(baseUrl, type, id, result);
                return result;
            });
    }
}

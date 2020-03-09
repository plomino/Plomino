import { PlominoDBService } from "./db.service";
import { LabelsRegistryService } from "./../editors/tiny-mce/services/labels-registry.service";
import { LogService } from "./log.service";
import { Injectable } from "@angular/core";
import { PlominoActiveEditorService } from "./active-editor.service";

@Injectable()
export class PlominoElementAdapterService {
    private $previousSelectedElement: JQuery;
    private $latestSelectedElement: JQuery;
    private $latestSelectedElementPath: string;
    private $latestSelectedPosition: JQuery;

    /**
     * this service is end-point for each element on the markup
     */
    constructor(
        private log: LogService,
        private labelsRegistry: LabelsRegistryService,
        private activeEditorService: PlominoActiveEditorService,
        private dbService: PlominoDBService
    ) {}

    endPoint(type: string, source: string) {
        // this.log.info('endPoint', type, source);
        if (type === "label") {
            const $source = $(source);
            /**
             * make labels editable
             */
            source = $source.removeClass("mceNonEditable").get(0).outerHTML;

            /**
       * <span class="plominoLabelClass mceNonEditable" 
          data-mce-resize="false" 
          data-plominoid="text_1_2_3_4_5_6_7">
          <span class="plominoLabelClass mceEditable"
          data-plominoid="text_1_2_3_4_5_6_7">Untitled9</span>    
        </span>
       */
            if ($source.find(".plominoLabelClass").length) {
                /* monkey patch */
                source = $source.html($source.find(".plominoLabelClass").html()).get(0).outerHTML;
            }
        }
        return source;
    }

    getPathTo(element: HTMLElement): string {
        if (element.id !== "") {
            return 'id("' + element.id + '")';
        }

        if (element === document.body) {
            return element.tagName;
        }

        let ix = 0;
        const siblings = element.parentNode.childNodes;

        for (let i = 0; i < siblings.length; i++) {
            const sibling = siblings[i];

            if (sibling === element) {
                return this.getPathTo(<HTMLElement>element.parentNode) + "/" + element.tagName + "[" + (ix + 1) + "]";
            }

            if (sibling.nodeType === 1 && (<HTMLElement>sibling).tagName === element.tagName) {
                ix++;
            }
        }
    }

    /**
     * difference with the select is that position not exactly selected element like field
     */
    selectPosition($position: JQuery) {
        this.$latestSelectedPosition = $position;
    }

    select($element: JQuery) {
        if ($element === null) {
            this.$previousSelectedElement = this.$latestSelectedElement;
            this.$latestSelectedElement = null;
            this.$latestSelectedElementPath = null;
            return;
        }

        if ($element.is("p,input,img") && $element.closest(".plominoFieldClass").length) {
            $element = $element.closest(".plominoFieldClass");
        }

        this.$previousSelectedElement = this.$latestSelectedElement;
        this.$latestSelectedElement = $element;
        this.$latestSelectedElementPath = this.getPathTo($element.get(0));

        this.log.info("selected", this.$latestSelectedElement);
        this.log.info("after", this.$previousSelectedElement);
        this.log.extra("element-adapter.service.ts select");

        /** blur */
        if (!this.activeEditorService.getActive()) {
            return;
        }
        const $editorBody = $(this.activeEditorService.getActive().getBody());

        $editorBody
            .find(".plominoFieldClass")
            .filter((i, element) => element !== $element.get(0))
            .removeClass("plominoFieldClass--selected");

        $editorBody
            .find(".plominoLabelClass")
            .filter((i, element) => element !== $element.get(0))
            .removeClass("mceEditable")
            .removeAttr("contenteditable")
            .removeClass("plominoLabelClass--selected");
        // .attr('contenteditable', 'false')
        // .addClass('mceNonEditable');

        if ($element.hasClass("plominoFieldClass")) {
            $element.addClass("plominoFieldClass--selected");
        }

        /**
         * if $element is label - make it listen to input event
         */
        if ($element.hasClass("plominoLabelClass")) {
            $editorBody.find(".plominoLabelClass").off(".adapter");

            $element.addClass("plominoLabelClass--selected").one("click.adapter", () => {
                $element
                    .removeClass("mceNonEditable")
                    .attr("contenteditable", "true")
                    .addClass("mceEditable");

                // const ed = this.activeEditorService.getActive();
                // const rng = ed.selection.getRng();
                // rng.setStart(rng.startContainer, 0);
                // ed.selection.setRng(rng);
            });

            this.log.info("element input.adapter event attached", $element.get(0));
            $element.on("input.adapter", $event => {
                setTimeout(() => {
                    if ($element.attr("data-plominoid") === "defaultLabel") {
                        return true;
                    }

                    this.log.info("input.adapter", $element.html());
                    const labelAdvanced = Boolean($element.attr("data-advanced"));

                    if (!labelAdvanced) {
                        const selectedId = $element.attr("data-plominoid");
                        const temporaryTitle = $element
                            .html()
                            .replace(/&nbsp;/g, " ")
                            .replace(/^(.+?)?<br>$/, "$1")
                            .replace(/\s+/g, " ")
                            .trim();
                        const activeURL = `${this.dbService.getDBLink()}/${this.activeEditorService.getActive().id}`;
                        this.labelsRegistry.update(`${activeURL}/${selectedId}`, temporaryTitle, "temporary_title");

                        const $allTheSame = $(this.activeEditorService.getActive().getBody())
                            .find(`.plominoLabelClass[data-plominoid="${selectedId}"]`)
                            .filter((i, element) => element !== $element.get(0) && !$(element).attr("data-advanced"));

                        $allTheSame.html(temporaryTitle);
                    }
                }, 1);
            });
        }
    }

    getSelectedBefore() {
        return this.$previousSelectedElement;
    }

    getSelected() {
        return this.$latestSelectedElement;
    }

    getSelectedXPath() {
        return this.$latestSelectedElementPath;
    }

    getSelectedJQueryPath() {
        const xPath = this.getSelectedXPath();
        return xPath
            ? xPath
                  .replace(/id\("(.+?)"\)/g, "#$1")
                  .replace(/\//g, " > ")
                  .replace(/\[(\d+)\]/g, (match, p1) => `:nth-of-type(${p1})`)
            : null;
    }

    getSelectedPosition() {
        return this.$latestSelectedPosition;
    }
}

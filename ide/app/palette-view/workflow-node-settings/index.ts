import { LogService } from "./../../services/log.service";
import { PlominoWorkflowChangesNotifyService } from "./../../editors/workflow/workflow.changes.notify.service";
import { Component, AfterContentChecked } from "@angular/core";

@Component({
    selector: "plomino-workflow-node-settings",
    template: require("./workflow-node-settings.component.html"),
    styles: [
        `
            .wfnode-settings {
                padding: 15px;
            }
        `,
    ],
})
export class PlominoWorkflowNodeSettingsComponent implements AfterContentChecked {
    element = {
        description: <string>null,
    };

    constructor(private changesService: PlominoWorkflowChangesNotifyService, private log: LogService) {}

    ngAfterContentChecked() {
        this.initElement();
    }

    initElement() {
        const $selected = $(".workflow-node--selected");
        let $description: string = null;

        if ($selected.length) {
            if ($selected.find(".workflow-node__text--task").length) {
                $description = $selected
                    .find(".workflow-node__text--task")
                    .html()
                    .replace("Task: ", "")
                    .trim();
            }
        }

        this.element = {
            description: $description,
        };
    }

    propertyChanged(key: string, event: Event) {
        setTimeout(() => this.changesService.changesDetector.next({ key, value: this.element[key] }), 10);
    }
}

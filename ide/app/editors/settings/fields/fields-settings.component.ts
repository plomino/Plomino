import { Component, Input, Output, EventEmitter, ViewChild } from "@angular/core";
import { REACTIVE_FORM_DIRECTIVES } from "@angular/forms";
import { ElementService, LogService } from "../../../services";
import { ChangeDetectorRef } from "@angular/core";

@Component({
    selector: "plomino-fields-settings",
    template: require("./fields-settings.component.html"),
    styles: [
        `
            form {
                margin: 15px;
            }
            .help-block {
                font-style: italic;
            }
            .specificOptions {
                border: 1px solid #aaaaaa;
                border-radius: 5px;
                padding: 15px;
                padding-bottom: 0px;
                margin-bottom: 15px;
            }
            .specificOptions legend {
                width: inherit;
                font-size: inherit;
                font-style: italic;
                border-bottom: 0;
                margin-bottom: 0;
            }
        `,
        require("../settings-styles.css"),
    ],
    providers: [ElementService],
    directives: [REACTIVE_FORM_DIRECTIVES],
})
export class FieldsSettingsComponent {
    @Input() id: string;
    @Input() tree: any;
    data: any;
    fieldTypeValue: any = "GOOGLECHART";
    conditional: any = this.conditionalInit();
    @Output() isDirty = new EventEmitter();
    @Output() titleChanged = new EventEmitter();
    @Output() elementDeleted = new EventEmitter();
    @ViewChild("form") form: any;
    @ViewChild("theForm") theForm: any;

    constructor(
        private _elementService: ElementService,
        private changeDetector: ChangeDetectorRef,
        private log: LogService
    ) {}

    ngAfterViewInit() {
        this.getElement();
        this.form.control.valueChanges.subscribe(() => this.isDirty.emit(true));
    }

    conditionalInit() {
        return {
            googlechart: {},
            text: {},
            number: {},
            datetime: {},
            datagrid: {},
            doclink: {},
            googlevisualization: {},
            selection: {},
            name: {},
            richtext: {},
            boolean: {},
            attachment: {},
        };
    }

    getElement() {
        this._elementService.getElement(this.id).subscribe(
            data => {
                if (data.field_type === "SELECTION") data.selectionlist = data.selectionlist.join("\n");
                this.data = data;
                this.fieldTypeValue = data.field_type;
                this.updateConditional();
                this.changeDetector.detectChanges(); // this way the tab isn't marked as unsaved
                this.isDirty.emit(false);
            },
            err => console.error(err)
        );
        this.log.extra("fields-settings.component.ts getElement");
    }

    onSubmit(
        id: string,
        title: string,
        description: string,
        fieldMode: string,
        indexType: string,
        readTemplate: string,
        editTemplate: string,
        mandatory: boolean,
        toBeIndexed: boolean
    ) {
        const element = {
            title: title,
            description: description,
            field_type: this.fieldTypeValue,
            field_mode: fieldMode,
            read_template: readTemplate,
            edit_template: editTemplate,
            mandatory: mandatory,
            to_be_indexed: toBeIndexed,
            //"index_type": indexType
        };
        this._elementService.patchElement(id, JSON.stringify(element)).subscribe(
            () => {
                this.titleChanged.emit(this.data.title);
                this.patchConditional();
            },
            err => console.error(err)
        );
        this.log.extra("fields-settings.component.ts onSubmit");
    }

    updateConditional() {
        switch (this.fieldTypeValue) {
            case "GOOGLECHART":
                this.conditional.googlechart = {
                    editrows: this.data.editrows,
                };
                break;
            case "TEXT":
                this.conditional.text = {
                    carriage: this.data.carriage,
                    size: this.data.size,
                    widget: this.data.widget,
                };
                break;
            case "NUMBER":
                this.conditional.number = {
                    format: this.data.format,
                    number_type: this.data.number_type,
                    size: this.data.size,
                };
                break;
            case "DATETIME":
                this.conditional.datetime = {
                    format: this.data.format,
                    startingyear: this.data.startingyear,
                    widget: this.data.widget,
                };
                break;
            case "DATAGRID":
                this.conditional.datagrid = {
                    associated_form: this.data.associated_form,
                    field_mapping: this.data.field_mapping,
                    widget: this.data.widget,
                };
                break;
            case "DOCLINK":
                this.conditional.doclink = {
                    labelcolumn: this.data.labelcolumn,
                    separator: this.data.separator,
                    sourceview: this.data.sourceview,
                    widget: this.data.widget,
                };
                break;
            case "GOOGLEVISUALIZATION":
                this.conditional.googlevisualization = {
                    chartid: this.data.chartid,
                };
                break;
            case "SELECTION":
                this.conditional.selection = {
                    separator: this.data.separator,
                    selectionlist: this.data.selectionlist,
                    widget: this.data.widget,
                };
                break;
            case "NAME":
                this.conditional.name = {
                    restricttogroup: this.data.restricttogroup,
                    selector: this.data.selector,
                    separator: this.data.separator,
                    type: this.data.type,
                };
                break;
            case "RICHTEXT":
                this.conditional.richtext = {
                    height: this.data.height,
                };
                break;
            case "BOOLEAN":
                this.conditional.boolean = {
                    widget: this.data.widget,
                };
                break;
            case "ATTACHMENT":
                this.conditional.attachment = {
                    type: this.data.type,
                };
                break;
        }
        this.log.extra("fields-settings.component.ts updateConditional");
    }

    patchConditional() {
        const element = JSON.parse(JSON.stringify(this.conditional[this.fieldTypeValue.toLowerCase()]));
        if (this.fieldTypeValue === "SELECTION") {
            element.selectionlist = this.conditional.selection.selectionlist.split("\n");
        }
        this._elementService.patchElement(this.id, JSON.stringify(element)).subscribe(() => {
            this.isDirty.emit(false);
        });
        this.log.extra("fields-settings.component.ts patchConditional");
    }

    deleteElement() {
        this._elementService.deleteElement(this.data["@id"]).subscribe(
            () => this.elementDeleted.emit(this.data["@id"]),
            (err: any) => console.error(err)
        );
        this.log.extra("fields-settings.component.ts deleteElement");
    }
}

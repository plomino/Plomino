import { Component, Input, Output, EventEmitter, ViewChild } from "@angular/core";
import { REACTIVE_FORM_DIRECTIVES } from "@angular/forms";
import { ElementService } from "../../../services";

@Component({
    selector: "plomino-hide-when-settings",
    template: require("./hide_when-settings.component.html"),
    styles: ["form {margin: 15px;} .help-block {font-style: italix;}"],
    providers: [ElementService],
    directives: [REACTIVE_FORM_DIRECTIVES],
})
export class HideWhenSettingsComponent {
    @Input() id: string;
    data: any;
    @Output() isDirty = new EventEmitter();
    @Output() titleChanged = new EventEmitter();
    @Output() elementDeleted = new EventEmitter();
    @ViewChild("form") form: any;

    constructor(private _elementService: ElementService) {}

    ngOnInit() {
        this.getElement();
    }

    ngAfterViewInit() {
        this.form.control.valueChanges.subscribe(() => this.isDirty.emit(true));
    }

    getElement() {
        // this._elementService.getElement(this.id)
        //     .subscribe(
        //         data => {
        //             this.data = data;
        //             this.isDirty.emit(false);
        //         },
        //         err => console.log(err)
        //     );
    }

    onSubmit(id: string, title: string, description: string, isDynamicHidewhen: boolean) {
        const element = { title, description, isDynamicHidewhen };
        this._elementService.patchElement(id, JSON.stringify(element)).subscribe(
            () => {
                this.titleChanged.emit(this.data.title);
                this.isDirty.emit(false);
            },
            err => console.error(err)
        );
    }

    deleteElement() {
        this._elementService.deleteElement(this.data["@id"]).subscribe(
            () => this.elementDeleted.emit(this.data["@id"]),
            (err: any) => console.error(err)
        );
    }
}

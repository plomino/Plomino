import { Component, Input, Output, EventEmitter, ViewChild } from "@angular/core";
import { REACTIVE_FORM_DIRECTIVES } from "@angular/forms";
import { ElementService } from "../../../services";

@Component({
    selector: "plomino-forms-settings",
    template: require("./forms-settings.component.html"),
    styles: ["form {margin: 15px;} .help-block {font-style: italic;}"],
    providers: [ElementService],
    directives: [REACTIVE_FORM_DIRECTIVES],
})
export class FormsSettingsComponent {
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
        //         err => console.error(err)
        //     );
    }

    onSubmit(
        id: string,
        title: string,
        description: string,
        formMethod: string,
        hideDefaultActions: boolean,
        isPage: boolean,
        searchForm: boolean,
        searchView: string,
        resourcesJS: string,
        resourcesCSS: string
    ) {
        const element = {
            title: title,
            description: description,
            form_method: formMethod,
            hide_default_actions: hideDefaultActions,
            isPage: isPage,
            isSearchForm: searchForm,
            search_view: searchView,
            resources_js: resourcesJS,
            resources_css: resourcesCSS,
        };
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

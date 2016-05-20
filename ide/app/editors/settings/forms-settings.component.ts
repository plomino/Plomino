import { Component, Input, Output, EventEmitter } from '@angular/core';
import { ElementService } from '../../services/element.service';

@Component({
    selector: 'my-forms-settings',
    template: require('./forms-settings.component.html'),
    styles: ['form {margin: 15px;} .help-block {font-style: italic;}'],
    providers: [ElementService]
})
export class FormsSettingsComponent {
    @Input() id: string;
    data: any;
    @Output() titleChanged = new EventEmitter();

    constructor(private _elementService: ElementService) { }

    ngOnInit() {
        this.getElement();
    }

    getElement() {
        this._elementService.getElement(this.id)
            .subscribe(
                data => { this.data = data },
                err => console.error(err)
            );
    }

    onSubmit(id: string,
        title: string,
        description: string,
        formMethod: string,
        hideDefaultActions: boolean,
        isPage: boolean,
        searchForm: boolean,
        searchView: string,
        resourcesJS: string,
        resourcesCSS: string) {
            let element = {
                "title": title,
                "description": description,
                "form_method": formMethod,
                "hide_default_actions": hideDefaultActions,
                "isPage": isPage,
                "isSearchForm": searchForm,
                "search_view": searchView,
                "resources_js": resourcesJS,
                "resources_css": resourcesCSS
            };
            this._elementService.patchElement(id, JSON.stringify(element));
            this.titleChanged.emit(this.data.title);
    }
}

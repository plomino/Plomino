import {Component, Input, Output, EventEmitter} from '@angular/core';
import {ElementService} from '../services/element.service';

declare var tinymce: any;

@Component({
    selector: 'my-tiny-mce',
    template: '<form><textarea class="tinymce-wrap"></textarea></form>',
    providers: [ElementService]
})
export class TinyMCEComponent {

    @Input() id: string;
    data: string;

    constructor(private _elementService: ElementService) {}

    ngOnInit() {
        tinymce.init({
            selector:'.tinymce-wrap',
            plugins: ["code, save", "link"],
            toolbar: "save | undo redo | formatselect | bold italic underline | alignleft aligncenter alignright alignjustify | bullist numlist | outdent indent | unlink link | image",
            save_onsavecallback: () => { this.saveFormLayout() },
		    menubar: "file edit insert view format table tools",
            height : "398",
            resize: false
        });
        this.getFormLayout();
    }

    getFormLayout() {
        this._elementService.getElementFormLayout(this.id).subscribe(
            // check if it's a string, so it won't change its value to undefined
            (data: string) => { tinymce.activeEditor.setContent(data); },
            err => console.error(err)
        );
    }

    saveFormLayout() {
        if(tinymce.activeEditor !== null){
            this._elementService.patchElement(this.id, JSON.stringify({"form_layout":tinymce.activeEditor.getContent()}));
        }
    }

}

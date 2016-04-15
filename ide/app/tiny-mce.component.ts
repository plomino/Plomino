import {Component, OnInit, Input} from 'angular2/core';

declare var tinymce: any;

@Component({
    selector: 'my-tiny-mce',
    template: '<textarea class="tinymce-wrap"></textarea>'
})
export class TinyMCEComponent {
    @Input() content: string;

    ngOnInit(){
        tinymce.init({
            selector:'.tinymce-wrap',
            plugins: ["code"],
		    menubar: true,
            height : "354"
        });
        tinymce.activeEditor.setContent(this.content);

        console.log(this.content);
    }
}

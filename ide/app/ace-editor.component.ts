import {Component, OnInit, AfterViewInit, Input} from 'angular2/core';

declare var ace: any;

@Component({
    selector: 'my-ace-editor',
    template: `
    <div [id]="id" class="ace-editor">{{content}}</div>
    `,
    styles: ['.ace-editor{display: block; height: 354px; text-align: left;}']
})
export class ACEEditorComponent {
    @Input() content: number;
    @Input() aceNumber: number;

    id: string;

    ngOnInit(){
        this.id = 'editor'+this.aceNumber;
    }

    ngAfterViewInit(){
        var editor = ace.edit(this.id);
        editor.setTheme("ace/theme/xcode");
        editor.getSession().setMode("ace/mode/python");
    }
}

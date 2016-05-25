import {Component, OnInit, AfterViewInit, Input} from '@angular/core';
import {ElementService} from '../services/element.service';

declare var ace: any;

@Component({
    selector: 'my-ace-editor',
    template: `
    <div [id]="id" class="ace-editor"></div>
    `,
    styles: ['.ace-editor{display: block; height: 508px; text-align: left;}'],
    providers: [ElementService]
})
export class ACEEditorComponent {
    @Input() aceNumber: number;
    @Input() url: string;
    @Input() path: any;

    editor: any;
    id: string;

    constructor(private _elementService: ElementService) { }

    ngOnInit(){
        this.id = 'editor'+this.aceNumber;
        this._elementService.getElement(this.url).subscribe((data) => {
            let type = data.parent['@type'].replace('Plomino','').replace('Database','')+data['@type'].replace('Plomino','');
            let name = this.url.replace("http://localhost:8080/Plone/plominodatabase/","");
            this._elementService.getElementCode("http://localhost:8080/Plone/plominodatabase/code?"+type+"="+name)
                .subscribe((code: string) => this.editor.setValue(code,-1));
        })
    }

    ngAfterViewInit(){
        this.editor = ace.edit(this.id);
        this.editor.setTheme("ace/theme/xcode");
        this.editor.getSession().setMode("ace/mode/python");
        this.editor.on("changeSelection", () => {
            let isComment = false;
            for(let line of this.editor.getSession().getLines(this.editor.getSelectionRange().start.row,this.editor.getSelectionRange().end.row)){
                isComment = line.match(/^##.START|^##.END/) === null ? isComment : true;
            }
            this.editor.setReadOnly(isComment);
        });
    }
}

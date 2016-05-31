import {Component, OnInit, AfterViewInit, Input} from '@angular/core';
import {PopoverComponent} from './popover.component';
import {ElementService} from '../services/element.service';
import {DROPDOWN_DIRECTIVES} from 'ng2-bootstrap/ng2-bootstrap';

declare var ace: any;

@Component({
    selector: 'my-ace-editor',
    template: require("./ace-editor.component.html"),
    styles: ['.ace-editor{display: block; height: 508px; text-align: left;} .popover{width: 500px;}'],
    directives: [DROPDOWN_DIRECTIVES, PopoverComponent],
    providers: [ElementService]
})
export class ACEEditorComponent {
    @Input() aceNumber: number;
    @Input() url: string;
    @Input() path: any;

    methodList: any[];
    type: string;
    editor: any;
    id: string;

    constructor(private _elementService: ElementService) { }

    ngOnInit(){
        this.id = 'editor'+this.aceNumber;
        this._elementService.getElement(this.url).subscribe((data) => {
            this.type = data['@type'];
            let type = data.parent['@type'].replace('Plomino','').replace('Database','')+this.type.replace('Plomino','');
            let name = this.url.replace("http://localhost:8080/Plone/plominodatabase/","");
            this._elementService.getElementCode("http://localhost:8080/Plone/plominodatabase/code?"+type+"="+name)
                .subscribe((code: string) => {
                    let parsed = JSON.parse(code);
                    this.editor.setValue(parsed.code,-1)
                    this.methodList = parsed.methods;
                });
        })
    }

    ngAfterViewInit(){
        this.editor = ace.edit(this.id);
        this.editor.setTheme("ace/theme/xcode");
        this.editor.getSession().setMode("ace/mode/python");
        this.editor.setOptions({enableBasicAutocompletion: true, enableLiveAutocompletion: true});
        this.editor.on("changeSelection", () => {
            let isComment = false;
            for(let line of this.editor.getSession().getLines(this.editor.getSelectionRange().start.row,this.editor.getSelectionRange().end.row)){
                isComment = line.match(/^##.START.*{$|^##.END.*}$/) === null ? isComment : true;
            }
            this.editor.setReadOnly(isComment);
        });
        let staticWordCompleter = {
            getCompletions: (editor: any, session: any, pos: any, prefix: any, callback: any) => {
                var wordList = this.getMethodList();
                callback(null, wordList.map(function(word: any) {
                    return {
                        caption: word.caption,
                        value: word.value,
                        meta: "methods"
                    };
                }));
            }
        }
        this.editor.completers = [];
        this.editor.completers.push(staticWordCompleter);
    }

    getMethodList(): any[] {
        let buildMethod = (name:string) => {return { caption:name, value:"## START "+name+" {\n\n## END "+name+" }", popup: false }};
        switch(this.type) {
            case "PlominoForm":
                return [
                    buildMethod("document_title"),
                    buildMethod("document_id"),
                    buildMethod("search_formula"),
                    buildMethod("onCreateDocument"),
                    buildMethod("onOpenDocument"),
                    buildMethod("beforeSaveDocument"),
                    buildMethod("onSaveDocument"),
                    buildMethod("onDeleteDocument"),
                    buildMethod("onSearch"),
                    buildMethod("beforeCreateDocument")
                ]
            case "PlominoField":
                return [
                    buildMethod("formula"),
                    buildMethod("validation_formula"),
                    buildMethod("html_attributes_formula")
                ]
            case "PlominoAction":
                return [
                    buildMethod("content"),
                    buildMethod("hidewhen")
                ]
            case "PlominoView":
                return [
                    buildMethod("selection_formula"),
                    buildMethod("form_formula"),
                    buildMethod("onOpenView")
                ]
        }
    }
}

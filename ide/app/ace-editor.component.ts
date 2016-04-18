import {Component, OnInit, Input} from 'angular2/core';

declare var ace: any;

@Component({
    selector: 'my-ace-editor',
    template: `
    <div id="editor">def test(test):
    if(ceci):
        cela();
        cela = 5;
        x = 5+4

    return x

print "blabla"</div>
    `,
    styles: ['#editor{display: block; height: 354px; text-align: left;}']
})
export class ACEEditorComponent {
    @Input() content: string;

    ngOnInit(){
        var editor = ace.edit("editor");
        editor.setTheme("ace/theme/xcode");
        editor.getSession().setMode("ace/mode/python");
    }
}

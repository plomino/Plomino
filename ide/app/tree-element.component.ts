import {Input, Component} from 'angular2/core';

@Component({
    selector: 'my-tree-element',
    templateUrl: 'app/tree-element.component.html',
    styles: [`
        ul {list-style:none;}
        li:before {
            content: "-";
            position: absolute;
            margin-left: -15px;
        }
        `],
    directives: [TreeElementComponent]
})
export class TreeElementComponent {
    @Input()
    data:any;
}

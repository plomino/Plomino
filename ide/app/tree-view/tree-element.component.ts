import {Input, Component} from 'angular2/core';

@Component({
    selector: 'my-tree-element',
    templateUrl: 'app/tree-view/tree-element.component.html',
    styleUrls: ['app/tree-view/tree-element.component.css'],
    directives: [TreeElementComponent]
})
export class TreeElementComponent {
    @Input()
    data:any;

    display:boolean = true;

    toggleDisplayChild(){
        this.display = !this.display;
    }
}

import {Input, Component} from 'angular2/core';
import {TreeElementComponent} from './tree-element.component';

@Component({
    selector: 'my-tree-search',
    template: `<input [(ngModel)]="input_value" value="{{input_value}}">
                <button (click)="search(data)">Search</button>
                <my-tree-element [data]="result"></my-tree-element>
                <hr/>
                `,
    directives: [TreeElementComponent]
})
export class TreeSearchComponent {
    @Input()
    data:any;

    result:any;
    input_value:string;

    search(pdata:any){
        this.result = [];
        if (this.input_value!="")
            this.search_child(pdata);
    }
    search_child(pdata:any){
        for (var key in pdata) {
            if (pdata[key].label.toLowerCase().indexOf(this.input_value.toLowerCase()) != -1) {
                this.result.push(pdata[key]);
                console.log(this.result);
            }
            else {
                this.search_child(pdata[key].children);
            }
        }
    }
}

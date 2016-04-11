import {Component} from 'angular2/core';
import {TreeComponent} from './tree.component';

@Component({
    selector: 'my-app',
    template: '<my-tree></my-tree>',
    directives: [TreeComponent]
})
export class AppComponent {

}

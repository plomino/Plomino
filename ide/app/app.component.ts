import {Component} from 'angular2/core';
import {TreeComponent} from './tree-view/tree.component';

@Component({
    selector: 'my-app',
    templateUrl: 'app/app.component.html',
    styleUrls: ['app/app.component.css'],
    directives: [TreeComponent]
})
export class AppComponent {
    
}

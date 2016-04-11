import {Component} from 'angular2/core';
import {TreeElementComponent} from './tree-element.component';

@Component({
    selector: 'my-tree',
    template: '<my-tree-element [data]="arbo"></my-tree-element>',
    directives: [TreeElementComponent]
})
export class TreeComponent {
    arbo:any = {name: 'Contact (form)',
        children: [
            {name: 'Layout',
            children: [
                {name: 'Form1',
                    children: [
                        {name: 'Test1'}
                    ]},
                {name: 'Form2'}
            ]},
            {name: 'Settings',
            children: [
                {name: 'Form1'},
                {name: 'Form2'}
            ]}
        ]
    }
}

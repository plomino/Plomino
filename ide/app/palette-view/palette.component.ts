import { 
    Component, 
    Input, 
    Output, 
    EventEmitter, 
    ViewChildren,
    OnInit, 
    OnChanges, 
    ContentChild,
    ChangeDetectorRef,
    NgZone,
    ChangeDetectionStrategy 
} from '@angular/core';

import { 
    CollapseDirective, 
    TAB_DIRECTIVES 
} from 'ng2-bootstrap/ng2-bootstrap';

import { DND_DIRECTIVES } from 'ng2-dnd/ng2-dnd';

import { AddComponent } from './add';
import { FieldSettingsComponent } from './fieldsettings';
import { FormSettingsComponent } from './formsettings';
import { DBSettingsComponent } from './dbsettings';

import { 
    ElementService,
    TabsService 
} from '../services';

@Component({
    selector: 'plomino-palette',
    template: require('./palette.component.html'),
    styles: [require('./palette.component.css')],
    directives: [
        CollapseDirective,
        DND_DIRECTIVES,
        TAB_DIRECTIVES,
        AddComponent,
        FieldSettingsComponent,
        FormSettingsComponent,
        DBSettingsComponent
    ],
    changeDetection: ChangeDetectionStrategy.OnPush,
    providers: [ElementService]
})
export class PaletteComponent implements OnInit {
    selectedTab: any;    
    selectedField: any;

    public tabs:Array<any> = [
        {title: 'Add', id: 'add'},
        {title: 'Field', id: 'field'},
        {title: 'Form', id: 'form'},
        {title: 'DB', id: 'db'}
    ];

    constructor(private changeDetector: ChangeDetectorRef,
                private tabsService: TabsService) { }


    
    ngOnInit() {
        this.tabsService.getActiveTab()
            .subscribe((activeTab) => {
                this.selectedTab = activeTab;
            });
        
        this.tabsService.getActiveField()
            .subscribe((activeField) => {
                this.selectedField = activeField;
            });
    }

    public setActiveTab(index:number):void {
        this.tabs[index].active = true;
    };

    onTabSelect(id: any) {
    //     setTimeout(function ():void {
    //         alert(id);
    //     });
    }
}

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

import 'lodash';
declare let _: any;

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
    selectedTab: any = null;    
    selectedField: any = null;

    tabs: Array<any> = [
        { title: 'Add', id: 'add' },
        { title: 'Field', id: 'item' },
        { title: 'Form', id: 'group' },
        { title: 'DB', id: 'db' }
    ];

    constructor(private changeDetector: ChangeDetectorRef,
                private tabsService: TabsService) { }

    ngOnInit() {
        this.tabsService.getActiveTab()
            .subscribe((activeTab) => {
                this.selectedTab = activeTab;
                if (activeTab) {
                    this.tabs = this.updateTabs(this.tabs, activeTab.type);
                }
                this.changeDetector.markForCheck();
            });
        
        this.tabsService.getActiveField()
            .subscribe((activeField) => {
                this.selectedField = activeField;
                if (activeField) {
                    this.tabs = this.updateTabs(this.tabs, this.selectedTab.type, activeField.type);
                }
                this.changeDetector.markForCheck();
            });
    }

    setActiveTab(index:number):void {
        this.tabs[index].active = true;
    };

    private updateTabs(tabs: any[], activeTabType: string, activeFieldType?: string): any[] {
        let clonnedTabs = tabs.slice(0);
        let group = _.find(clonnedTabs, { id: 'group' });
        let field = _.find(clonnedTabs, { id: 'item' });

        group.title = activeTabType === 'PlominoForm' ? 'Form' : 'View';

        if (activeFieldType) {
            field.title = activeFieldType.slice(0, 7);
        } 
        return clonnedTabs;
    }
}

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
    TabsService,
    TemplatesService,
} from '../services';

import {FormsService} from "../services/forms.service";

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
        { title: 'Add', id: 'add', active: true },
        { title: 'Field Settings', id: 'item' },
        { title: 'Form Settings', id: 'group' },
        { title: 'DB Settings', id: 'db' }
    ];

    constructor(private changeDetector: ChangeDetectorRef,
                private tabsService: TabsService,
                private formsService: FormsService,
                private templatesService: TemplatesService) { }

    ngOnInit() {
        this.tabsService.getActiveTab().subscribe((activeTab) => {
            this.selectedTab = activeTab;
            // don't track tiny-mce tab change event
            // remove when be sure
            // if (activeTab) {
            //     this.tabs = this.updateTabs(activeTab.showAdd, this.tabs, activeTab.type);
            // }
            this.changeDetector.markForCheck();
        });

        this.tabsService.getActiveField().subscribe((activeField) => {
            this.selectedField = activeField;
            if (activeField) {
                this.updateTabs(false, this.tabs, this.selectedTab && this.selectedTab.type, activeField.type);
            }
            this.changeDetector.markForCheck();
        });

        this.formsService.paletteTabChange$.subscribe((tabIndex:number) => {
            this.tabs.forEach((tab, index) => tab.active = (index === tabIndex));
            this.resizeInnerScrollingContainers();
            this.changeDetector.markForCheck();
        });
        
    }

    resizeInnerScrollingContainers() {
      const $wrapper = $('.palette-wrapper .mdl-tabs__panel');
      const $containers76 = $('.scrolling-container--76');
      const $containers66 = $('.scrolling-container--66');
      const height = parseInt($wrapper.css('height').replace('px', ''), 10);
      $containers76.css('height', `${ height - 76 }px`);
      $containers66.css('height', `${ height - 66 }px`);
    }

    setActiveTab(tabIndex: number):void {
        this.formsService.changePaletteTab(tabIndex);
    };

    private updateTabs(showAddTab: boolean, tabs: any[], activeTabType: string, activeFieldType?: string): any[] {
        let clonnedTabs = tabs.slice(0);
        let group = _.find(clonnedTabs, { id: 'group' });
        let field = _.find(clonnedTabs, { id: 'item' });

        group.title = activeTabType === 'PlominoForm' ? 'Form Settings' : 'View Settings';

        if (activeFieldType) {
            let tempTitle = activeFieldType.slice(7).toLowerCase();
            let title = tempTitle.slice(0, 1).toUpperCase() + tempTitle.slice(1);
            field.title = `${title} Settings`
            clonnedTabs.forEach((tab) => {
                tab.active = false;
            });

            clonnedTabs[1].active = true;
        } else {
            if (showAddTab) {
                clonnedTabs.forEach((tab) => {
                    tab.active = false;
                });
                clonnedTabs[0].active = true;
            }
        }
        return clonnedTabs;
    }
}

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

import { DND_DIRECTIVES } from 'ng2-dnd';

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
    selectedTab: PlominoTab = null;    
    selectedField: any = null;

    tabs: Array<any> = [
        { title: 'Add', id: 'add', active: true },
        { title: 'Field Settings', id: 'item' },
        { title: 'Form Settings', id: 'group' },
        { title: 'DB Settings', id: 'db' },
    ];

    constructor(private changeDetector: ChangeDetectorRef,
                private tabsService: TabsService,
                private formsService: FormsService,
                private templatesService: TemplatesService) { }

    ngOnInit() {
        this.tabsService.getActiveTab().subscribe((activeTab) => {
          if (activeTab && this.selectedTab 
            && activeTab.formUniqueId !== this.selectedTab.formUniqueId) {
            this.selectedTab = activeTab;
            
            this.formsService.changePaletteTab(0);
            $('.drop-zone').remove();
            // don't track tiny-mce tab change event
            // remove when be sure
            // if (activeTab) {
            //     this.tabs = this.updateTabs(activeTab.showAdd, this.tabs, activeTab.type);
            // }
            this.changeDetector.markForCheck();
          }
        });

        this.tabsService.getActiveField().subscribe((activeField) => {
            this.selectedField = activeField;
            // console.warn('ACTIVE', activeField);
            if (activeField) {
                this.updateTabs(false, this.tabs, 
                this.selectedTab && this.selectedTab.type, activeField.type);
            }
            this.changeDetector.markForCheck();
        });

        this.formsService.paletteTabChange$.subscribe((tabIndex:number) => {
          let activeChanged = false;
          this.tabs.forEach((tab, index) => {
            const isActive = (index === tabIndex);
            if (tab.active && isActive) {
              return false;
            }
            else {
              activeChanged = true;
              tab.active = isActive;
            }
          });
          if (activeChanged) {
            this.resizeInnerScrollingContainers();
            this.changeDetector.markForCheck();
          }
        });
        
    }

    resizeInnerScrollingContainers() {
      const $wrapper = $('.palette-wrapper .mdl-tabs__panel');
      const $containers76 = $('.scrolling-container--76');
      const $containers66 = $('.scrolling-container--66');
      const $containers0 = $('.scrolling-container--0');
      const height = parseInt($wrapper.css('height').replace('px', ''), 10);
      $containers76.css('height', `${ height - 76 }px`);
      $containers66.css('height', `${ height - 66 }px`);
      $containers0.css('height', `${ height }px`);
    }

    setActiveTab(tabIndex: number):void {
        this.formsService.changePaletteTab(tabIndex);
    };

    private updateTabs(showAddTab: boolean, tabs: any[], activeTabType: string, activeFieldType?: string): any[] {
        let clonnedTabs = tabs.slice(0);
        let group = _.find(clonnedTabs, { id: 'group' });
        let field = _.find(clonnedTabs, { id: 'item' });

        // console.warn('activeTabType', activeTabType, 'activeFieldType', activeFieldType);
        group.title = !activeTabType || activeTabType === 'PlominoForm' 
          ? 'Form Settings' : 'View Settings';

        if (activeFieldType) {
          let title: string;
          
          if (activeFieldType !== 'subform'
            && activeFieldType !== 'label'
            && activeFieldType !== 'group'
          ) {
            let tempTitle = activeFieldType.slice(7).toLowerCase();
            title = tempTitle.slice(0, 1).toUpperCase() + tempTitle.slice(1);
          }
          else if (activeFieldType === 'label') {
            title = 'Label';
          }
          else if (activeFieldType === 'group') {
            title = 'Group';
          }
          else {
            title = 'Subform';
          }

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

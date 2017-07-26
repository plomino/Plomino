import { URLManagerService } from './../services/url-manager.service';
import { PlominoDBService } from './../services/db.service';
import { PlominoTabsManagerService } from './../services/tabs-manager/index';
import { LogService } from './../services/log.service';
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
    PlominoFormFieldsSelectionService,
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
        DBSettingsComponent,
        PlominoWorkflowNodeSettingsComponent,
    ],
    changeDetection: ChangeDetectionStrategy.OnPush,
    providers: [ElementService]
})
export class PaletteComponent implements OnInit {
    selectedTab: any = null;    
    selectedField: any = null;
    workflowMode: boolean = false;

    tabs: Array<any> = [
        { title: 'Add', id: 'add', active: true },
        { title: 'Field Settings', id: 'item' },
        { title: 'Form Settings', id: 'group' },
<<<<<<< HEAD
        { title: 'DB Settings', id: 'db' },
        { title: 'Workflow Node', id: 'wfnode', hidden: true },
=======
        { title: 'Service', id: 'db' },
>>>>>>> upstream/advanced_ide
    ];

    constructor(private changeDetector: ChangeDetectorRef,
                private tabsService: TabsService,
                private dbService: PlominoDBService,
                private tabsManagerService: PlominoTabsManagerService,
                private formFieldsSelection: PlominoFormFieldsSelectionService,
                private formsService: FormsService,
                private log: LogService,
                private templatesService: TemplatesService,
                private urlManager: URLManagerService,
              ) { }

    ngOnInit() {
<<<<<<< HEAD
      this.tabsService.workflowModeChanged$
      .subscribe((value: boolean) => {
        if (this.workflowMode !== value) {
          this.formsService.changePaletteTab(0);
        }
        this.workflowMode = value;
        this.tabs[1].hidden = value;
        this.tabs[4].hidden = !value;
        this.changeDetector.markForCheck();
        this.changeDetector.detectChanges();
        componentHandler.upgradeDom();
      });

        this.tabsService.getActiveTab().subscribe((activeTab) => {
=======
        this.tabsManagerService.getActiveTab()
        .subscribe((tabUnit) => {

          const dbURL = this.dbService.getDBLink();
          const tabElementPath = tabUnit ? tabUnit.url.replace(dbURL, '') : '';

          const activeTab = tabUnit ? {
            label: tabUnit.label || tabUnit.id,
            url: tabUnit.url,
            editor: tabUnit.editor,
            isField: tabElementPath.split('/').length === 3
          } : null;

>>>>>>> upstream/advanced_ide
          this.log.info('activeTab', activeTab);
          this.log.extra('palette.component.ts ngOnInit');

          if (activeTab) {
            this.tabs = this.updateTabs(true, this.tabs, activeTab.editor);
          }
          
          if (activeTab && this.selectedTab 
            && activeTab.url !== this.selectedTab.url) {
            this.selectedTab = activeTab;
            
            this.formsService.changePaletteTab(0);
            $('.drop-zone').remove();
<<<<<<< HEAD
=======

            // don't track tiny-mce tab change event
            // remove when be sure
            // if (activeTab) {
            //     this.tabs = this.updateTabs(activeTab.showAdd, this.tabs, activeTab.type);
            // }
>>>>>>> upstream/advanced_ide
            this.changeDetector.markForCheck();
          }

          if (activeTab && activeTab.editor === 'code') {
            this.formsService.changePaletteTab(activeTab.isField ? 1 : 2);
            this.changeDetector.markForCheck();
          }
          else {
            this.formsService.changePaletteTab(0);
            try {
              $('a[href="#palette-tab-0-panel"]')
                .get(0).dispatchEvent(new Event('click'));
              this.changeDetector.markForCheck();
              this.changeDetector.detectChanges();
            } catch (e) {}
          }
        });

        this.formFieldsSelection.getActiveField().subscribe((activeField) => {
            this.selectedField = activeField;
            // console.warn('ACTIVE', activeField);
            if (activeField) {
                this.updateTabs(false, this.tabs, 
                this.selectedTab && this.selectedTab.editor, activeField.type);
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

    setActiveTab(ev: MouseEvent, tabIndex: number) {
      this.formsService.changePaletteTab(tabIndex);
    };

    private updateTabs(showAddTab: boolean, tabs: any[], activeTabType: string, activeFieldType?: string): any[] {
        let clonnedTabs = tabs.slice(0);
        let group = _.find(clonnedTabs, { id: 'group' });
        let field = _.find(clonnedTabs, { id: 'item' });

        if (!activeTabType && group.title === 'View Settings' 
          && (activeFieldType === 'PlominoColumn'
          || activeFieldType === 'PlominoAction')
        ) {
          group.title = 'View Settings';
        }
        else {
          group.title = !activeTabType || activeTabType === 'layout'
             || activeTabType === 'code' 
            ? 'Form Settings' : 'View Settings';
        }

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

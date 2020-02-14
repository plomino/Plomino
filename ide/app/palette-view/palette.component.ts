import { URLManagerService } from './../services/url-manager.service';
import { PlominoDBService } from './../services/db.service';
import { PlominoTabsManagerService } from './../services/tabs-manager/index';
import { PlominoWorkflowNodeSettingsComponent } from './workflow-node-settings/index';
import { LogService } from './../services/log.service';
import { 
    Component, 
    OnInit, 
    ChangeDetectorRef,
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
    selectedTab: PlominoTab = null;    
    selectedField: any = null;
    workflowMode = false;

    tabs: Array<any> = [
        { title: 'Add', id: 'add', active: true },
        { title: 'Field Settings', id: 'item' },
        { title: 'Form Settings', id: 'group' },
        { title: 'Service', id: 'db' },
        { title: 'Workflow Node', id: 'wfnode', hidden: true },
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
      this.tabsManagerService.workflowModeChanged$
      .subscribe((value: boolean) => {
        if (this.workflowMode !== value) {
          this.formsService.changePaletteTab(0);
        }
        this.workflowMode = value;

        // this.tabs[1].hidden = value;
        // this.tabs[4].hidden = !value;
        this.changeDetector.markForCheck();
        this.changeDetector.detectChanges();
        componentHandler.upgradeDom();
        $('.nav-item:has(#tab_workflow)')
          .css({ height: '42px', display: 'flex', 'align-items': 'flex-end' });
      });

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

        let j = 0;

        this.formsService.paletteTabChange$.subscribe((tabIndex: number) => {
          j++;
          let activeChanged = false;
          const x: any = [];
          this.tabs.forEach((tab, index) => {
            x.push([tabIndex, index, tab.active]);
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
            if (j > 1 && tabIndex === 3) {
              /* if any other editors are opened - do nothing */
              const tabs = this.urlManager.parseURLString();
              if (!tabs.length) {
                /* open wf */
                this.tabsManagerService.openTab({
                  id: 'workflow',
                  url: 'workflow',
                  label: 'Workflow',
                  editor: 'workflow',
                  // path: []
                });
              }
            }
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
    }

    private updateTabs(showAddTab: boolean, tabs: any[], activeTabType: string, activeFieldType?: string): any[] {
        const clonnedTabs = tabs.slice(0);
        const group = _.find(clonnedTabs, { id: 'group' });
        const field = _.find(clonnedTabs, { id: 'item' });

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
            const tempTitle = activeFieldType.slice(7).toLowerCase();
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

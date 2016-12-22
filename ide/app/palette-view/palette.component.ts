import { 
    Component, 
    Input, 
    Output, 
    EventEmitter, 
    ViewChildren, 
    OnChanges, 
    ContentChild, 
    ChangeDetectionStrategy 
} from '@angular/core';

import { 
    CollapseDirective, 
    TAB_DIRECTIVES 
} from 'ng2-bootstrap/ng2-bootstrap';

import { ElementService } from '../services/element.service';
import { DND_DIRECTIVES } from 'ng2-dnd/ng2-dnd';

import { AddComponent } from './add.component';
import { FieldSettingsComponent } from './fieldsettings.component';
import { FormSettingsComponent } from './formsettings.component';
import { DBSettingsComponent } from './dbsettings.component';


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
export class PaletteComponent {
    private _selectedTab: any;    

    @Input() set selectedTab(tab: any) {
        if (tab) {
            this._selectedTab = tab;
        } else {
            this._selectedTab = null;
        }
    }

    get selectedTab() {
        return this._selectedTab;
    }
    
    selected: any;
    
    public tabs:Array<any> = [
        {title: 'Add', id: 'add'},
        {title: 'Field', id: 'field'},
        {title: 'Form', id: 'form'},
        {title: 'DB', id: 'db'}
      ];

    public setActiveTab(index:number):void {
        this.tabs[index].active = true;
    };

    onTabSelect(id: any) {
    //     setTimeout(function ():void {
    //         alert(id);
    //     });
    }
}

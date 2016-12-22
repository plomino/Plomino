import { 
    Component, 
    Input, 
    Output, 
    EventEmitter,
    OnChanges 
} from '@angular/core';

import { ObjService } from '../services/obj.service';

@Component({
    selector: 'plomino-palette-formsettings',
    template: require('./formsettings.component.html'),
    directives: [],
    providers: []
})

export class FormSettingsComponent implements OnChanges {
    @Input() item: any = null;

    // This needs to handle both views and forms
    heading: string;
    
    constructor(private objService: ObjService) {}

    ngOnChanges() {
        console.log(`Item selected, `, this.item);
        // if (this.item) {
            // this.objService.getFormSettings()
        // }
    }
}

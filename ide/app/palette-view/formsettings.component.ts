import { 
    Component, 
    Input, 
    Output, 
    EventEmitter,
    OnChanges,
    ChangeDetectorRef,
    NgZone,
    ViewChild,
    ElementRef 
} from '@angular/core';

import { ObjService } from '../services/obj.service';
import { Observable } from 'rxjs/Observable';
import { PloneHtml } from '../custom.pipes';

declare let $: any;

@Component({
    selector: 'plomino-palette-formsettings',
    template: require('./formsettings.component.html'),
    directives: [],
    providers: [],
    pipes: [PloneHtml]
})

export class FormSettingsComponent implements OnChanges {
    @Input() item: any = null;
    @ViewChild('formElem') formElem: ElementRef; 

    // This needs to handle both views and forms
    heading: string;
    formSettings: string = '';
    
    constructor(private objService: ObjService,
                private changeDetector: ChangeDetectorRef,
                private zone: NgZone) {}

    ngOnChanges() {
        if (this.item) {
            this.objService.getFormSettings(this.item.url)
                .subscribe((template) => {
                    this.zone.run(() => {
                        this.formSettings = template;
                    });
                });
        }
    }

    saveSettings() {
        let form: HTMLFormElement = $(this.formElem.nativeElement).find('form').get(0);
        let formData: FormData = new FormData(form);
        
        formData.append('form.buttons.save', 'Save');        
        
        this.objService.updateFormSettings(this.item.url, formData)
            .flatMap((responseHtml) => {
                let $responseHtml = $(responseHtml);
                if ($responseHtml.find('dl.error')) {
                    return Observable.of(responseHtml);
                } else {
                    return this.objService.getDB();
                }
            })
            .subscribe(responseHtml => {
                    this.formSettings = responseHtml;
                    this.changeDetector.detectChanges();
                }, err => { 
                    console.error(err) 
                });
    }
}

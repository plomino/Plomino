import { 
    Component,
    OnChanges, 
    Input, 
    Output,
    ViewChild,
    ElementRef,
    ChangeDetectorRef,
    NgZone, 
    EventEmitter 
} from '@angular/core';

import { Observable } from 'rxjs/Observable';

import { ObjService } from '../services';

import { PloneHtmlPipe } from '../pipes';

import { IField } from '../interfaces';

import 'jquery';

declare let $: any;

@Component({
    selector: 'plomino-palette-fieldsettings',
    template: require('./fieldsettings.component.html'),
    directives: [],
    providers: [],
    pipes: [PloneHtmlPipe]
})

export class FieldSettingsComponent implements OnChanges {
    
    @Input() field: IField;
    @ViewChild('fieldForm') fieldForm: ElementRef;

    formTemplate: string;

    
    constructor(private objService: ObjService,
                private zone: NgZone,
                private changeDetector: ChangeDetectorRef) { }

    ngOnChanges(changes: any) {
        console.log(`Changes arrived: `, changes.field);
        if (this.field) {
            this.objService.getFieldSettings(changes.field.currentValue.url) 
                .subscribe((template) => {
                    this.zone.run(() => {
                        this.formTemplate = template;
                    });
                });
        }
    }

    submitForm() {
        let form: HTMLFormElement = $(this.fieldForm.nativeElement).find('form').get(0);
        let formData: FormData = new FormData(form);
        
        formData.append('form.buttons.save', 'Save');        
        
        this.objService.updateFormSettings(this.field.url, formData)
            .flatMap((responseHtml) => {
                let $responseHtml = $(responseHtml);
                if ($responseHtml.find('dl.error')) {
                    return Observable.of(responseHtml);
                } else {
                    return this.objService.getFieldSettings(this.field.url);
                }
            })
            .subscribe(responseHtml => {
                    this.formTemplate = responseHtml;
                    this.changeDetector.detectChanges();
                }, err => { 
                    console.error(err) 
                });
    }
}

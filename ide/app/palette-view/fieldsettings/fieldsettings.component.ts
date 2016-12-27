import { 
    Component,
    OnInit,
    OnChanges, 
    Input, 
    Output,
    ViewChild,
    ElementRef,
    ChangeDetectorRef,
    ChangeDetectionStrategy,
    EventEmitter 
} from '@angular/core';

import { Observable } from 'rxjs/Observable';

import { 
    ObjService,
    TabsService 
} from '../../services';

import { PloneHtmlPipe } from '../../pipes';

import { IField } from '../../interfaces';

import 'jquery';

declare let $: any;

@Component({
    selector: 'plomino-palette-fieldsettings',
    template: require('./fieldsettings.component.html'),
    styles: [require('./fieldsettings.component.css')],
    directives: [],
    providers: [],
    pipes: [PloneHtmlPipe],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class FieldSettingsComponent implements OnInit {
    @ViewChild('fieldForm') fieldForm: ElementRef;
    
    field: any;
    formTemplate: string = '';

    
    constructor(private objService: ObjService,
                private tabsService: TabsService,
                private changeDetector: ChangeDetectorRef) { }

    ngOnInit() {
        this.tabsService.getActiveField()
            .do((field) => {
                console.log(`Field received in fieldssettings `, field);
                this.field = field;
            })
            .flatMap((field: any) => {
                if (field && field.id) {
                    return this.objService.getFieldSettings(field.url)
                } else {
                    return Observable.of('');
                }
            })
            .subscribe((template) => {
                this.formTemplate = template;
                this.changeDetector.markForCheck();
            }) 
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
                this.changeDetector.markForCheck();
            }, err => { 
                console.error(err) 
            });
    }
}

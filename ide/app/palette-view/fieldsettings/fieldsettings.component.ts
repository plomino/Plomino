import { 
    Component,
    OnInit,
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
    directives: [],
    providers: [],
    pipes: [PloneHtmlPipe]
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

                // This is a hack, need to find out, how to get rid of it
                this.changeDetector.detectChanges();
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
                    this.changeDetector.detectChanges();
                }, err => { 
                    console.error(err) 
                });
    }
}

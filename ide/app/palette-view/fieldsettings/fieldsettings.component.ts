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
    TabsService,
    TreeService,
    FieldsService 
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
    // changeDetection: ChangeDetectionStrategy.OnPush
})

export class FieldSettingsComponent implements OnInit {
    @ViewChild('fieldForm') fieldForm: ElementRef;
    
    field: any;
    formTemplate: string = '';

    
    constructor(private objService: ObjService,
                private tabsService: TabsService,
                private fieldsService: FieldsService,
                private changeDetector: ChangeDetectorRef,
                private treeService: TreeService) { }

    ngOnInit() {
        this.loadSettings();
    }

    submitForm() {
        let $form: any = $(this.fieldForm.nativeElement);
        let form: HTMLFormElement = $form.find('form').get(0);
        let formData: FormData = new FormData(form);
        let $fieldId = $form.find('#form-widgets-IShortName-id').val().toLowerCase();
        let newUrl = this.field.url.slice(0, this.field.url.lastIndexOf('/') + 1) + $fieldId; 

        formData.append('form.buttons.save', 'Save');        
        
        this.objService.updateFormSettings(this.field.url, formData)
            .flatMap((responseHtml: string) => {
                if (responseHtml.indexOf('dl.error') > -1) {
                    return Observable.of(responseHtml);
                } else {
                    this.field.url = newUrl;
                    this.fieldsService.updateField(this.field, this.formAsObject($form), $fieldId);
                    this.field.id = $fieldId;
                    this.treeService.updateTree();
                    return this.objService.getFieldSettings(newUrl);
                }
            })
            .subscribe(responseHtml => {
                this.formTemplate = responseHtml;
                this.changeDetector.markForCheck();
            }, err => { 
                console.error(err) 
            });
    }

    cancelForm() {
        this.loadSettings();
    }

    private loadSettings() {
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
                this.changeDetector.detectChanges();
            }); 
    }

    private formAsObject(form: any): any {
        let result = {};
        let serialized = form.find('form').serializeArray();
        serialized.forEach((formItem: any) => {
            let isId = formItem.name.indexOf('IShortName.id') > -1;
            let isTitle = formItem.name.indexOf('IBasic.title') > -1;
            let isType = formItem.name.indexOf('field_type:list') > -1;
            let isWidget = formItem.name.indexOf('ITextField.widget:list') > -1;
        
            if (isId) {
                result['id'] = formItem.value;
            }

            if (isTitle) {
                result['title'] = formItem.value;
            }

            if (isType) {
                result['type'] = formItem.value.toLowerCase();
            }

            if (isWidget) {
                result['widget'] = formItem.value.toLowerCase();
            }
        });
        return result;
    }
}

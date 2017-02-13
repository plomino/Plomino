import { 
    Component,
    OnInit,
    OnChanges, 
    Input, 
    Output,
    ViewChild,
    ElementRef,
    NgZone,
    ChangeDetectorRef,
    ChangeDetectionStrategy,
    EventEmitter 
} from '@angular/core';

import { Observable } from 'rxjs/Observable';

import { 
    ObjService,
    TabsService,
    TreeService,
    FieldsService,
    FormsService
} from '../../services';

import { PloneHtmlPipe } from '../../pipes';

import { IField } from '../../interfaces';

import 'jquery';

import { LoadingComponent } from '../../editors';

@Component({
    selector: 'plomino-palette-fieldsettings',
    template: require('./fieldsettings.component.html'),
    styles: [require('./fieldsettings.component.css')],
    directives: [
        LoadingComponent
    ],
    providers: [],
    pipes: [PloneHtmlPipe],
    // changeDetection: ChangeDetectionStrategy.OnPush
})

export class FieldSettingsComponent implements OnInit {
    @ViewChild('fieldForm') fieldForm: ElementRef;
    
    field: any;
    formTemplate: string = '';

    formSaving: boolean = false;
    macrosWidgetTimer: any = null;
    
    constructor(private objService: ObjService,
                private tabsService: TabsService,
                private zone: NgZone,
                private formsService: FormsService,
                private fieldsService: FieldsService,
                private changeDetector: ChangeDetectorRef,
                private treeService: TreeService) { }

    ngOnInit() {
        this.loadSettings();

        this.formsService.formIdChanged$.subscribe(((data: any) => {
            console.info('seems that formIdChanged', data);
            if (this.field && this.field.url.indexOf(data.oldId) !== -1) {
                this.field.url = `${data.newId}/${this.formsService.getIdFromUrl(this.field.url)}`;
            }
        }).bind(this));
    }

    submitForm() {
        console.info('submit form called');
        let $form: JQuery = $(this.fieldForm.nativeElement);
        let form: HTMLFormElement = <HTMLFormElement> $form.find('form').get(0);
        let formData: FormData = new FormData(form);

        formData.append('form.buttons.save', 'Save');

        this.formSaving = true;
        
        console.info('this.objService.updateFormSettings', this.field.url, formData);
        this.objService.updateFormSettings(this.field.url, formData)
            .flatMap((responseData: any) => {
                console.info('responseData', responseData);
                if (responseData.html.indexOf('dl.error') > -1) {
                    console.info('responseData.html.indexOf(dl.error) > -1', responseData.html.indexOf('dl.error'));
                    return Observable.of(responseData.html);
                } else {
                    let $fieldId = responseData.url.slice(responseData.url.lastIndexOf('/') + 1);
                    let newUrl = this.field.url.slice(0, this.field.url.lastIndexOf('/') + 1) + $fieldId; 
                    this.field.url = newUrl;
                    console.info('its ok $fieldId', $fieldId);
                    console.info('newUrl', newUrl);
                    console.info('this.fieldsService.updateField', this.field, this.formAsObject($form), $fieldId);
                    this.fieldsService.updateField(this.field, this.formAsObject($form), $fieldId);
                    this.field.id = $fieldId;
                    console.info('this.field.id = $fieldId', this.field.id);
                    this.treeService.updateTree();
                    console.info('this.treeService.updateTree();');
                    console.info('return this.objService.getFieldSettings(newUrl);', newUrl);
                    return this.objService.getFieldSettings(newUrl);
                }
            })
            .subscribe((responseHtml: string) => {
                console.info('submitForm responseHtml received');
                this.formTemplate = responseHtml;
                this.formSaving = false;
                this.updateMacroses();
                this.changeDetector.markForCheck();
            }, (err: any) => { 
                console.error(err) 
            });
    }

    cancelForm() {
        console.info('form cancelled');
        this.loadSettings();
    }

    openFieldCode(): void {
        let $form: JQuery = $(this.fieldForm.nativeElement);
        let form: HTMLFormElement = <HTMLFormElement> $form.find('form').get(0);
        let formData: any = new FormData(form);
        const label = formData.get('form.widgets.IBasic.title');
        const urlData = this.field.url.split('/');
        const eventData = {
            formUniqueId: this.field.formUniqueId,
            editor: 'code',
            label: label,
            path: [
                { name: urlData[urlData.length - 2], type: 'Forms' },
                { name: label, type: 'Fields' }
            ],
            url: this.field.url
        };
        this.tabsService.openTab(eventData, true);
    }

    private updateMacroses() {
        if (this.field) {
            window['MacroWidgetPromise'].then((MacroWidget: any) => {
                if (this.macrosWidgetTimer !== null) {
                    clearTimeout(this.macrosWidgetTimer);
                }
                this.macrosWidgetTimer = setTimeout(() => { // for exclude bugs
                    let $el = $('.field-settings-wrapper ' + 
                    '#formfield-form-widgets-IHelpers-helpers > ul.plomino-macros');
                    if ($el.length) {
                        this.zone.runOutsideAngular(() => { new MacroWidget($el); });
                    }
                }, 200);
            });

            let formulasSelector = '';
            formulasSelector += '#formfield-form-widgets-validation_formula';
            formulasSelector += ',#formfield-form-widgets-formula';
            formulasSelector += ',#formfield-form-widgets-html_attributes_formula';
            formulasSelector += ',#formfield-form-widgets-ISelectionField-selectionlistformula';
            setTimeout(() => { $(formulasSelector).remove(); }, 500);
        }
    }

    private clickAddLink() {
      this.formsService.changePaletteTab(0);
    }

    private loadSettings() {
        console.info('load settings called');
        this.tabsService.getActiveField()
            .do((field) => {
                if (field === null) {
                    this.clickAddLink();
                }

                this.field = field;
                console.info('this.field', this.field);
            })
            .flatMap((field: any) => {
                if (field && field.id) {
                    console.info('this.objService.getFieldSettings(field.url)', field.url);
                    return this.objService.getFieldSettings(field.url)
                } else {
                    return Observable.of('');
                }
            })
            .subscribe((template) => {
                console.info('formTemplate changed');
                this.formTemplate = template;
                this.updateMacroses();
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

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

declare let $: any;

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
            if (this.field && this.field.url.indexOf(data.oldId) !== -1) {
                this.field.url = `${data.newId}/${this.formsService.getIdFromUrl(this.field.url)}`;
            }
        }).bind(this));
    }

    submitForm() {
        let $form: any = $(this.fieldForm.nativeElement);
        let form: HTMLFormElement = $form.find('form').get(0);
        let formData: FormData = new FormData(form);

        formData.append('form.buttons.save', 'Save');

        this.formSaving = true;
        
        this.objService.updateFormSettings(this.field.url, formData)
            .flatMap((responseData: any) => {
                if (responseData.html.indexOf('dl.error') > -1) {
                    return Observable.of(responseData.html);
                } else {
                    let $fieldId = responseData.url.slice(responseData.url.lastIndexOf('/') + 1);
                    let newUrl = this.field.url.slice(0, this.field.url.lastIndexOf('/') + 1) + $fieldId; 
                    this.field.url = newUrl;
                    this.fieldsService.updateField(this.field, this.formAsObject($form), $fieldId);
                    this.field.id = $fieldId;
                    this.treeService.updateTree();
                    return this.objService.getFieldSettings(newUrl);
                }
            })
            .subscribe((responseHtml: string) => {
                this.formTemplate = responseHtml;
                this.formSaving = false;
                this.updateMacroses();
                this.changeDetector.markForCheck();
            }, (err: any) => { 
                console.error(err) 
            });
    }

    cancelForm() {
        this.loadSettings();
    }

    private updateMacroses() {
        if (this.field) {
            window['MacroWidgetPromise'].then((MacroWidget: any) => {
                setTimeout(() => { // for exclude bugs
                    let $el = $('.field-settings-wrapper ' + 
                    '#formfield-form-widgets-IHelpers-helpers > ul.plomino-macros');
                    if ($el.length) {
                        this.zone.runOutsideAngular(() => { new MacroWidget($el); });
                    }
                }, 200);
            });
        }
    }

    private clickAddLink() {
        const $addLink = $('plomino-palette > tabset > ul > li > a > span:contains("Add")');
        if ($addLink.length !== 0) {
            $addLink.click();
        }
    }

    private loadSettings() {
        this.tabsService.getActiveField()
            .do((field) => {
                if (field === null) {
                    this.clickAddLink();
                }

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

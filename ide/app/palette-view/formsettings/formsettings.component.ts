import { 
    Component, 
    Input, 
    Output, 
    EventEmitter,
    OnInit,
    OnChanges,
    ChangeDetectorRef,
    NgZone,
    ViewChild,
    ElementRef,
    ChangeDetectionStrategy 
} from '@angular/core';

import { Observable } from 'rxjs/Observable';

import { 
    ObjService,
    TabsService,
    TreeService,
    FormsService
} from '../../services';
import { PloneHtmlPipe } from '../../pipes';
import {ElementService} from "../../services/element.service";
import {WidgetService} from "../../services/widget.service";

declare let $: any;

import { LoadingComponent } from '../../editors';

@Component({
    selector: 'plomino-palette-formsettings',
    template: require('./formsettings.component.html'),
    styles: [require('./formsettings.component.css')],
    directives: [
        LoadingComponent
    ],
    providers: [],
    pipes: [PloneHtmlPipe],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class FormSettingsComponent implements OnInit {
    @ViewChild('formElem') formElem: ElementRef; 
    
    tab: any;

    formSaving:boolean = false;

    // This needs to handle both views and forms
    heading: string;
    formSettings: string = '';
    private formLayout: string = '';
    
    constructor(private objService: ObjService,
                private changeDetector: ChangeDetectorRef,
                private tabsService: TabsService,
                private treeService: TreeService,
                private elementService: ElementService,
                private widgetService: WidgetService,
                private formsService: FormsService) {}

    ngOnInit() {
        this.getSettings();

        this.formsService.formSettingsSave$.subscribe((data) => {
            if(this.tab.formUniqueId !== data.formUniqueId)
                return;

            this.saveForm(data.cb)
        });
    }

    saveFormSettings(formData:any, cb:any) {

        this.formSaving = true;
        let $formId:any = '';

        this.objService.updateFormSettings(this.tab.url, formData)
            .flatMap((responseData: any) => {
                if (responseData.html.indexOf('dl.error') > -1) {
                    return Observable.of(responseData.html);
                } else {
                    $formId = responseData.url.slice(responseData.url.lastIndexOf('/') + 1);
                    let newUrl = this.tab.url.slice(0, this.tab.url.lastIndexOf('/') + 1) + $formId;
                    let oldUrl = this.tab.url;

                    if (newUrl && oldUrl && newUrl !== oldUrl) {
                        this.formsService.changeFormId({
                            newId: newUrl,
                            oldId: oldUrl
                        });

                        this.tabsService.updateTabId(this.tab, $formId);

                        this.changeDetector.markForCheck();
                    }

                    this.changeDetector.markForCheck();

                    return this.objService.getFormSettings(newUrl);
                }
            })
            .subscribe(responseHtml => {

                this.treeService.updateTree().then(() => {
                    this.formSaving = false;
                    this.formSettings = responseHtml;
                    this.changeDetector.markForCheck();
                    if (cb) {
                        cb();
                    }
                });
            }, err => {
                console.error(err)
            });
    }

    submitForm() {
        this.formsService.saveForm(this.tab.formUniqueId);
        this.changeDetector.markForCheck();
    }

    saveForm(cb:any) {
        let $form: any = $(this.formElem.nativeElement);
        let form: HTMLFormElement = $form.find('form').get(0);
        let formData: any = new FormData(form);

        this.treeService.updateTree();

        formData.append('form.buttons.save', 'Save');

        this.saveFormSettings(formData, cb);
    }

    cancelForm() {
        this.getSettings();
    }

    openFormPreview(formUrl: string): void {
        window.open(`${formUrl}/OpenForm`);
    }

    private getSettings() {
        this.tabsService.getActiveTab()
            .do((tab) => {
                this.tab = tab;
            })
            .flatMap((tab: any) => {
                if (tab) {
                    return this.objService.getFormSettings(tab.url);
                } else {
                    return Observable.of('');
                }
            })
            .subscribe((template) => {
                // $template.find('#formfield-form-widgets-form_layout').css('display', 'none');
                // console.log(this.formSettings = $template.innerHTML);
                // this.formSettings = $template.wrap('<div />').parent().html();
                this.formSettings = template;
                this.changeDetector.markForCheck();
            });
    }
}

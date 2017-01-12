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
    TreeService 
} from '../../services';
import { PloneHtmlPipe } from '../../pipes';
import {ElementService} from "../../services/element.service";
import {WidgetService} from "../../services/widget.service";

declare let $: any;

@Component({
    selector: 'plomino-palette-formsettings',
    template: require('./formsettings.component.html'),
    styles: [require('./formsettings.component.css')],
    directives: [],
    providers: [],
    pipes: [PloneHtmlPipe],
    changeDetection: ChangeDetectionStrategy.OnPush
})

export class FormSettingsComponent implements OnInit {
    @ViewChild('formElem') formElem: ElementRef; 
    
    tab: any;

    // This needs to handle both views and forms
    heading: string;
    formSettings: string = '';
    
    constructor(private objService: ObjService,
                private changeDetector: ChangeDetectorRef,
                private tabsService: TabsService,
                private treeService: TreeService,
                private elementService: ElementService,
                private widgetService: WidgetService) {}

    ngOnInit() {
        this.getSettings();
    }

    getElementFormLayout(id:any, formData:FormData, callback:any) {
        this.elementService.getElementFormLayout(id)
            .subscribe((data) => {
                if (data && data.length) {
                    this.widgetService.getFormLayout(this.tab.url, data)
                        .subscribe((formLayout: string) => {
                            callback(formData, formLayout)
                        });
                } else {
                    callback(formData, null);
                }
            }, (err) => {
                console.error(err);
            });
    }

    updateFormSettings(formData:any, formLayout:any) {
        formData.set('form.widgets.form_layout', formLayout);

        this.objService.updateFormSettings(this.tab.url, formData)
            .flatMap((responseData: any) => {
                if (responseData.html.indexOf('dl.error') > -1) {
                    return Observable.of(responseData.html);
                } else {
                    let $formId = responseData.url.slice(responseData.url.lastIndexOf('/') + 1);
                    let newUrl = this.tab.url.slice(0, this.tab.url.lastIndexOf('/') + 1) + $formId;
                    // this.tab.url = newUrl;
                    this.tabsService.updateTab(this.tab, $formId);
                    this.treeService.updateTree();
                    return this.objService.getFormSettings(newUrl);
                }
            })
            .subscribe(responseHtml => {
                this.formSettings = responseHtml;
                this.changeDetector.markForCheck();
            }, err => {
                console.error(err)
            });
    }

    submitForm() {

        let $form: any = $(this.formElem.nativeElement);
        let form: HTMLFormElement = $form.find('form').get(0);
        let formData: any = new FormData(form);
        
        formData.append('form.buttons.save', 'Save');

        this.getElementFormLayout(this.tab.url, formData, this.updateFormSettings.bind(this));
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

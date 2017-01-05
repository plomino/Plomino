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
                private treeService: TreeService) {}

    ngOnInit() {
        this.getSettings();
    }

    submitForm() {
        let $form: any = $(this.formElem.nativeElement);
        let form: HTMLFormElement = $form.find('form').get(0);
        let formData: FormData = new FormData(form);
        let $formId = $form.find('#form-widgets-IShortName-id').val().toLowerCase();
        let newUrl = this.tab.url.slice(0, this.tab.url.lastIndexOf('/') + 1) + $formId; 
        
        formData.append('form.buttons.save', 'Save');        
        
        this.objService.updateFormSettings(this.tab.url, formData)
            .flatMap((responseHtml: string) => {
                if (responseHtml.indexOf('dl.error') > -1) {
                    return Observable.of(responseHtml);
                } else {
                    this.tab.url = newUrl;
                    this.tabsService.updateTab(this.tab, $formId);
                    this.tab.id = $formId;
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

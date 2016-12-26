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
    ElementRef 
} from '@angular/core';

import { Observable } from 'rxjs/Observable';

import { 
    ObjService,
    TabsService 
} from '../../services';
import { PloneHtmlPipe } from '../../pipes';

declare let $: any;

@Component({
    selector: 'plomino-palette-formsettings',
    template: require('./formsettings.component.html'),
    directives: [],
    providers: [],
    pipes: [PloneHtmlPipe]
})

export class FormSettingsComponent implements OnInit {
    @ViewChild('formElem') formElem: ElementRef; 
    
    tab: any;

    // This needs to handle both views and forms
    heading: string;
    formSettings: string = '';
    
    constructor(private objService: ObjService,
                private changeDetector: ChangeDetectorRef,
                private tabsService: TabsService) {}

    ngOnInit() {
        this.tabsService.getActiveTab()
            .do((tab) => {
                this.tab = tab;
            })
            .flatMap((tab: any) => {
                if (tab) {
                    return this.objService.getFormSettings(tab.url)
                } else {
                    return Observable.of('');
                }
            })
            .subscribe((template) => {
                this.formSettings = template;
                // This is a hack, need to find out, how to get rid of it
                this.changeDetector.detectChanges();
            });
    }

    saveSettings() {
        let form: HTMLFormElement = $(this.formElem.nativeElement).find('form').get(0);
        let formData: FormData = new FormData(form);
        
        formData.append('form.buttons.save', 'Save');        
        
        this.objService.updateFormSettings(this.tab.url, formData)
            .flatMap((responseHtml) => {
                let $responseHtml = $(responseHtml);
                if ($responseHtml.find('dl.error')) {
                    return Observable.of(responseHtml);
                } else {
                    return this.objService.getFormSettings(this.tab.url);
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

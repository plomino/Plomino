import { 
    Component, 
    Input, 
    Output,
    EventEmitter, 
    ViewChild, 
    ElementRef,
    ChangeDetectorRef
} from '@angular/core';

import { 
    Http, 
    Headers, 
    Response, 
    RequestOptions 
} from '@angular/http';

import { Observable } from 'rxjs/Rx';
import { ObjService } from '../../services/obj.service';
import { PloneHtmlPipe } from '../../pipes';

declare var $: any;

@Component({
    selector: 'plomino-palette-dbsettings',
    template: require('./dbsettings.component.html'),
    directives: [],
    providers: [ObjService],
    pipes: [PloneHtmlPipe],
})

export class DBSettingsComponent {

    @ViewChild('dbform') el:ElementRef;

    dbForm: any;

    constructor(private _objService: ObjService,
                private changeDetector: ChangeDetectorRef) { }

    submit() {
        // this.el is the div that contains the Edit Form
        // We want to seralize the data in the form, submit it to the form
        // action. If the response is <div class="ajax_success">, we re-fetch
        // the form. Otherwise we update the displayed form with the response
        // (which may have validation failures etc.) 
        let form: HTMLFormElement = $(this.el.nativeElement).find('form').get(0);
        let formData: FormData = new FormData(form);
        
        formData.append('form.buttons.save', 'Save');
        
        this._objService.submitDB(formData)
            .flatMap((responseHtml) => {
                let $responseHtml = $(responseHtml);
                if ($responseHtml.find('dl.error')) {
                    return Observable.of(responseHtml);
                } else {
                    return this._objService.getDB();
                }
            })
            .subscribe(responseHtml => {
                    this.dbForm = responseHtml;
                    this.changeDetector.detectChanges();
                }, err => { 
                    console.error(err) 
                });
    }

    ngOnInit() {
        this._objService.getDB().subscribe(html => { 
            this.dbForm = html 
        }, err => { 
            console.error(err);
        });
    }

}



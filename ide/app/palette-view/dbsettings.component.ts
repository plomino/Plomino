import { Component, Input, Output, EventEmitter, ViewChild, ElementRef } from '@angular/core';
import { Http, Headers, Response, RequestOptions } from '@angular/http';
import { ObjService }                   from '../services/obj.service';
import { PloneHtml } from '../custom.pipes';

declare var $: any;

@Component({
    selector: 'plomino-palette-dbsettings',
    template: require('./dbsettings.component.html'),
    directives: [],
    providers: [ObjService],
    pipes: [PloneHtml],
})

export class DBSettingsComponent {

    @ViewChild('dbform') el:ElementRef;

    dbForm: any;

    constructor(private _objService: ObjService) { }

    saved() {
        // this.el is the div that contains the Edit Form
        // We want to seralize the data in the form, submit it to the form
        // action. If the response is <div class="ajax_success">, we re-fetch
        // the form. Otherwise we update the displayed form with the response
        // (which may have validation failures etc.) 
        console.log(this.el.nativeElement);
    }

    ngOnInit() {
        // Fetch the DB form from the object service
        this.getDBForm();
    }

    getDBForm() {
        this._objService.getDB()
            .subscribe(
                html => { this.dbForm = html },
                err => console.error(err)
            );
    }

}



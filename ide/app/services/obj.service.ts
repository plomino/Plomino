import { Injectable } from '@angular/core';
import { 
    Http, 
    Headers, 
    Response, 
    RequestOptions
} from '@angular/http';

import { Observable } from 'rxjs/Observable';

@Injectable()
export class ObjService {
    // For handling the injection/fetching/submission of Plomino objects

    constructor(private http:Http) {
        let headers = new Headers({ 'Content-Type': 'text/html' });
        let options = new RequestOptions({ headers: headers });
    }

    getFormSettings(formUrl: any): Observable<any> {
        return this.http.get(formUrl).map(this.extractText);
    }

    updateFormSettings(formUrl: any, formData: any): Observable<any> {
        return this.http.post(formUrl, formData).map(this.extractText);
    }

    // Change this to use Promises/Observable pattern
    getDB(): Observable<any> {
        return this.http.get("../../edit?ajax_load=1&ajax_include_head=1")
            .map(this.extractText);
    }

    // Form should be a jquery form object
    submitDB(form: any): Observable<any> {
        var inputs = form.serialize();
        // Action will always be @@edit
        // var action = form.attr('action')
        return this.http.post("../../@@edit", inputs)
            .map(this.extractText);
    }

    private extractText(response: Response): any {
        return response.text();
    }
}

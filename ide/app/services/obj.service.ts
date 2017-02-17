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
    
    getFieldSettings(fieldUrl: string): Observable<any> {
        console.info('getFieldSettings called', fieldUrl);
        return this.http.get(`${fieldUrl}/@@edit?ajax_load=1&ajax_include_head=1`)
                    .map(this.extractText);
    }

    updateFieldSettings(fieldUrl: string, formData: FormData): Observable<any> {
        return this.http.post(`${fieldUrl}/@@edit`, formData)
                    .map(this.extractTextAndUrl);
    }
    
    getFormSettings(formUrl: string): Observable<any> {
        console.info('getFormSettings called', formUrl);
        return this.http.get(`${formUrl}/@@edit?ajax_load=1&ajax_include_head=1`)
                    .map(this.extractText);
    }

    
    updateFormSettings(formUrl: string, formData: FormData): Observable<any> {
      console.info('updateFormSettings', formUrl, (<any>formData).entries());
      //<p><span class="plominoHidewhenClass mceNonEditable" data-plominoid="defaulthidewhen-1" data-plomino-position="start">&nbsp;</span><span class="plominoHidewhenClass mceNonEditable" data-plominoid="defaulthidewhen-1" data-plomino-position="end">&nbsp;</span>&nbsp;</p>
        return this.http.post(`${formUrl}/@@edit`, formData)
                    .map(this.extractTextAndUrl);
    }



    // Change this to use Promises/Observable pattern
    getDB(): Observable<any> {
        return this.http.get("../../@@edit?ajax_load=1&ajax_include_head=1")
            .map(this.extractText);
    }

    // Form should be a jquery form object
    submitDB(formData: FormData): Observable<any> {
        return this.http.post("../../@@edit", formData)
            .map(this.extractText);
    }

    private extractText(response: Response): any {
        return response.text();
    }

    private extractTextAndUrl(response: Response): any {
        return {
            html: response.text(),
            url: response.url.slice(0, response.url.indexOf('@') - 1)
        }
    }
}

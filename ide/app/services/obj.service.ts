import {Injectable} from '@angular/core';
import {Http, Headers, Response, RequestOptions} from '@angular/http';

@Injectable()
export class ObjService {
    // For handling the injection/fetching/submission of Plomino objects

    constructor(private http:Http) {
        let headers = new Headers({ 'Content-Type': 'text/html' });
        let options = new RequestOptions({ headers: headers });
    }

    // Change this to use Promises/Observable pattern
    getDB() {
        return this.http.get("../../edit?ajax_load=1&ajax_include_head=1").map((res: Response) => res.text() );
    }

    // Form should be a jquery form object
    submitDB(form: any) {
        var inputs = form.serialize();
        // Action will always be @@edit
        // var action = form.attr('action')
        return this.http.post("../../@@edit", inputs).map((res: Response) => res.text() );
    }
}

import {Injectable} from 'angular2/core';
import {Http, Headers, Response} from 'angular2/http';

@Injectable()
export class ElementService {

    headers: Headers;

    constructor(private http: Http) {
        this.headers = new Headers();
        this.headers.append('Accept', 'application/json');
        this.headers.append('Content-Type', 'application/json');
    }

    getElement(url: string) {
        return this.http.get(url, { headers: this.headers }).map((res: Response) => res.json());
    }

    patchElement(id: string, element: any) {
        this.http
        .patch(id,
        element, {
            headers: this.headers
        })
        .map(response => response === null ? null : response)
        .subscribe(
            //
        );
    }
}

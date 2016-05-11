import {Injectable} from 'angular2/core';
import {Http, Headers, Response} from 'angular2/http';

@Injectable()
export class ElementService {

    getheader: Headers;

    constructor(private http: Http) {
        this.getheader = new Headers();
        this.getheader.append('Accept', 'application/json');
    }

    getElement(url: string) {
        return this.http.get(url, {headers: this.getheader}).map((res:Response) => res.json());
    }
}

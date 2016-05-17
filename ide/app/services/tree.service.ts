import {Injectable} from '@angular/core';
import {Http, Response} from '@angular/http';

@Injectable()
export class TreeService {

    constructor(private http: Http) { }
    getTree() {
        return this.http.get('http://localhost:8080/Plone/plominodatabase/@@designtree').map((res: Response) => res.json() );
    }
}

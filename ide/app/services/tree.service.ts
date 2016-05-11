import {Injectable} from 'angular2/core';
import {Http, Response} from 'angular2/http';

@Injectable()
export class TreeService {

    constructor(private http: Http) { }
    getTree() {
        return this.http.get('../../@@designtree').map((res:Response) => res.json());
    }
}

import {Injectable} from '@angular/core';
import {Http, Headers, Response} from '@angular/http';

@Injectable()
export class ElementService {

    headers: Headers;

    constructor(private http: Http) {
        this.headers = new Headers();
        this.headers.append('Accept', 'application/json');
        this.headers.append('Content-Type', 'application/json');
    }

    getElement(id: string) {
        return this.http.get(id, { headers: this.headers }).map((res: Response) => res.json());
    }

    // Had some issues with TinyMCEComponent, had to do this instead of using getElement() method
    // XXX: This should really call the getForm_layout method on the Form object?
    getElementFormLayout(id: string) {
        return this.http.get(id, { headers: this.headers }).map((res: Response) => res.json().form_layout);
    }

    getElementCode(url: string) {
        return this.http.get(url).map((res: Response) => res.text());
    }

    postElementCode(url: string, type: string, id: string, code: string) {
        let headers = new Headers()
        headers.append('Content-Type', 'application/json');
        return this.http.post(url, JSON.stringify({"Type": type, "Id": id, "Code": code}), { headers: headers })
            .map((res: Response) => res.json());
    }

    patchElement(id: string, element: any) {
        return this.http.patch(id, element, { headers: this.headers });
    }

    // XXX: Docs for debugging:
    // http://plonerestapi.readthedocs.io/en/latest/crud.html#creating-a-resource-with-post

    postElement(url: string, newElement: any) {
        let headers = new Headers();
        headers.append('Content-Type', 'application/json');
        if(newElement['@type']=='PlominoField') {
            url = url + '/@@add-field'
            headers.append('Accept', '*/*');
        } else {
            headers.append('Accept', 'application/json');
        }

        // A form must have an empty layout
        if (newElement['@type'] == 'PlominoForm') {
            newElement.form_layout = '';
        }

        return this.http.post(url, JSON.stringify(newElement), { headers: headers })
            .map((res: Response) => res.json());
    }

    deleteElement(url: string) {
        return this.http.delete(url);
    }

    searchElement(query: string) {
        return this.http.get('../../search?SearchableText='+query+'*', { headers: this.headers }).map((res: Response) => res.json());
    }
}

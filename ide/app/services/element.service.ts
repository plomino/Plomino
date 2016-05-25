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
    getElementFormLayout(id: string) {
        return this.http.get(id, { headers: this.headers }).map((res: Response) => res.json().form_layout)
    }

    getElementCode(url: string) {
        // TODO : remove hardcoded url
        return this.http.get(url).map((res: Response) => res.text());
    }

    patchElement(id: string, element: any) {
        this.http.patch(id,element, { headers: this.headers })
        .map(response => response === null ? null : response).subscribe();
    }

    searchElement(query: string) {
        // TODO : remove hardcoded url
        return this.http.get('http://localhost:8080/Plone/plominodatabase/search?SearchableText='+query+'*', { headers: this.headers }).map((res: Response) => res.json());
    }
}

import { LogService } from './log.service';
import { PlominoHTTPAPIService } from './http-api.service';
import { Injectable } from '@angular/core';

import { 
    Headers, 
    Response
} from '@angular/http';

import { Observable } from 'rxjs/Rx';

@Injectable()
export class ElementService {

  headers: Headers;

  constructor(private http: PlominoHTTPAPIService, private log: LogService) {
    this.headers = new Headers();
    this.headers.append('Accept', 'application/json');
    this.headers.append('Content-Type', 'application/json');
  }

  getElement(id: string): Observable<PlominoFieldDataAPIResponse> {
    return this.http.getWithOptions(
      id, { headers: this.headers },
      'element.service.ts getElement'
    ).map((res: Response) => res.json());
  }

  // Had some issues with TinyMCEComponent, had to do this instead of using getElement() method
  // XXX: This should really call the getForm_layout method on the Form object?
  getElementFormLayout(id: string): Observable<PlominoFormDataAPIResponse> {
    return this.http.getWithOptions(
      id, { headers: this.headers },
      'element.service.ts getElementFormLayout'
    ).map((res: Response) => res.json());
  }

  getElementCode(url: string) {
    return this.http.get(
      url, 'element.service.ts getElementCode'
    ).map((res: Response) => res.text());
  }

  postElementCode(url: string, type: string, id: string, code: string) {
    let headers = new Headers()
    headers.append('Content-Type', 'application/json');
    return this.http.postWithOptions(
      url, JSON.stringify({"Type": type, "Id": id, "Code": code}),
      { headers },
      'element.service.ts postElementCode'
    )
    .map((res: Response) => res.json());
  }

  patchElement(id: string, element: any) {
    return this.http.patch(id, element, 'element.service.ts patchElement');
  }

  // XXX: Docs for debugging:
  // http://plonerestapi.readthedocs.io/en/latest/crud.html#creating-a-resource-with-post

  postElement(url: string, newElement: InsertFieldEvent): Observable<AddFieldResponse> {
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

    return this.http.postWithOptions(
      url, JSON.stringify(newElement), { headers },
      'element.service.ts postElement'
    )
    .map((res: Response) => res.json());
  }

  deleteElement(url: string) {
    return this.http.delete(url, 'element.service.ts deleteElement');
  }

  searchElement(query: string) {
    return this.http.getWithOptions(
      '../../search?SearchableText='+query+'*',
      { headers: this.headers },
      'element.service.ts searchElement'
    ).map((res: Response) => res.json());
  }

  getWidget(base: string, type: string, id: string, newTitle?: string): Observable<string> {
    this.log.info('type', type, 'id', id, 'newTitle', newTitle);
    this.log.extra('element.service.ts getWidget');
    if (type === 'label') {
      return Observable.of(
        `<span class="plominoLabelClass mceEditable"
          ${ id ? `data-plominoid="${ id }"` : '' }>${ newTitle }</span>`
      );
    }
    return this.http.get(
      `${base}/@@tinyform/example_widget?widget_type=${type}${ id ? `&id=${id}` : '' }`,
      'element.service.ts getWidget')
      .map((response) => response.json());
  }
}

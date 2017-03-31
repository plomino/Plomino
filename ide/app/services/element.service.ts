import { PlominoElementAdapterService } from './element-adapter.service';
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
  confirmDialog: HTMLDialogElement;

  constructor(
    private http: PlominoHTTPAPIService, private log: LogService,
    private adapter: PlominoElementAdapterService
  ) {
    this.headers = new Headers();
    this.headers.append('Accept', 'application/json');
    this.headers.append('Content-Type', 'application/json');

    this.confirmDialog = <HTMLDialogElement> 
      document.querySelector('#confirm-dialog');
  }

  awaitForConfirm(text = 'Do you agree to delete this object?'): Promise<boolean> {
    this.confirmDialog
      .querySelector('.mdl-dialog__content')
      .innerHTML = text;
    this.confirmDialog.showModal();
    return new Promise((resolve, reject) => {
      $(this.confirmDialog)
        .find('.close').off('click.confirm')
        .on('click.confirm', () => {
          reject(false);
          this.confirmDialog.close();
        });
      $(this.confirmDialog)
        .find('.agree').off('click.confirm')
        .on('click.confirm', () => {
          resolve(true);
          this.confirmDialog.close();
        });
      });
  }

  getElement(id: string): Observable<PlominoFieldDataAPIResponse> {
    if (id.split('/').pop() === 'defaultLabel') {
      return Observable.of(null);
    }
    return this.http.getWithOptions(
      id, { headers: this.headers },
      'element.service.ts getElement'
    ).map((res: Response) => res.json());
  }

  // Had some issues with TinyMCEComponent, had to do this instead of using getElement() method
  // XXX: This should really call the getForm_layout method on the Form object?
  getElementFormLayout(formUrl: string): Observable<PlominoFormDataAPIResponse> {
    if (this.http.recentlyChangedFormURL !== null
      && this.http.recentlyChangedFormURL[0] === formUrl
      && $('.tab-name').toArray().map((e) => e.innerText)
      .indexOf(formUrl.split('/').pop()) === -1
    ) {
      formUrl = this.http.recentlyChangedFormURL[1];
      this.log.info('patched formUrl!', this.http.recentlyChangedFormURL);
      this.log.extra('element.service.ts getElementFormLayout');
    }
    return this.http.getWithOptions(
      formUrl, { headers: this.headers },
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
        this.adapter.endPoint('label', `<span class="plominoLabelClass mceNonEditable"
          ${ id ? `data-plominoid="${ id }"` : '' }>${ newTitle || 'Untitled' }</span>`
      ));
    }
    return this.http.get(
      `${base}/@@tinyform/example_widget?widget_type=${type}${ id ? `&id=${id}` : '' }`,
      'element.service.ts getWidget')
      .map((response: any) => response.json());
  }
}

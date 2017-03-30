import { Observable } from 'rxjs/Rx';
import { Headers, Response, RequestOptions } from '@angular/http';
import { PlominoHTTPAPIService } from './../../services/http-api.service';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoViewsAPIService {

  constructor(
    private http: PlominoHTTPAPIService
  ) { }

  fetchViewTableHTML(url: string): Observable<string> {
    return this.http
      .get(`${ url }/view?ajax_load=1&ajax_include_header=1`)
      .map((response: Response) => response.text())
  }

  addNewColumn(url: string, id = 'default-column'): Observable<boolean> {
    const token = this.getCSRFToken();
    const form = new FormData();

    form.set('form.widgets.IShortName.id', id);
    form.set('form.widgets.IBasic.title', id);
    form.set('form.widgets.displayed_field:list', '--NOVALUE--');
    form.set('form.widgets.displayed_field-empty-marker', '1');
    form.set('form.widgets.hidden_column-empty-marker', '1');
    form.set('ajax_load', '');
    form.set('ajax_include_head', '');
    form.set('form.widgets.IHelpers.helpers:list', '');
    form.set('form.widgets.formula', '');
    form.set('form.widgets.IBasic.description', '');
    form.set('form.buttons.save', 'Save');
    form.set('_authenticator', token);

    return this.http
      .postWithOptions(`${ url }/++add++PlominoColumn`, form, 
        new RequestOptions({}), 'views-api.service.ts addNewColumn')
      .map((response: Response) => true);
  }

  dragColumn(url: string, id: string, delta: number, subsetIds: string[]): Observable<any> {
    const token = this.getCSRFToken();

    const options = {
      delta, id, subsetIds,
      _authenticator: token
    };

    // const formData = new FormData();

    // for (let key in options) {
    //     formData.append(key, options[key]);
    // }
    
    return this.http
      .postWithOptions(`${ url }/fc-itemOrder`, $.param(options), new RequestOptions({
        headers: new Headers({
          'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
          'X-CSRF-TOKEN': token,
          'X-Requested-With': 'XMLHttpRequest',
        })
      }), 'views-api.service.ts dragColumn')
      .map((response: Response) => response.json())
  }

  getCSRFToken() {
    const script = document.getElementById('protect-script');
    const token = script.getAttribute('data-token');

    return token;
  }
}

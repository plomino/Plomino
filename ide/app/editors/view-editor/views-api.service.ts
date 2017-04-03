import { ElementService } from './../../services/element.service';
import { Observable } from 'rxjs/Rx';
import { Headers, Response, RequestOptions } from '@angular/http';
import { PlominoHTTPAPIService } from './../../services/http-api.service';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoViewsAPIService {

  constructor(
    private http: PlominoHTTPAPIService,
    private elementService: ElementService,
  ) { }

  fetchViewTableHTML(url: string): Observable<string> {
    return this.http
      .get(`${ url }/view?ajax_load=1&ajax_include_header=1`)
      .map((response: Response) => response.text())
  }

  fetchViewTableDataJSON(url: string): Observable<PlominoVocabularyViewData> {
    let reqURL = '/Plone/@@getVocabulary?name=plone.app.vocabularies.Catalog';
    reqURL += '&query={%22criteria%22:[{%22i%22:%22path%22,%22o%22:%22';
    reqURL += 'plone.app.querystring.operation.string.path%22,%22v%22:%22/';
    reqURL += url.split('/').slice(-2).join('/');
    reqURL += '::1%22}],%22sort_on%22:%22getObjPositionInParent%22,';
    reqURL += '%22sort_order%22:%22ascending%22}&batch={%22page%22:1,%22size%22:100}';
    reqURL += '&attributes=[%22id%22,%22Type%22]';
    return this.http
      .get(reqURL)
      .map((response: Response) => response.json())
      .catch((err: any) => {
        return Observable.of({ results: [], total: 0 });
      })
  }

  fetchViewTable(url: string): Observable<[string, PlominoVocabularyViewData]> {
    const html$ = this.fetchViewTableHTML(url);
    const json$ = this.fetchViewTableDataJSON(url);
    return <Observable<[string, PlominoVocabularyViewData]>> Observable.forkJoin(html$, json$);
  }

  addNewAction(url: string, id = 'default-action'): Observable<AddFieldResponse> {
    const field = {
      title: 'default-action',
      action_type: 'OPENFORM',
      '@type': 'PlominoAction',
    }
    return this.elementService.postElement(url, field);
  }

  addNewColumn(url: string, id = 'default-column'): Observable<string> {
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
      .map((response: Response) => {
        return response.url.replace('/view', '').split('/').pop();
      });
  }

  reOrderItem(url: string, id: string, delta: number, subsetIds: string[]): Observable<any> {
    const token = this.getCSRFToken();

    const options = {
      delta, id, subsetIds,
      _authenticator: token
    };
    
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

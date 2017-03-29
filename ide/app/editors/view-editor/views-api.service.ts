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

  dragColumn(url: string, id: string, delta: number, subsetIds: string[]): Observable<any> {
    const script = document.getElementById('protect-script');
    const token = script.getAttribute('data-token');

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
}

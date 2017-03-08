import { Observable } from 'rxjs/Rx';
import { LogService } from './log.service';
import { Http, Headers, Response } from '@angular/http';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoHTTPAPIService {
  headers: Headers = new Headers();
  okDialog: HTMLDialogElement;
        
  constructor(private http: Http, private log: LogService) {
    this.headers.append('Accept', 'application/json');
    this.headers.append('Content-Type', 'application/json');
    this.okDialog = <HTMLDialogElement> 
        document.querySelector('#ok-dialog');

    if (!this.okDialog.showModal) {
      dialogPolyfill.registerDialog(this.okDialog);
    }

    this.okDialog.querySelector('.mdl-dialog__actions button')
    .addEventListener('click', () => {
      this.okDialog.close();
    });
  }

  get(url: string, debugInformation?: string) {
    this.log.info(`GET -> ${ url }`);
    if (debugInformation) {
      this.log.extra(debugInformation);
    }
    return this.http.get(url)
      .map(this.getErrors)
      .catch(this.throwError);
  }

  getWithOptions(url: string, options: any, debugInformation?: string) {
    this.log.info(`GET<H> -> ${ url }`);
    if (debugInformation) {
      this.log.extra(debugInformation);
    }
    return this.http.get(url, options)
      .map(this.getErrors)
      .catch(this.throwError);
  }

  delete(url: string, debugInformation?: string) {
    this.log.info(`DELETE -> ${ url }`);
    if (debugInformation) {
      this.log.extra(debugInformation);
    }
    return this.http.delete(url, { headers: this.headers });
  }

  post(url: string, data: any, debugInformation?: string) {
    this.log.info(`POST -> ${ url }`);
    if (debugInformation) {
      this.log.extra(debugInformation);
    }
    return this.http.post(url, data, { headers: this.headers })
      .map(this.getErrors)
      .catch(this.throwError);
  }

  postWithOptions(url: string, data: any, options: any, debugInformation?: string) {
    this.log.info(`POST<H> -> ${ url }`);
    if (debugInformation) {
      this.log.extra(debugInformation);
    }
    return this.http.post(url, data, options)
      .map(this.getErrors)
      .catch(this.throwError);
  }

  getErrors(response: Response) {
    if (response.status === 500) {
      const tmp = response.json();
      throw tmp.error_type || tmp.toString();
    }
    else if (response.status === 401) {
      const tmp = response.json();
      throw tmp.message || tmp.toString();
    }
    else {
      return response;
    }
  }

  throwError(error: any) {
    const okDialog = <HTMLDialogElement> document.querySelector('#ok-dialog');
    okDialog.querySelector('.mdl-dialog__content')
      .innerHTML = `<p>${ error }</p>`;
    okDialog.showModal();
    return Observable.throw(error);
  }

  patch(url: string, data: any, debugInformation?: string) {
    this.log.info(`PATCH -> ${ url }`);
    if (debugInformation) {
      this.log.extra(debugInformation);
    }
    return this.http.patch(url, data, { headers: this.headers })
      .map(this.getErrors)
      .catch(this.throwError);
  }
}

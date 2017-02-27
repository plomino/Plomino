import { LogService } from './log.service';
import { Http, Headers } from '@angular/http';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoHTTPAPIService {
  headers: Headers = new Headers();
        
  constructor(private http: Http, private log: LogService) {
    this.headers.append('Accept', 'application/json');
    this.headers.append('Content-Type', 'application/json');
  }

  get(url: string, debugInformation?: string) {
    this.log.info(`GET -> ${ url }`);
    if (debugInformation) {
      this.log.extra(debugInformation);
    }
    return this.http.get(url);
  }

  getWithOptions(url: string, options: any, debugInformation?: string) {
    this.log.info(`GET<H> -> ${ url }`);
    if (debugInformation) {
      this.log.extra(debugInformation);
    }
    return this.http.get(url, options);
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
    return this.http.post(url, data, { headers: this.headers });
  }

  postWithOptions(url: string, data: any, options: any, debugInformation?: string) {
    this.log.info(`POST<H> -> ${ url }`);
    if (debugInformation) {
      this.log.extra(debugInformation);
    }
    return this.http.post(url, data, options);
  }

  patch(url: string, data: any, debugInformation?: string) {
    this.log.info(`PATCH -> ${ url }`);
    if (debugInformation) {
      this.log.extra(debugInformation);
    }
    return this.http.patch(url, data, { headers: this.headers });
  }
}

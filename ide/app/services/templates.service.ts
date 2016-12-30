import { Injectable } from '@angular/core';

import { 
  Http, 
  Response 
} from '@angular/http';

import { Observable } from 'rxjs/Rx';

@Injectable()
export class TemplatesService {
  constructor(private http: Http) {}
  
  addTemplate(formUrl: string, templateId: string): Observable<any> {
    return this.http.get(`${formUrl}/add-template?id=${templateId}`).map(this.extractData);
  }

  getTemplates(formUrl: string): Observable<any> {
    return this.http.get(`${formUrl}/@@list-templates`).map(this.extractData);
  }

  private extractData(response: Response): Response {
    return response.json();
  }
}
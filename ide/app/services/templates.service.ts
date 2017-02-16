import { Injectable } from '@angular/core';

import { 
  Http, 
  Response 
} from '@angular/http';

import { Observable, Subject } from 'rxjs/Rx';

@Injectable()
export class TemplatesService {
  $insertion: Subject<any> = new Subject();

  constructor(private http: Http) {}
  
  addTemplate(formUrl: string, templateId: string): Observable<any> {
    return templateId ? 
      this.http.get(`${formUrl}/add-template?id=${templateId}`).map(this.extractData):
      Observable.of('');
  }

  getTemplate(formUrl: string, templateId: string): Observable<string> {
    return Observable.of(`
      <div id="drag-autopreview" class="plominoGroupClass mceNonEditable"
        contenteditable="false">
        <span class="mceEditable" contenteditable="false">
          <span class="plominoLabelClass mceNonEditable"
            contenteditable="false">
            Untitled
          </span><br>
        </span>
        <span class="plominoFieldClass mceNonEditable"
          data-present-method="convertFormFields_1"
          contenteditable="false"> <input type="text"> 
        </span>
      </div>
    `);
  }

  getTemplates(formUrl: string): Observable<any> {
    return this.http.get(`${formUrl}/@@list-templates`).map(this.extractData);
  }

  insertTemplate(templateData: any): void {
    this.$insertion.next(templateData);
  }

  getInsertion(): Observable<any> {
    return this.$insertion.asObservable();
  }

  private extractData(response: Response): Response {
    return response.json();
  }
}

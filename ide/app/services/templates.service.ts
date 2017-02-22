import { WidgetService } from './widget.service';
import { Injectable } from '@angular/core';

import { 
  Http, 
  Response 
} from '@angular/http';

import { Observable, Subject } from 'rxjs/Rx';

@Injectable()
export class TemplatesService {
  $insertion: Subject<any> = new Subject();
  templatesRegistry = {};

  constructor(private http: Http, private widgetService: WidgetService) {}
  
  addTemplate(formUrl: string, templateId: string): Observable<any> {
    return templateId ? 
      this.http.get(`${formUrl}/add-template?id=${templateId}`).map(this.extractData):
      Observable.of('');
  }

  buildTemplate(formUrl: string, template: PlominoFormGroupTemplate): void {
    if (!this.templatesRegistry.hasOwnProperty(formUrl)) {
      this.templatesRegistry[formUrl] = {};
    }

    this.widgetService
    .loadAndParseTemplatesLayout(formUrl, template)
    .subscribe((result: string) => {
      const $result = $(result).addClass('drag-autopreview');
      $result.find('input,textarea,button').removeAttr('name').removeAttr('id');
      $result.find('span').removeAttr('data-plominoid').removeAttr('data-mce-resize');
      $result.removeAttr('data-groupid');
      this.templatesRegistry[formUrl][template.id] = $result.get(0).outerHTML;
    });
  }

  getTemplate(formUrl: string, templateId: string): Observable<string> {
    return Observable.of(this.templatesRegistry[formUrl][templateId] 
      ? this.templatesRegistry[formUrl][templateId] 
      : `<div class="drag-autopreview plominoGroupClass mceNonEditable"
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

import { Injectable } from '@angular/core';
import { 
    Http, 
    Headers, 
    Response, 
    RequestOptions
} from '@angular/http';

import { Observable } from 'rxjs/Observable';

@Injectable()
export class ObjService {
    // For handling the injection/fetching/submission of Plomino objects

    constructor(private http:Http) {
        let headers = new Headers({ 'Content-Type': 'text/html' });
        let options = new RequestOptions({ headers: headers });
    }
    
    getFieldSettings(fieldUrl: string): Observable<any> {
        console.info('getFieldSettings called', fieldUrl);
        return this.http.get(`${fieldUrl}/@@edit?ajax_load=1&ajax_include_head=1`)
                    .map(this.extractText);
    }

    updateFieldSettings(fieldUrl: string, formData: FormData): Observable<any> {
        return this.http.post(`${fieldUrl}/@@edit`, formData)
                    .map(this.extractTextAndUrl);
    }
    
    getFormSettings(formUrl: string): Observable<any> {
        console.info('getFormSettings called', formUrl);
        return this.http.get(`${formUrl}/@@edit?ajax_load=1&ajax_include_head=1`)
                    .map(this.extractText);
    }

    
    updateFormSettings(formUrl: string, formData: any): Observable<any> {
      console.info('updateFormSettings', formUrl, (<any>formData).entries());
      let layout = formData.get('form.widgets.form_layout');
      if (layout) {
        layout = layout.replace(/\r/g , '').replace(/\xa0/g, ' ');
        let $layout = $(`<div>${ layout }</div>`);
  
        $layout.find('.plominoHidewhenClass,.plominoCacheClass').each(function () {
          let position = $(this).attr('data-plomino-position');
          let hwid = $(this).attr('data-plominoid');
          if (position && hwid) {
            $(this).text(`${position}:${hwid}`);
          }
  
          $(this).removeClass('mceNonEditable')
            .removeAttr('data-plominoid')
            .removeAttr('data-plomino-position');
  
          if (position === 'end' && $(this).next().get(0).tagName === 'BR') {
            $(this).next().remove();
          }
        });
  
        $layout.find('.plominoLabelClass').each(function () {
          let tag = this.tagName;
          let id = $(this).attr('data-plominoid');
          if (!id) {
            return true;
          }
  
          if (tag === 'SPAN') {
            $(this)
            .removeClass('mceNonEditable')
            .removeAttr('data-plominoid')
            .empty()
            .text(id);
          }
  
          if (tag === 'DIV') {
            let html = $(this).find('.plominoLabelContent').html();
            html = html.replace(/<p>/g, ' ');
            html = html.replace(/<\/p>/g, ' ');
            html = html.replace(/<p\/>/g, ' ');
            let span = `<span class="plominoLabelClass">${id}:${html}</span>`;
            $(this).replaceWith(span);
          }
        });
  
        $layout.find('*[data-plominoid]').each(function () {
          let id = $(this).attr('data-plominoid');
          let pClass = $(this).removeClass('mceNonEditable').attr('class');
          let span = `<span class="${pClass}">${id}</span>`;
          $(this).replaceWith(span);
        });

        formData.set('form.widgets.form_layout', $layout.html());
      }
      //<p><span class="plominoHidewhenClass mceNonEditable" data-plominoid="defaulthidewhen-1" data-plomino-position="start">&nbsp;</span><span class="plominoHidewhenClass mceNonEditable" data-plominoid="defaulthidewhen-1" data-plomino-position="end">&nbsp;</span>&nbsp;</p>
        return this.http.post(`${formUrl}/@@edit`, formData)
                    .map(this.extractTextAndUrl);
    }



    // Change this to use Promises/Observable pattern
    getDB(): Observable<any> {
        return this.http.get("../../@@edit?ajax_load=1&ajax_include_head=1")
            .map(this.extractText);
    }

    // Form should be a jquery form object
    submitDB(formData: FormData): Observable<any> {
        return this.http.post("../../@@edit", formData)
            .map(this.extractText);
    }

    private extractText(response: Response): any {
        return response.text();
    }

    private extractTextAndUrl(response: Response): any {
        return {
            html: response.text(),
            url: response.url.slice(0, response.url.indexOf('@') - 1)
        }
    }
}

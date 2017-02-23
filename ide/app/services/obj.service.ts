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
        return this.http.get(`${fieldUrl}/@@edit?ajax_load=1&ajax_include_head=1`)
                    .map(this.extractText);
    }

    updateFieldSettings(fieldUrl: string, formData: FormData): Observable<any> {
        return this.http.post(`${fieldUrl}/@@edit`, formData)
                    .map(this.extractTextAndUrl);
    }
    
    getFormSettings(formUrl: string): Observable<any> {
        return this.http.get(`${formUrl}/@@edit?ajax_load=1&ajax_include_head=1`)
                    .map(this.extractText);
    }

    /**
     * This code calling on the form saving.
     */
    updateFormSettings(formUrl: string, formData: any): Observable<any> {
      let layout = formData.get('form.widgets.form_layout');
      if (layout) {
        layout = layout.replace(/\r/g , '').replace(/\xa0/g, ' ');
        let $layout = $(`<div id="tmp-layout" style="display: none">${ layout }</div>`);
        $('body').append($layout);
        $layout = $("#tmp-layout");
  
        $layout.find('.plominoHidewhenClass,.plominoCacheClass')
        .each(function () {
          let $element = $(this);
          let position = $element.attr('data-plomino-position');
          let hwid = $element.attr('data-plominoid');
          if (position && hwid) {
            $element.text(`${position}:${hwid}`);
          }
  
          $element.removeClass('mceNonEditable')
            .removeAttr('data-plominoid')
            .removeAttr('data-present-method')
            .removeAttr('data-plomino-position');
  
          if (position === 'end' && $element.next().length 
            && $element.next().prop('tagName') === 'BR') {
            $element.next().remove();
          }
        });

        $layout.find('span.mceEditable').each((i, mceEditable) => {
          const $mceEditable = $(mceEditable);
          if ($mceEditable.children().last().prop('tagName') === 'BR') {
            $mceEditable.children().last().remove();
            $mceEditable.replaceWith(`<p>${$mceEditable.html()}</p>`);
          }
        });
  
        $layout.find('.plominoLabelClass').each(function () {
          let $element = $(this);
          let tag = $element.prop('tagName');
          let id = $element.attr('data-plominoid');

          if (!id) {
            const $relateFieldElement = $element.parent().next();

            if ($relateFieldElement.hasClass('plominoFieldClass') 
              && $relateFieldElement.attr('data-plominoid')) {
              id = $relateFieldElement.attr('data-plominoid');
            }
            else if ($relateFieldElement.prop('tagName') === 'P' 
              && $relateFieldElement.children().first().hasClass('plominoFieldClass') 
              && $relateFieldElement.children().first().attr('data-plominoid')) {
              id = $relateFieldElement.children().first().attr('data-plominoid');
            }
            else {
              console.info("???????", id, tag, $element);
              return true;
            }
          }
  
          if (tag === 'SPAN') {
            $element
            .removeClass('mceNonEditable')
            .removeAttr('data-plominoid')
            .empty()
            .text(id);
          }
  
          if (tag === 'DIV') {
            let html = $element.find('.plominoLabelContent').html();
            html = html.replace(/<p>/g, ' ');
            html = html.replace(/<\/p>/g, ' ');
            html = html.replace(/<p\/>/g, ' ');
            let span = `<span class="plominoLabelClass">${id}:${html}</span>`;
            $(this).replaceWith(span);
          }
        });
  
        $layout.find('*[data-plominoid]').each(function () {
          let $element = $(this);
          let id = $element.attr('data-plominoid');
          let pClass = $element.removeClass('mceNonEditable').attr('class');
          let span = `<span class="${pClass}">${id}</span>`;
          $(this).replaceWith(span);
        });

        formData.set('form.widgets.form_layout', $layout.html());
        $layout.remove();
      }
      
      // throw formData.get('form.widgets.form_layout');
      console.warn(formData.get('form.widgets.form_layout'));
      
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

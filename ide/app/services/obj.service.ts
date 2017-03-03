import { ElementService } from './element.service';
import { LabelsRegistryService } from './../editors/tiny-mce/services/labels-registry.service';
import { LogService } from './log.service';
import { Response } from '@angular/http';
import { PlominoHTTPAPIService } from './http-api.service';
import { Injectable, ChangeDetectorRef } from '@angular/core';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class ObjService {
    // For handling the injection/fetching/submission of Plomino objects

    constructor(private http: PlominoHTTPAPIService, private log: LogService,
    private elementService: ElementService,
    private changeDetector: ChangeDetectorRef,
    private labelsRegistry: LabelsRegistryService) {}

    getFieldSettings(fieldUrl: string): Observable<any> {
        return this.http.get(
          `${fieldUrl}/@@edit?ajax_load=1&ajax_include_head=1`,
          'obj.service.ts getFieldSettings'
        ).map(this.extractText);
    }

    updateFieldSettings(fieldUrl: string, formData: FormData): Observable<any> {
        return this.http.postWithOptions(
          `${fieldUrl}/@@edit`, formData, {},
          'obj.service.ts updateFieldSettings'
        ).map(this.extractTextAndUrl);
    }
    
    getFormSettings(formUrl: string): Observable<any> {
        return this.http.get(
          `${formUrl}/@@edit?ajax_load=1&ajax_include_head=1`,
          'obj.service.ts getFormSettings'
        ).map(this.extractText);
    }

    /**
     * this code calling on the form saving.
     * this code calling on the field-settings saving.
     */
    updateFormSettings(
      formUrl: string, formData: any
    ): Observable<{html: string, url: string}> {
      let layout = formData.get('form.widgets.form_layout');
      const context = this;
      if (layout) {
        /**
         * this code will be running only while form saving
         */
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
          const $element = $(this);
          const tag = $element.prop('tagName');
          let id = $element.attr('data-plominoid');
          const theLabelIsAdvanced = Boolean($element.attr('data-advanced'));

          if (id && !theLabelIsAdvanced) {
            /**
             * the label is not advanced - save its field title
             */
            
            /* current element (label) text */
            const title = $element.html();
            const relatedFieldTitle = context.labelsRegistry.get(`${formUrl}/${id}`, 'title');
            const relatedFieldTemporaryTitle = context.labelsRegistry.get(`${formUrl}/${id}`);

            if (relatedFieldTemporaryTitle !== relatedFieldTitle) {
              /**
               * save the field title
               */
              context.elementService.patchElement(
                `${formUrl}/${id}`, { title: relatedFieldTemporaryTitle }
              ).subscribe(() => {});
              
              $element.html(relatedFieldTemporaryTitle);
              context.changeDetector.detectChanges();
            }
          }
  
          if (tag === 'SPAN') {
            $element
            .removeClass('mceEditable')
            .removeClass('mceNonEditable')
            .removeAttr('data-plominoid');

            $element.html(
              theLabelIsAdvanced ? `${id}:${$element.html().trim()}` : id
            );
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
      else {
        /**
         * field settings saving
         */
        const workingId = formData.get('form.widgets.IShortName.id');
        const newTitle = formData.get('form.widgets.IBasic.title');
        
        this.labelsRegistry.update(`${ formUrl }/${ workingId }`, newTitle, 'title', true);
        this.labelsRegistry.update(`${ formUrl }/${ workingId }`, newTitle, 'temporary_title');

        const $allTheSame = $('iframe:visible').contents()
          .find(`.plominoLabelClass[data-plominoid="${ workingId }"]`)
          .filter((i, element) => !Boolean($(element).attr('data-advanced')));

        $allTheSame.html(newTitle);
      }
      
      // throw formData.get('form.widgets.form_layout');
      // console.warn(formData.get('form.widgets.form_layout'));
      
      return this.http.postWithOptions(
        `${formUrl}/@@edit`, formData, {},
        'obj.service.ts updateFormSettings'
      ).map(this.extractTextAndUrl);
    }



    // Change this to use Promises/Observable pattern
    getDB(): Observable<any> {
      return this.http.get(
        "../../@@edit?ajax_load=1&ajax_include_head=1",
        'obj.service.ts getDB'
      ).map(this.extractText);
    }

    // Form should be a jquery form object
    submitDB(formData: FormData): Observable<any> {
      return this.http.postWithOptions(
        "../../@@edit", formData, {},
        'obj.service.ts submitDB'
      ).map(this.extractText);
    }

    private extractText(response: Response) {
      return response.text();
    }

    private extractTextAndUrl(response: Response) {
      return {
        html: response.text(),
        url: response.url.slice(0, response.url.indexOf('@') - 1)
      }
    }
}

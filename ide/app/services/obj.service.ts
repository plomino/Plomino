import { FakeFormData } from './../utility/fd-helper/fd-helper';
import { Observable } from 'rxjs/Rx';
import { TabsService } from './tabs.service';
import { PlominoActiveEditorService } from './active-editor.service';
import { WidgetService } from './widget.service';
import { ElementService } from './element.service';
import { LabelsRegistryService } from './../editors/tiny-mce/services/labels-registry.service';
import { LogService } from './log.service';
import { Response } from '@angular/http';
import { PlominoHTTPAPIService } from './http-api.service';
import { Injectable, ChangeDetectorRef } from '@angular/core';

@Injectable()
export class ObjService {
    // For handling the injection/fetching/submission of Plomino objects

    constructor(private http: PlominoHTTPAPIService, private log: LogService,
      private elementService: ElementService,
      private widgetService: WidgetService,
      private tabsService: TabsService,
      private changeDetector: ChangeDetectorRef,
      private labelsRegistry: LabelsRegistryService,
      private activeEditorService: PlominoActiveEditorService,
    ) {}

    getFieldSettings(fieldUrl: string): Observable<any> {
      const addNew = fieldUrl.indexOf('++add++PlominoColumn') !== -1;
      
      return this.http.get(
        `${fieldUrl}/${ addNew ? '' : '@@edit' }?ajax_load=1&ajax_include_head=1`,
        'obj.service.ts getFieldSettings'
      ).map(this.extractText);
    }

    // updateFieldSettings(fieldUrl: string, formData: FormData): Observable<any> {
    //   const addNew = fieldUrl.indexOf('++add++PlominoColumn') !== -1;

    //   return this.http.postWithOptions(
    //     `${fieldUrl}/${ addNew ? '' : '@@edit' }`, formData, {},
    //     'obj.service.ts updateFieldSettings'
    //   ).map(this.extractTextAndUrl);
    // }
    
    getFormSettings(formUrl: string): Observable<any> {
      // if (this.http.recentlyChangedFormURL !== null
      //   && this.http.recentlyChangedFormURL[0] === formUrl
      //   && $('.tab-name').toArray().map((e) => e.innerText)
      //   .indexOf(formUrl.split('/').pop()) === -1
      // ) {
      //   formUrl = this.http.recentlyChangedFormURL[1];
      //   this.log.info('patched formUrl!', this.http.recentlyChangedFormURL);
      //   this.log.extra('obj.service.ts getFormSettings');
      // }
      return this.http.get(
        `${formUrl}/@@edit?ajax_load=1&ajax_include_head=1`,
        'obj.service.ts getFormSettings'
      ).map(this.extractText);
    }

  /**
   * this code calling on the form saving.
   * this code calling on the field-settings saving.
   */
  updateFieldSettings(
    formUrl: string, formData: FakeFormData
  ): Observable<{html: string, url: string}> {
    const addNew = formUrl.indexOf('++add++PlominoColumn') !== -1;
    // let layout = formData.get('form.widgets.form_layout');
    const workingId = formData.get('form.widgets.IShortName.id');
    const context = this;

    // this.http.recentlyChangedFormURL = null;

    // const oldFormId = formUrl.split('/').pop();
    // let newFormUrl = oldFormId !== workingId
    //   ? formUrl.replace(oldFormId, workingId)
    //   : formUrl;

    return Observable.of(true).flatMap(() => {
      // if (layout) {
      //   if (oldFormId !== workingId) {
      //     this.http.recentlyChangedFormURL = [formUrl, newFormUrl];
      //   }
      //   /**
      //    * this code will be running only while form saving
      //    */
      //   layout = layout.replace(/\r/g , '').replace(/\xa0/g, ' ');
      //   let $layout = $(`<div id="tmp-layout" style="display: none">${ layout }</div>`);
      //   $('body').append($layout);
      //   $layout = $("#tmp-layout");
  
      //   $layout.find('.plominoHidewhenClass,.plominoCacheClass')
      //   .each(function () {
      //     let $element = $(this);
      //     let position = $element.attr('data-plomino-position');
      //     let hwid = $element.attr('data-plominoid');
      //     if (position && hwid) {
      //       $element.text(`${position}:${hwid}`);
      //     }
  
      //     $element.removeAttr('data-plominoid')
      //       .removeAttr('data-present-method')
      //       .removeAttr('data-plomino-position');
  
      //     if (position === 'end' && $element.next().length 
      //       && $element.next().prop('tagName') === 'BR') {
      //       $element.next().remove();
      //     }
      //   });

      //   $layout.find('span.mceEditable').each((i, mceEditable) => {
      //     const $mceEditable = $(mceEditable);
      //     if ($mceEditable.children().last().prop('tagName') === 'BR') {
      //       $mceEditable.children().last().remove();
      //       $mceEditable.replaceWith(`<p>${$mceEditable.html()}</p>`);
      //     }
      //   });

      //   const labels$: Observable<any>[] = [];
  
      //   $layout.find('.plominoLabelClass').each(function () {
      //     const $element = $(this);
      //     const tag = $element.prop('tagName');
      //     let id = $element.attr('data-plominoid');
      //     const theLabelIsAdvanced = Boolean($element.attr('data-advanced'));

      //     if (id && !theLabelIsAdvanced) {
      //       /**
      //        * the label is not advanced - save its field title
      //        */
            
      //       /* current element (label) text */
      //       const title = $element.html();
      //       const relatedFieldTitle = context.labelsRegistry.get(`${formUrl}/${id}`, 'title');
      //       const relatedFieldTemporaryTitle = context.labelsRegistry.get(`${formUrl}/${id}`);

      //       if (relatedFieldTemporaryTitle !== relatedFieldTitle) {
      //         /**
      //          * save the field title
      //          */
      //         labels$.push(
      //           context.elementService.patchElement(
      //             `${formUrl}/${id}`, { title: relatedFieldTemporaryTitle }
      //           )
      //         );
              
      //         $element.html(relatedFieldTemporaryTitle);
      //         context.changeDetector.detectChanges();
      //       }
      //     }
  
      //     if (tag === 'SPAN') {
      //       $element
      //       .removeAttr('data-plominoid');

      //       $element.html(
      //         theLabelIsAdvanced ? `${id}:${$element.html().trim()}` : id
      //       );
      //     }
  
      //     if (tag === 'DIV') {
      //       let html = $element.find('.plominoLabelContent').html();
      //       html = html.replace(/<p>/g, ' ');
      //       html = html.replace(/<\/p>/g, ' ');
      //       html = html.replace(/<p\/>/g, ' ');
      //       let span = `<span class="plominoLabelClass">${id}:${html}</span>`;
      //       $(this).replaceWith(span);
      //     }
      //   });

      //   const labels$$ = (labels$.length) 
      //     ? Observable.forkJoin(labels$) : Observable.of('');
  
      //   $layout.find('*[data-plominoid]').each(function () {
      //     let $element = $(this);
      //     let id = $element.attr('data-plominoid');
      //     let pClass = $element.removeClass('mceNonEditable').attr('class');
      //     let span = `<span class="${pClass}">${id}</span>`;
      //     $(this).replaceWith(span);
      //   });

      //   const $errLabels = $layout.find(
      //     '.plominoLabelClass:contains(":") > .plominoLabelClass'
      //   );
  
      //   $errLabels.each((i, errLabel) => {
      //     const $errLabel = $(errLabel);
      //     const id = $errLabel.html();
      //     $errLabel.parent().html(id);
      //   });

      //   $layout.find(
      //     '.mceNonEditable,.mceEditable,.plominoFieldClass--selected,' +
      //     '.plominoLabelClass--selected'
      //   )
      //   .removeClass('mceNonEditable')
      //   .removeClass('mceEditable')
      //   .removeClass('plominoFieldClass--selected')
      //   .removeClass('plominoLabelClass--selected');

      //   formData.set('form.widgets.form_layout', $layout.html());
      //   $layout.remove();

      //   return labels$$;
      // }
      // else {
        /**
         * field settings saving
         */
        if (this.activeEditorService.getActive()) {
          const newTitle = formData.get('form.widgets.IBasic.title');
          
          this.labelsRegistry.update(
            `${ formUrl }/${ workingId }`, newTitle, 'title', true
          );
          
          this.labelsRegistry.update(
            `${ formUrl }/${ workingId }`, newTitle, 'temporary_title'
          );
  
          const $allTheSame = $(this.activeEditorService.getActive().getBody())
            .find(`.plominoLabelClass[data-plominoid="${ workingId }"]`)
            .filter((i, element) => !Boolean($(element).attr('data-advanced')));
  
          $allTheSame.html(newTitle);
        }

        return Observable.of('');
      // }
      
      // throw formData.get('form.widgets.form_layout');
      // console.warn(formData.get('form.widgets.form_layout'));
    })
    .flatMap(() => {
      
      return this.http.postWithOptions(
        `${formUrl}/${ addNew ? '' : '@@edit' }`, formData.build(), {},
        'obj.service.ts updateFieldSettings'
      )
      .map((data: Response) => {
        return this.extractTextAndUrl(data);
      });
    });
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

    extractText(response: Response) {
      if (response.text().indexOf(
        'You do not have sufficient privileges to view this page'
      ) !== -1) {
        return `<div class="outer-wrapper">
          <p style="text-align: center; padding-top: 20px;">
            You do not have sufficient privileges to view this page
          </p>
        </div><!--/outer-wrapper -->`;
      };

      return response.text();
    }

    extractTextAndUrl(response: Response): {html: string, url: string} {
      const result = {
        html: response.text(),
        url: response.url.indexOf('@') !== -1 
          ? response.url.slice(0, response.url.indexOf('@') - 1)
          : response.url
      };
      return result;
    }
}

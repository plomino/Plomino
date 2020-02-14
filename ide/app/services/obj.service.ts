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

  private formSettingsCache: Map<string, string> = new Map();

  /**
   * @description formSettingsCurrent[formId: string, htmlFormContent: string]
   */
  private formSettingsCurrent: [
    string, string
  ] = null;

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
      )
      .map(this.extractText)
      .catch((error) => {
        return 'E';
      });
    }
    
    getFormSettings(formUrl: string, flushCache = false): Observable<any> {
      const formId = formUrl.split('/').pop();
      if (this.formSettingsCache.has(formId) && !flushCache) {
        const data = this.formSettingsCache.get(formId).toString();
        const result = Observable.of(data);
        this.formSettingsCurrent = [formId, data];
        this.formSettingsCache.delete(formId);
        return result;
      }
      return this.http.get(
        `${formUrl}/@@edit?ajax_load=1&ajax_include_head=1`,
        'obj.service.ts getFormSettings'
      )
      .map(this.extractText)
      .map((data) => {
        this.formSettingsCurrent = [formId, data];
        return data;
      })
    }

    updateFormSettingsCache() {
      if (!this.formSettingsCurrent) {
        return;
      }
      this.formSettingsCache.set(
        this.formSettingsCurrent[0], this.formSettingsCurrent[1]);
    }

    flushFormSettingsCache(formId: string) {
      if (this.formSettingsCache.has(formId)) {
        this.formSettingsCache.delete(formId);
      }
    }

  /**
   * this code calling on the form saving.
   * this code calling on the field-settings saving.
   */
  updateFieldSettings(
    formUrl: string, formData: FakeFormData
  ): Observable<{html: string; url: string}> {
    const addNew = formUrl.indexOf('++add++PlominoColumn') !== -1;
    const workingId = formData.get('form.widgets.IShortName.id');
    const context = this;

    return Observable.of(true).flatMap(() => {
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
          .filter((i, element) => !$(element).attr('data-advanced'));

        $allTheSame.html(newTitle);
      }

      return Observable.of('');
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
      }

      return response.text();
    }

    extractTextAndUrl(response: Response): {html: string; url: string} {
      const result = {
        html: response.text(),
        url: response.url.indexOf('@') !== -1 
          ? response.url.slice(0, response.url.indexOf('@') - 1)
          : response.url
      };
      return result;
    }
}

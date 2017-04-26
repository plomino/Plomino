import { PlominoViewSaveProcess } from './view-save-process';
import { FakeFormData } from './../../utility/fd-helper/fd-helper';
import { Observable, Subject } from 'rxjs/Rx';
import { PlominoFormSaveProcess } from './form-save-process';
import { TinyMCEFormContentManagerService } from './../../editors/tiny-mce/content-manager/content-manager.service';
import { Injectable } from '@angular/core';
import { PlominoHTTPAPIService, ElementService, 
  WidgetService, PlominoActiveEditorService } from '../';
import { LabelsRegistryService } from '../../editors/tiny-mce/services';

@Injectable()
export class PlominoSaveManagerService {

  private savedStates: Map<string, string> = new Map<string, string>();
  private saveStack: Array<Observable<any>> = [];
  private saveNotifier: Subject<string> = new Subject<string>();

  constructor(
    private contentManager: TinyMCEFormContentManagerService,
    private http: PlominoHTTPAPIService,
    private elementService: ElementService,
    private widgetService: WidgetService,
    private labelsRegistry: LabelsRegistryService,
    private activeEditorService: PlominoActiveEditorService,
  ) {
    Observable
      .interval(500)
      .flatMap(() => this.saveStack.length 
        ? this.saveStack.pop() : Observable.of(null))
      .subscribe((data) => {
        if (data) {
          this.saveNotifier.next(data.url);
        }
      });
  }

  onBackgroundSaveProcessComplete() {
    return this.saveNotifier.asObservable();
  }

  nextEditorSavedState(editorId: string, state: string = null): void {
    this.savedStates.set(editorId, state || this.contentManager.getContent(editorId));
  }

  isEditorUnsaved(editorId: string): boolean {
    if (this.savedStates.has(editorId)) {
      return this.savedStates.get(editorId)
        !== this.contentManager.getContent(editorId);
    }
    else {
      return true;
    }
  }

  createViewSaveProcess(viewURL: string, formData: FakeFormData = null) {
    viewURL = viewURL.replace(/^(.+?)\/?$/, '$1');

    if (formData === null) {
      const $form = $('form[action="' + viewURL + '/@@edit"]');
      
      if (!$form.length) {
        debugger;
        return null;
      }

      formData = new FakeFormData(<HTMLFormElement> $form.get(0));
      formData.set('form.buttons.save', 'Save');
    }

    const process = new PlominoViewSaveProcess({
      immediately: false,
      formURL: viewURL,
      formData: formData,
      labelsRegistryLink: this.labelsRegistry,
      httpServiceLink: this.http,
      activeEditorServiceLink: this.activeEditorService,
      widgetServiceLink: this.widgetService
    });

    return process;
  }

  createFormSaveProcess(formURL: string, formData: FakeFormData = null) {
    formURL = formURL.replace(/^(.+?)\/?$/, '$1');

    if (formData === null) {
      const $form = $('form[action="' + formURL + '/@@edit"]');
      
      if (!$form.length) {
        return null;
      }

      formData = new FakeFormData(<HTMLFormElement> $form.get(0));
      formData.set('form.buttons.save', 'Save');
      formData.set('form.widgets.form_layout', this.contentManager.getContent(formURL));
    }

    const process = new PlominoFormSaveProcess({
      immediately: false,
      formURL: formURL,
      formData: formData,
      labelsRegistryLink: this.labelsRegistry,
      httpServiceLink: this.http,
      activeEditorServiceLink: this.activeEditorService,
      widgetServiceLink: this.widgetService
    });

    return process;
  }

  enqueueNewFormSaveProcess(formURL: string) {
    const process = this.createFormSaveProcess(formURL);
    this.saveStack.unshift(process.start());
  }
}

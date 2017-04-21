import { PlominoFormSaveProcess } from './save-process';
import { TinyMCEFormContentManagerService } from './../../editors/tiny-mce/content-manager/content-manager.service';
import { Injectable } from '@angular/core';
import { PlominoHTTPAPIService, ElementService, 
  WidgetService, PlominoActiveEditorService } from '../';
import { LabelsRegistryService } from '../../editors/tiny-mce/services';

@Injectable()
export class PlominoSaveManagerService {

  private savedStates: Map<string, string> = new Map<string, string>();

  constructor(
    private contentManager: TinyMCEFormContentManagerService,
    private http: PlominoHTTPAPIService,
    private elementService: ElementService,
    private widgetService: WidgetService,
    private labelsRegistry: LabelsRegistryService,
    private activeEditorService: PlominoActiveEditorService,
  ) { }

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

  createFormSaveProcess(formURL: string, formData: FormData = null) {
    if (formData === null) {
      const $form = $('form[action="' + formURL + '/@@edit"]');
      
      if (!$form.length) {
        return null;
      }

      formData = new FormData(<HTMLFormElement> $form.get(0));
      formData.append('form.buttons.save', 'Save');
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

  enqueueNewFormSaveProcess(immediately = false) {
    // const process = new PlominoFormSaveProcess({
    //   immediately
    // });
  }
}

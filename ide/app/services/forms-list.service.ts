import { PlominoActiveEditorService } from './active-editor.service';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoFormsListService {
  forms: any[];
  views: any[];

  constructor(private activeEditorService: PlominoActiveEditorService) { }

  setForms(forms: any[]) {
    this.forms = forms.filter((form) => form.type === 'PlominoForm');
    this.views = forms.filter((form) => form.type === 'PlominoView');
  }

  getForms() {
    return this.forms;
  }

  getViews() {
    return this.views;
  }

  getFiltered() {
    const active = this.activeEditorService.getActive();
    return this.getForms().filter((form) => {
      const formId = (<string>form.url).split("/").pop()
      return !active || active.id !== formId;
    });
  }
}

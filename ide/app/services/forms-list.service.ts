import { PlominoActiveEditorService } from './active-editor.service';
import { Injectable } from '@angular/core';

@Injectable()
export class PlominoFormsListService {
  forms: any[];

  constructor(private activeEditorService: PlominoActiveEditorService) { }

  setForms(forms: any[]) {
    this.forms = forms.filter((form) => form.type === 'PlominoForm');
  }

  getForms() {
    return this.forms;
  }

  getFiltered() {
    const active = this.activeEditorService.getActive();
    return this.getForms().filter((form) => {
      return !active || active.id !== form.url;
    });
  }
}

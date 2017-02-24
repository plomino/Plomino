import { Injectable } from '@angular/core';

@Injectable()
export class PlominoFormsListService {
  forms: any[];

  constructor() { }

  setForms(forms: any[]) {
    this.forms = forms.filter((form) => form.type === 'PlominoForm');
  }

  getForms() {
    return this.forms;
  }
}

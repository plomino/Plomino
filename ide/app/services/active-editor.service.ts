import { Injectable } from '@angular/core';

@Injectable()
export class PlominoActiveEditorService {

  editorURL: string = null;

  constructor() { }

  setActive(editorURL: string) {
    if (editorURL !== null) {
      this.editorURL = editorURL;
    }
  }

  getActive(): TinyMceEditor {
    return tinymce.get(this.editorURL);
  }
}

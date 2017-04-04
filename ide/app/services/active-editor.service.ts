import { Injectable } from '@angular/core';

@Injectable()
export class PlominoActiveEditorService {

  editorURL: string = null;

  constructor() { }

  setActive(editorURL: string, fixEditors = false) {
    /* hide all another editors */
    this.editorURL = editorURL;

    if (fixEditors) {
      $('plomino-tiny-mce').css({
        position: 'fixed',
        top: 0, left: 0,
        'pointer-events': 'none',
        'z-index': -111111 
      });

      if (editorURL !== null) {
        $(`plomino-tiny-mce:has(textarea[id="${ editorURL }"])`)
          .removeAttr('style');
      }
    }
  }

  getActive(): TinyMceEditor {
    return tinymce.get(this.editorURL);
  }
}

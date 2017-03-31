import { Injectable } from '@angular/core';

@Injectable()
export class PlominoActiveEditorService {

  editorURL: string = null;

  constructor() { }

  setActive(editorURL: string) {
    /* hide all another editors */
    $('plomino-tiny-mce').css({
      position: 'fixed',
      top: 0, left: 0,
      'z-index': -111111 
    });
    if (editorURL !== null) {
      this.editorURL = editorURL;
      $(`plomino-tiny-mce:has(textarea[id="${ editorURL }"])`)
        .removeAttr('style');
    }
  }

  getActive(): TinyMceEditor {
    return tinymce.get(this.editorURL);
  }
}

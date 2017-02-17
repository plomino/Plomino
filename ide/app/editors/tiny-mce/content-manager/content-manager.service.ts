import { Injectable } from '@angular/core';

@Injectable()
export class TinyMCEFormContentManagerService {

  logLevel = 2;

  constructor() { }

  log(func = 'null', msg = 'empty', requiredLevel = 1) {
    if (this.logLevel >= requiredLevel) {
      console.info(func, msg);
    }
  }

  setContent(editorId: any, contentHTML: string, dragging?: any): void {
    const editor = tinymce.get(editorId);

    if (!/<br\040?\/?>(\s+)?$/ig.test(contentHTML)) {
      contentHTML = contentHTML + '<br>';
    }

    editor.setContent(contentHTML);
    this.log('setContent contentHTML', contentHTML, 3);

    const that = this;

    $('iframe:visible').contents()
    .find('.plominoGroupClass').off('.cme')
    .on('mousemove.cme', function () {
      if (dragging.currentDraggingData) {
        that.selectAndRemoveElementById(editorId, 'drag-autopreview');
        dragging.target = $(this);
        $(dragging.currentDraggingTemplateCode)
        .insertAfter(dragging.target);
      }
    })
    .on('mouseleave.cme', function () {
      that.selectAndRemoveElementById(editorId, 'drag-autopreview');
      dragging.target = null;
    });

    $('iframe:visible').contents().off('.cmb')
    .on('mousemove.cmb', function () {
      if (!dragging.target) {
        // console.log('body-move', 
        //   $('iframe:visible').contents().find('*:not(.mce-visual-caret):last').get(0),
        //   dragging.currentDraggingTemplateCode);
      }
      
      // if (dragging.target === null) {
      //   $('iframe:visible').contents().find('*:last');
      //   $(dragging.currentDraggingTemplateCode)
      //   .insertAfter(dragging.target);
      // }
    })
    .on('mouseleave.cmb', function () {
      // that.selectAndRemoveElementById(editorId, 'drag-autopreview');
      // dragging.target = null;
    });
  }

  getContent(editorId: any): string {
    const editor = tinymce.get(editorId);
    const content = editor.getContent();

    return (/<br\040?\/?>(\s+)?$/ig.test(content)) 
      ? content.replace(/<br\040?\/?>(\s+)?$/ig, '') 
      : content;
  }

  selectAndRemoveElementById(editorId: any, elementId: string): void {
    const editor = tinymce.get(editorId);
    editor.focus(); //give the editor focus
    editor.selection.select(editor.dom.select(`#${ elementId }`)[0]);
    editor.selection.collapse(0);
    editor.dom.remove(elementId);

    this.log('selectAndRemoveElementById elementId', elementId, 2);
  }

  insertRawHTML(editorId: any, contentHTML: string): void {
    const editor = tinymce.get(editorId);
    editor.execCommand('mceInsertRawHTML', false, contentHTML);
    this.log('insertRawHTML contentHTML', contentHTML);
  }

  insertContent(editorId: any, contentHTML: string, options?: any): void {
    const editor = tinymce.get(editorId);

    let target: any = null;
    if (options.target) {
      target = options.target;
    }
    
    if (options) {
      editor.execCommand('mceInsertContent', false, contentHTML, options);
    }
    else {
      if (target) {
        let $content = $(contentHTML);
        $content.insertAfter($(target));
        $('iframe:visible').contents().click();

        this.setContent(editorId, this.getContent(editorId));
      }
      else {
        editor.execCommand('mceInsertContent', false, contentHTML);
      }
    }

    this.log('insertContent contentHTML', contentHTML);
  }

  selectDOM(editorId: any, selector: string): any {
    const editor = tinymce.get(editorId);
    try {
      return editor.dom.select(selector);
    } catch (e) {
      this.log('selectDOM DOM cannot be selected selector', selector);
      return [];
    }
  }

  selectContent(editorId: any, contentHTML: string): any {
    const editor = tinymce.get(editorId);
    try {
      return editor.selection.select(contentHTML);
    } catch (e) {
      this.log('selectContent content cannot be selected contentHTML', contentHTML);
      return false;
    }
  }

  replaceContent(editorId: any, contentHTML: string): void {
    const editor = tinymce.get(editorId);
    try {
      editor.execCommand('mceReplaceContent', false, contentHTML);
      this.log('replaceContent contentHTML', contentHTML);
    } catch (e) {
      this.log('replaceContent content cannot be replaced contentHTML', contentHTML);
    }
  }

  getCaretRangeFromMouseEvent(editorId: any, eventData: MouseEvent) {
    const editor = tinymce.get(editorId);

    const x = eventData.clientX;
    const y = eventData.clientY;

    const caretRange = tinymce.dom.RangeUtils
      .getCaretRangeFromPoint(x, y, editor.getDoc());

    this.log('getCaretRangeFromMouseEvent', caretRange, 4);
    return caretRange;
  }

  setRange(editorId: any, range: any) {
    const editor = tinymce.get(editorId);
    editor.selection.setRng(range);
  }
}

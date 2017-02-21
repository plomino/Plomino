import { Observable, Subject } from 'rxjs/Rx';
import { TabsService } from './../../../services/tabs.service';
import { DraggingService } from './../../../services/dragging.service';
import { Injectable, ChangeDetectorRef } from '@angular/core';

@Injectable()
export class TinyMCEFormContentManagerService {
  private logLevel = 0;

  private iframeMouseMoveEvents: Subject<PlominoIFrameMouseMove> 
    = new Subject<PlominoIFrameMouseMove>();
  private iframeMouseMoveEvents$: Observable<PlominoIFrameMouseMove> 
    = this.iframeMouseMoveEvents.asObservable();
  
  private iframeMouseLeaveEvents: Subject<PlominoIFrameMouseLeave> 
    = new Subject<PlominoIFrameMouseLeave>();
  private iframeMouseLeaveEvents$: Observable<PlominoIFrameMouseLeave> 
    = this.iframeMouseLeaveEvents.asObservable();

  constructor(private changeDetector: ChangeDetectorRef, 
  private tabsService: TabsService) {
    interface OneInTimeObservable<PlominoIFrameMouseMove> 
      extends Observable<PlominoIFrameMouseMove> {
      oneInTime: (delay: any) => Observable<PlominoIFrameMouseMove>;
    };

    (<any>Observable).prototype.oneInTime = function (delay: any) {
     return this.take(1).merge(Observable.empty().delay(delay)).repeat();
    };

    /**
     * listening on the MouseMove event on the tinymce editable body.
     * note: this event callback different with the .PlominoGroup MouseMove
     */
    (
      <OneInTimeObservable<PlominoIFrameMouseMove>>
      this.iframeMouseMoveEvents$
    )
    .oneInTime(500)
    .subscribe((event) => {
      const dragging = event.draggingService;
      const editorId = event.editorId;
      const originalEvent = event.originalEvent;

      if (dragging.currentDraggingData && dragging.target === null) {
        const range = 
          this.getCaretRangeFromMouseEvent(editorId, originalEvent);
        if (this.rangeAccepted(range)) {
          $('iframe:visible').contents().find('#drag-autopreview').remove();
          range.insertNode($(dragging.currentDraggingTemplateCode).get(0));
          dragging.targetRange = range;
          return;
        }
        const $latestTarget = $('iframe:visible').contents()
          .find('*:not(.mce-visual-caret):last');
        $('iframe:visible').contents().find('#drag-autopreview').remove();
        $(dragging.currentDraggingTemplateCode)
        .insertBefore($latestTarget);
      }
    });

    /**
     * listening on the MouseLeave event on the tinymce editable body.
     * note: this event callback different with the .PlominoGroup MouseLeave
     */
    this.iframeMouseLeaveEvents$
    .subscribe((event) => {
      const dragging = event.draggingService;

      if (dragging.currentDraggingData) {
        $('iframe:visible').contents().find('#drag-autopreview').remove();
      }
    });
  }

  log(func = 'null', msg = 'empty', requiredLevel = 1) {
    if (this.logLevel >= requiredLevel) {
      console.info(func, msg);
    }
  }

  setContent(editorId: any, contentHTML: string, dragging?: any): void {
    let editor = tinymce.get(editorId);
    
    if (!editor) {
      editorId = $('iframe:visible').attr('id').replace('_ifr', '');
      editor = tinymce.EditorManager.editors[editorId];
    }

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
        $('iframe:visible').contents().find('#drag-autopreview').remove();
        dragging.target = $(this);
        $(dragging.currentDraggingTemplateCode)
        .insertAfter(dragging.target);
      }
    })
    .on('mouseleave.cme', function () {
      if (dragging.currentDraggingData) {
        $('iframe:visible').contents().find('#drag-autopreview').remove();
      }
      
      dragging.target = null;
      dragging.targetRange = null;
    });

    $('iframe:visible').contents().off('.cmb')
    .on('mousemove.cmb', function (evt) {
      that.iframeMouseMoveEvents.next({
        originalEvent: <MouseEvent>evt.originalEvent,
        draggingService: dragging,
        editorId
      });
    })
    .on('mouseleave.cmb', function () {
      that.iframeMouseLeaveEvents.next({
        draggingService: dragging
      });
    });
  }

  getContent(editorId: any): string {
    let editor = tinymce.get(editorId);

    if (!editor) {
      editorId = $('iframe:visible').attr('id').replace('_ifr', '');
      editor = tinymce.EditorManager.editors[editorId];
    }
    const content = editor.getContent();

    return (/<br\040?\/?>(\s+)?$/ig.test(content)) 
      ? content.replace(/<br\040?\/?>(\s+)?$/ig, '') 
      : content;
  }

  selectAndRemoveElementById(editorId: any, elementId: string): void {
    const editor = tinymce.get(editorId);
    if (editor) {
      editor.focus(); //give the editor focus
      editor.selection.select(editor.dom.select(`#${ elementId }`)[0]);
      editor.selection.collapse(0);
      editor.dom.remove(elementId);
  
      this.log('selectAndRemoveElementById elementId', elementId, 2);
    }
  }

  insertRawHTML(editorId: any, contentHTML: string): void {
    const editor = tinymce.get(editorId);
    editor.execCommand('mceInsertRawHTML', false, contentHTML);
    this.log('insertRawHTML contentHTML', contentHTML);
  }

  rangeAccepted(range: Range): boolean {
    return range && $(range.startContainer).prop('tagName') === 'P';
  }

  insertContent(editorId: any, dragging: DraggingService, contentHTML: string, options?: any): void {
    let editor = tinymce.get(editorId);

    if (!editor) {
      editorId = $('iframe:visible').attr('id').replace('_ifr', '');
      editor = tinymce.EditorManager.editors[editorId];
    }

    let target: any = null;
    
    if (options.target) {
      target = options.target;
    }

    if (contentHTML === '<div class="plominoGroupClass mceNonEditable"></div>') {
      return;
    }
    
    if (options && !options.target) {
      // delete options['target'];
      const a = editor.getContent().length;
      
      editor.execCommand('mceInsertContent', false, contentHTML, options);
      
      setTimeout(() => {
        if (a === editor.getContent().length) {
          editor.execCommand('mceInsertContent', false, contentHTML, options);
        }
      }, 100);
    }
    else {
      if (target) {
        const $content = $(contentHTML);
        const $latestTarget = $('iframe:visible').contents()
          .find('*:not(.mce-visual-caret):last');
        const lastInsert = $latestTarget.get(0) === target;
        const range = dragging.targetRange;
        console.info(
          'target && !options, dragging.targetRange', dragging.targetRange,
          'lastInsert', lastInsert);
        if (this.rangeAccepted(range)) {
          range.insertNode($content.get(0));
        }
        else {
          $content[lastInsert ? 'insertBefore': 'insertAfter']($(target));
        }
        
        $('iframe:visible').contents().click();
      }
      else {
        console.info(
          '!target && !options, dragging.targetRange', dragging.targetRange);
        editor.execCommand('mceInsertContent', false, contentHTML);
      }
    }

    dragging.targetRange = null;
    this.changeDetector.markForCheck();
    // this.tabsService.setActiveTabDirty();
    this.setContent(editorId, this.getContent(editorId), dragging);
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

  getCaretRangeFromMouseEvent(editorId: any, eventData: MouseEvent): Range {
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

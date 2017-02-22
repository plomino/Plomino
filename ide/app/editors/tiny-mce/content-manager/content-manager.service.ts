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

  private iframeGroupMouseMoveEvents: Subject<PlominoIFrameMouseMove> 
    = new Subject<PlominoIFrameMouseMove>();
  private iframeGroupMouseMoveEvents$: Observable<PlominoIFrameMouseMove> 
    = this.iframeGroupMouseMoveEvents.asObservable();
  
  private iframeGroupMouseLeaveEvents: Subject<PlominoIFrameMouseLeave> 
    = new Subject<PlominoIFrameMouseLeave>();
  private iframeGroupMouseLeaveEvents$: Observable<PlominoIFrameMouseLeave> 
    = this.iframeGroupMouseLeaveEvents.asObservable();

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
    .oneInTime(300)
    .subscribe((event) => {
      const dragging = event.draggingService;
      const editorId = event.editorId;
      const originalEvent = event.originalEvent;

      if (dragging.currentDraggingData && dragging.target === null) {
        const range = 
          this.getCaretRangeFromMouseEvent(editorId, originalEvent);
          
        console.info('range', range.startContainer, range.startOffset,
          range.commonAncestorContainer);

        const currentDragCode = dragging.currentDraggingTemplateCode;
        const $currentDragNode = $(currentDragCode);

        if (!$currentDragNode.hasClass('drag-autopreview')) {
          $currentDragNode.addClass('drag-autopreview');
        }

        if (this.rangeAccepted(range)) {
          $('iframe:visible').contents().find('.drag-autopreview').remove();
          range.insertNode($currentDragNode.get(0));
          dragging.targetRange = range;
          return;
        }
        const $latestTarget = $('iframe:visible').contents()
          .find('*:not(.mce-visual-caret):last');
        $('iframe:visible').contents().find('.drag-autopreview').remove();
        $currentDragNode.insertBefore($latestTarget);
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
        $('iframe:visible').contents().find('.drag-autopreview').remove();
      }
    });

    /**
     * listening on the MouseMove event on the tinymce editable GROUP.
     * note: this event callback different with outside of .PlominoGroup MouseMove
     */
    (
      <OneInTimeObservable<PlominoIFrameMouseMove>>
      this.iframeGroupMouseMoveEvents$
    )
    // .oneInTime(200)
    .subscribe((event) => {
      const originalEvent = event.originalEvent;
      const dragging = event.draggingService;
      const $group = event.$group;
      /**
       * check where are we now - bottom or the top of the group
       * 1. get height
       * 2. get y inside the group
       * 3. if y >= 40% of height then bottom else top
       */
      const groupHeight = $group.height();
      const yPositionInsideGroup = originalEvent.clientY - $group.offset().top;
      const hoverAtBottom = yPositionInsideGroup >= groupHeight * 0.4;
      // dragging.targetSideBottom = hoverAtBottom;
      dragging.targetSideBottom = true;
      
      dragging.target = $group;
      $('iframe:visible').contents().find('.drag-autopreview').remove();

      let $preview = $(dragging.currentDraggingTemplateCode);
      if (!hoverAtBottom) {
        $preview.css({
          top: `-${ groupHeight * 2 + 25 }px`,
          position: 'relative'
        });
      }
      
      if (/hidewhenclass/ig.test($preview.get(0).outerHTML)) {
        const $templateA = $(`
          <span class="drag-autopreview plominoHidewhenClass mceNonEditable"
            data-plomino-position="start"
            contenteditable="false">&nbsp;</span>
        `);
        const $templateB = $(`
          <span class="drag-autopreview plominoHidewhenClass mceNonEditable"
            data-plomino-position="end"
            contenteditable="false">&nbsp;</span>
        `);

        $templateA.insertBefore(dragging.target);
        $templateB.insertAfter(dragging.target);
      }
      else {
        if (!$preview.hasClass('drag-autopreview')) {
          $preview.addClass('drag-autopreview');
        }
        $preview.insertAfter(dragging.target);
      }
    });

    /**
     * listening on the MouseLeave event on the tinymce editable GROUP.
     * note: this event callback different with outside of .PlominoGroup MouseLeave
     */
    (
      <OneInTimeObservable<PlominoIFrameMouseMove>>
      this.iframeGroupMouseLeaveEvents$
    )
    // .oneInTime(500)
    .subscribe((event) => {
      const dragging = event.draggingService;
      if (dragging.currentDraggingData) {
        $('iframe:visible').contents().find('.drag-autopreview').remove();
      }
      
      dragging.target = null;
      dragging.targetRange = null;
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
    .on('mousemove.cme', function (evt) {
      if (dragging.currentDraggingData) {
        that.iframeGroupMouseMoveEvents.next({
          draggingService: dragging,
          originalEvent: <MouseEvent>evt.originalEvent,
          $group: $(this),
          editorId
        });
      }
    })
    .on('mouseleave.cme', function () {
      that.iframeGroupMouseLeaveEvents.next(
        { draggingService: dragging }
      );
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
    return Boolean(range)/* && ['P', 'BR', 'BODY']
      .indexOf($(range.startContainer).prop('tagName')) !== -1*/;
  }

  insertContent(editorId: any, dragging: DraggingService, contentHTML: string, options?: any): void {
    $('iframe:visible').contents().find('.drag-autopreview').remove(); // just in case
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

    if (/hidewhenclass/ig.test(contentHTML)) {
      console.info('this is hidewhen insertion');
      const $target = $(target);
      if (target && $target.hasClass('plominoGroupClass')) {
        /**
         * split hidewhen on 2 different spans
         */
        console.info('target ok and target is plominoGroupClass');
        let spans = contentHTML.split('</span>&nbsp;');
        if (spans.length > 1) {
          spans[0] = spans[0] + '</span>';
        }
        else {
          spans = contentHTML.split('</span><span class="plominoHidewhenClass');
          spans[0] = spans[0] + '</span>';
          spans[1] = '<span class="plominoHidewhenClass' + spans[1];
        }

        /* just in case */
        $('iframe:visible').contents()
          .find('.drag-autopreview').remove();

        $(spans[0]).insertBefore($target);
        $(spans[1]).insertAfter($target);
        
        $('iframe:visible').contents().click();
        editor.setDirty(true);
        return;
      }
      else {
        console.info('not target ok and target is plominoGroupClass',
        'target', $(target).get(0).outerHTML,
        '$(target).hasClass(\'plominoGroupClass\')',
        $(target).hasClass('plominoGroupClass'));
        contentHTML = `<p>${contentHTML}</p>`;
      }
    }

    if ($(contentHTML).hasClass('plominoActionClass')
      || $(contentHTML).hasClass('plominoFieldClass')
      || $(contentHTML).hasClass('plominoLabelClass')) {
      contentHTML = `<p>${contentHTML}</p>`;
    }

    console.log(target, options);
    
    if (options && !options.target) {
      const a = editor.getContent().length;
      
      editor.selection.select((<any>editor).getBody(), true);
      editor.selection.collapse(false);
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
          'this.rangeAccepted(range)', this.rangeAccepted(range),
          'target', target,
          'lastInsert', lastInsert);
        if (this.rangeAccepted(range)) {
          range.insertNode($content.get(0));
        }
        else {
          $content[
            lastInsert || !dragging.targetSideBottom 
            ? 'insertBefore': 'insertAfter'
          ]($(target));
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
    this.setContent(editorId, this.getContent(editorId), dragging);
    editor.setDirty(true);
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

import { PlominoFormFieldsSelectionService } from './../../../services/form-fields-selection/index';
import { PlominoActiveEditorService } from './../../../services/active-editor.service';
import { PlominoElementAdapterService } from './../../../services/element-adapter.service';
import { LogService } from './../../../services/log.service';
import { Observable, Subject } from 'rxjs/Rx';
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
  private logService: LogService,
  private adapter: PlominoElementAdapterService,
  private activeEditorService: PlominoActiveEditorService,
  private formFieldsSelection: PlominoFormFieldsSelectionService) {
    interface OneInTimeObservable<PlominoIFrameMouseMove> 
      extends Observable<PlominoIFrameMouseMove> {
      oneInTime: (delay: any) => Observable<PlominoIFrameMouseMove>;
    }

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
          
        if (range) {
          this.logService.info('range', range.startContainer, range.startOffset,
            range.commonAncestorContainer);
        }
        else {
          this.logService.warn('there is no range');
        }

        const currentDragCode = dragging.currentDraggingTemplateCode;
        const $currentDragNode = $(currentDragCode);

        if (!$currentDragNode.hasClass('drag-autopreview')) {
          $currentDragNode.addClass('drag-autopreview');
        }

        if (range && this.rangeAccepted(range)) {
          $(this.activeEditorService.getActive().getBody())
            .find('.drag-autopreview').remove();
          // console.log('insert A!3');
          range.insertNode($currentDragNode.get(0));
          dragging.targetRange = range;
          return;
        }
        const $iframeContents = $(this.activeEditorService.getActive()
          .getContainer().querySelector('iframe')).contents();
        const $latestTarget = $(
          $.merge(
            $iframeContents.find('#tinymce *:first').toArray(),
            $iframeContents.find('#tinymce *:not(.mce-visual-caret)')
            .filter(function (i, tag) {
              return $(tag).html().replace(/&nbsp;/g, '').trim() 
                && !($(tag).closest('.plominoGroupClass').length 
                && !$(tag).hasClass('plominoGroupClass'));
              }).toArray()
          )
        ).last();
        $iframeContents.find('.drag-autopreview').remove();
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
        $(this.activeEditorService.getActive().getBody())
          .find('.drag-autopreview').remove();
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
      $(this.activeEditorService.getActive().getBody())
        .find('.drag-autopreview').remove();

      const $preview = $(dragging.currentDraggingTemplateCode);
      // if (!hoverAtBottom) {
      //   $preview.css({
      //     top: `-${ groupHeight * 2 + 25 }px`,
      //     position: 'relative'
      //   });
      // }
      
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
        // console.log('insert B!2');
        $templateB.insertAfter(dragging.target);
      }
      else {
        if (!$preview.hasClass('drag-autopreview')) {
          $preview.addClass('drag-autopreview');
        }
        // console.log('insert B!1', dragging.target);
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
        $(this.activeEditorService.getActive().getBody())
          .find('.drag-autopreview').remove();
      }
      
      dragging.target = null;
      dragging.targetRange = null;
    });
  }

  log(func = 'null', msg = 'empty', requiredLevel = 1) {
    if (this.logLevel >= requiredLevel) {
      this.logService.info(func, msg);
    }
  }

  setContent(editorId: any, contentHTML: string, dragging?: any): void {
    // console.warn('setContent called', editorId);
    const editor = this.getEditor(editorId);
    
    if (!editor) {
      this.logService.warn('setContent', 'error: editor not found', editorId);
      return;
      // const $iframe = $(this.activeEditorService.getActive()
      //     .getContainer().querySelector('iframe'));
      // editorId = $iframe.attr('id').replace('_ifr', '');
      // editor = tinymce.EditorManager.editors[editorId];
    }

    contentHTML = contentHTML.replace(/(<p>(?:&nbsp;|\s)<\/p>(\s+)?)+?$/i, '');
    contentHTML = contentHTML
      .replace(/plominoGroupClass mceNonEditable plominoSubformClass/gi,
        'mceNonEditable plominoSubformClass');
    contentHTML = contentHTML + ('<p>&nbsp;</p>'.repeat(30));

    editor.setContent(contentHTML);
    this.log('setContent contentHTML', contentHTML, 3);

    const that = this;
    if (editor) {
      $(editor.getBody())
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
  
      $(editor.getBody()).off('.cmb')
      .on('mousemove.cmb', function (evt) {
        if (
          $(evt.target).closest('.plominoGroupClass:not(.drag-autopreview)').length
          && dragging.currentDraggingData
        ) {
          evt.preventDefault();
        }
        else {
          that.iframeMouseMoveEvents.next({
            originalEvent: <MouseEvent>evt.originalEvent,
            draggingService: dragging,
            editorId
          });
        }
      })
      .on('mouseleave.cmb', function (evt) {
        if (
          $(evt.target).closest('.plominoGroupClass:not(.drag-autopreview)').length
        ) {
          evt.preventDefault();
        }
        else {
          that.iframeMouseLeaveEvents.next({
            draggingService: dragging
          });
        }
      });
    }
  }

  getContent(editorId: any): string {
    let editor = this.getEditor(editorId);

    if (!editor) {
      const $iframe = this.activeEditorService.getActive()
        ? $(this.activeEditorService.getActive()
          .getContainer().querySelector('iframe'))
        : $('iframe:visible');
      if ($iframe.attr('id')) {
        editorId = $iframe.attr('id').replace('_ifr', '');
        editor = tinymce.EditorManager.editors[editorId];
      }
      else {
        return null;
      }
    }
    const content = editor.getContent();
    return content.replace(/(<p>(?:&nbsp;|\s)<\/p>(\s+)?)+?$/i, '');
  }

  selectAndRemoveElementById(editorId: any, elementId: string): void {
    const editor = this.getEditor(editorId);
    if (editor) {
      try {
        editor.focus(); //give the editor focus
        editor.selection.select(editor.dom.select(`#${ elementId }`)[0]);
        editor.selection.collapse(0);
        editor.dom.remove(elementId);
    
        this.log('selectAndRemoveElementById elementId', elementId, 2);
      }
      catch (e) {}
    }
  }

  insertRawHTML(editorId: any, contentHTML: string): void {
    const editor = this.getEditor(editorId);
    editor.execCommand('mceInsertRawHTML', false, contentHTML);
    this.log('insertRawHTML contentHTML', contentHTML);
  }

  rangeAccepted(range: Range): boolean {
    return Boolean(range)/* && ['P', 'BR', 'BODY']
      .indexOf($(range.startContainer).prop('tagName')) !== -1*/;
  }

  insertContent(editorId: any, dragging: DraggingService, contentHTML: string, options?: any): void {
    $(this.activeEditorService.getActive().getBody())
      .find('.drag-autopreview').remove(); // just in case
    let editor = this.getEditor(editorId);

    const INSERT_EVENT_UNIQUE = Math.random().toString();

    if (!editor) {
      const $iframe = $(this.activeEditorService.getActive()
          .getContainer().querySelector('iframe'));
      editorId = $iframe.attr('id').replace('_ifr', '');
      editor = tinymce.EditorManager.editors[editorId];
    }

    let target: HTMLElement = null;
    
    if (options.target) {
      target = options.target;
    }

    if (contentHTML === '<div class="plominoGroupClass mceNonEditable"></div>') {
      return;
    }

    if (/hidewhenclass/ig.test(contentHTML)) {
      this.logService.info('this is hidewhen insertion');
      const $target = $(target);
      if (target && $target.hasClass('plominoGroupClass')) {
        /**
         * split hidewhen on 2 different spans
         */
        this.logService.info('target ok and target is plominoGroupClass');
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
        $(this.activeEditorService.getActive().getBody())
          .find('.drag-autopreview').remove();

        $(spans[0]).insertBefore($target);
        // console.log('insert B!3');
        $(spans[1]).insertAfter($target);

        const $iframe = $(this.activeEditorService.getActive()
          .getContainer().querySelector('iframe'));
        
        $iframe.contents().click();
        editor.setDirty(true);
        this.activeEditorService.turnActiveEditorToLoadingState(false);
        return;
      }
      else {
        this.logService.info('not target ok and target is plominoGroupClass',
        'target', $(target).get(0).outerHTML,
        '$(target).hasClass(\'plominoGroupClass\')',
        $(target).hasClass('plominoGroupClass'));
        contentHTML = `<p>${contentHTML}</p>`;
        this.activeEditorService.turnActiveEditorToLoadingState(false);
      }
    }

    if ($(contentHTML).hasClass('plominoActionClass')
      || $(contentHTML).hasClass('plominoFieldClass')) {
      contentHTML = `<p>${contentHTML}</p>`;
      this.activeEditorService.turnActiveEditorToLoadingState(false);
    }
    else if ($(contentHTML).hasClass('plominoLabelClass')) {
      contentHTML = `<span class="mceNonEditable">${contentHTML}</span>`;
      // contentHTML = `<p contenteditable="false">${contentHTML}</p>`;
      this.activeEditorService.turnActiveEditorToLoadingState(false);
    }

    const $iframeContents = $(this.activeEditorService.getActive()
          .getContainer().querySelector('iframe')).contents();
    const $latestTarget = $(
      $.merge(
        $iframeContents.find('#tinymce *:first').toArray(),
        $iframeContents.find('#tinymce *:not(.mce-visual-caret)')
        .filter(function (i, tag) {
          return $(tag).html().replace(/&nbsp;/g, '').trim() 
            && !($(tag).closest('.plominoGroupClass').length 
            && !$(tag).hasClass('plominoGroupClass'));
          }).toArray()
      )
    ).last();
    
    if (typeof target === 'boolean' || target === null) {
      target = $latestTarget.get(0);
    }

    if (target && $(target).closest('.plominoGroupClass').length) {
      target = $(target).closest('.plominoGroupClass').get(0);
    }
    
    if (options && !options.target && !target) {
      const a = editor.getContent().length;
      
      editor.selection.select((<any>editor).getBody(), true);
      editor.selection.collapse(false);
      editor.execCommand('mceInsertContent', false, contentHTML, options);
      this.activeEditorService.turnActiveEditorToLoadingState(false);
      
      setTimeout(() => {
        if (a === editor.getContent().length) {
          editor.execCommand('mceInsertContent', false, contentHTML, options);
        }
      }, 100);
    }
    else {
      if (target) {
        const $content = $(contentHTML);
        const lastInsert = $latestTarget.get(0) === target;
        const range = dragging.targetRange;
        this.logService.info(
          'target && !options, dragging.targetRange', dragging.targetRange,
          'this.rangeAccepted(range)', this.rangeAccepted(range),
          'target', target,
          'lastInsert', lastInsert);

        if (this.rangeAccepted(range)) {
          $content.attr('data-event-unique', INSERT_EVENT_UNIQUE)
          // console.log('insert A!2');
          range.insertNode($content.get(0));
        }
        else {
          // const $first = $iframeContents.find('#tinymce *:first');
          // $content[lastInsert && $first.get(0) === target ? 'insertBefore' :'insertAfter']($(target))
          //   .attr('data-event-unique', INSERT_EVENT_UNIQUE);
          // console.log('insert B!5');
          
          $content.insertAfter($(target))
            .attr('data-event-unique', INSERT_EVENT_UNIQUE);

          if (!$content.is(':visible')) {
            $content.insertAfter($latestTarget)
              .attr('data-event-unique', INSERT_EVENT_UNIQUE);
          }
        }

        const $iframe = $(this.activeEditorService.getActive()
          .getContainer().querySelector('iframe'));
        
        $iframe.contents().click();
        this.activeEditorService.turnActiveEditorToLoadingState(false);
      }
      else {
        this.logService.info(
          '!target && !options, dragging.targetRange', dragging.targetRange);
        editor.execCommand('mceInsertContent', false, contentHTML);
        this.activeEditorService.turnActiveEditorToLoadingState(false);
      }
    }

    $('.drop-zone').remove();

    dragging.targetRange = null;
    this.changeDetector.markForCheck();
    this.setContent(editorId, this.getContent(editorId), dragging);
    editor.setDirty(true);
    this.log('insertContent contentHTML', contentHTML);

    if ($(contentHTML).html().indexOf('data-plominoid="defaultLabel"') !== -1) {
      /** if content is a label then click on it to show settings */
      const $label = $(this.activeEditorService.getActive().getBody())
        .find('.plominoLabelClass').filter(function () {
          return INSERT_EVENT_UNIQUE === $(this).parent().attr('data-event-unique');
        });
      
      if ($label.length) {
        this.adapter.select($label);
        this.formFieldsSelection.selectField(
          { id: 'defaultLabel', parent: editorId, type: 'label' }
        );
  
        $('a[href="#palette-tab-1-panel"] > span').click();
      }
    }
  }

  selectDOM(editorId: any, selector: string): HTMLElement[] {
    const editor = this.getEditor(editorId);
    try {
      return editor.dom.select(selector);
    } catch (e) {
      this.log('selectDOM DOM cannot be selected selector', selector);
      return [];
    }
  }

  selectContent(editorId: any, contentHTML: any): any {
    const editor = this.getEditor(editorId);
    try {
      return editor.selection.select(contentHTML);
    } catch (e) {
      this.log('selectContent content cannot be selected contentHTML', contentHTML);
      return false;
    }
  }

  setSelectionContent(editorId: any, contentHTML: any): any {
    const editor = this.getEditor(editorId);
    try {
      return editor.selection.setContent(contentHTML);
    } catch (e) {
      this.log('selectContent content cannot be setted contentHTML', contentHTML);
      return false;
    }
  }

  replaceContent(editorId: any, contentHTML: string): void {
    const editor = this.getEditor(editorId);
    try {
      editor.execCommand('mceReplaceContent', false, contentHTML);
      this.log('replaceContent contentHTML', contentHTML);
    } catch (e) {
      this.log('replaceContent content cannot be replaced contentHTML', contentHTML);
    }
  }

  getCaretRangeFromMouseEvent(editorId: any, eventData: MouseEvent): Range {
    const editor = this.getEditor(editorId);

    const x = eventData.clientX;
    const y = eventData.clientY;

    const caretRange = tinymce.dom.RangeUtils
      .getCaretRangeFromPoint(x, y, editor.getDoc());

    this.log('getCaretRangeFromMouseEvent', caretRange, 4);
    return caretRange;
  }

  setRange(editorId: any, range: any) {
    const editor = this.getEditor(editorId);
    editor.selection.setRng(range);
  }

  private getEditor(id: string) {
    const edId = id ? id.split('/').pop() : null;
    return tinymce.get(edId);
  }
}

import { TemplatesService } from './templates.service';
import { Injectable } from '@angular/core';

import { Subject } from 'rxjs/Subject';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class DraggingService {
  draggingData$: Subject<any> = new Subject<any>();
  customPaletteDragEvent$: Subject<any> = new Subject<any>();
  customPaletteDragEventCancel$: Subject<any> = new Subject<any>();
  customPaletteDragMouseMoveInIFrameEvent$: Subject<any> = new Subject<any>();
  customPaletteDragMouseMoveOutIFrameEvent$: Subject<any> = new Subject<any>();
  currentDraggingData: PlominoDraggingData = null;
  previousDraggingData: PlominoDraggingData = null;
  currentDraggingTemplateCode: string;
  target: JQuery = null;

  constructor(private templateService: TemplatesService) {}
  
  setDragging(data?: any): void {
    if (data !== false && data !== null) {
      this.currentDraggingData = <PlominoDraggingData>data;
      // preload the widget code
      let {parent, templateId} = this.currentDraggingData;

      if (data['@type'] === 'PlominoTemplate' && !this.currentDraggingData.resolved) {
        console.log('this.currentDraggingData', this.currentDraggingData);
        const widgetCode = this.currentDraggingData.template.layout;
        this.templateService
        .getTemplate(parent, templateId)
        .subscribe((widgetCode: string) => {
          this.currentDraggingTemplateCode = widgetCode;
  
          if (this.currentDraggingData.eventData) {
            const $dragCursor = $(this.currentDraggingTemplateCode);
    
            $dragCursor.css({
              position: 'absolute',
              display: 'block',
            });
  
            $dragCursor.attr('id', 'drag-data-cursor');
            $dragCursor.css('pointer-events', 'none');
            $('body').append($dragCursor);
  
            this.startDragging(
              this.currentDraggingData.eventData
            );
          }
        });
      }
      else {
        this.previousDraggingData = this.currentDraggingData === null 
          ? null : Object.assign(this.currentDraggingData);
        this.currentDraggingData = null;
      }
    }
    else {
      console.log('null dragData');
      this.previousDraggingData = this.currentDraggingData === null 
        ? null : Object.assign(this.currentDraggingData);
      this.currentDraggingData = null;
    }
    
    this.draggingData$.next(data);
  }

  somethingIsDragging(): boolean {
    return this.currentDraggingData !== null;
  }

  getDragging(): Observable<any> {
    return this.draggingData$.asObservable();
  }

  /**
   * Event happens when user stop dragging the component on the tinymce editor
   */
  onPaletteCustomDragEvent(): Observable<any> {
    return this.customPaletteDragEvent$.asObservable();
  }

  /**
   * Event happens when user stop dragging the component out of the tinymce editor
   */
  onPaletteCustomDragEventCancel(): Observable<any> {
    return this.customPaletteDragEventCancel$.asObservable();
  }

  /**
   * Event happens while user dragging the component through the tinymce editor
   */
  onPaletteCustomDragMMIIEvent(): Observable<any> {
    return this.customPaletteDragMouseMoveInIFrameEvent$.asObservable();
  }

  /**
   * Event happens while user dragging the component out of the tinymce editor
   */
  onPaletteCustomDragMMOIEvent(): Observable<any> {
    return this.customPaletteDragMouseMoveOutIFrameEvent$.asObservable();
  }

  private startDragging(e: MouseEvent) {
    $(document)
    .on('mousemove.drgs', this.drag.bind(this))
    .on('mouseup.drgs', this.stopDragging.bind(this));

    $('iframe:visible').contents()
    .on('mousemove.drgs', ((e: any) => this.drag(e, true)).bind(this))
    .on('mouseup.drgs', ((e: any) => this.stopDragging(e, true)).bind(this));

    this.drag(e);
  }

  private drag(e: MouseEvent, iframe?: boolean) {
    const pos = this.getMousePos(e);
    const offset = $('iframe:visible').offset();
  
    if (pos === null) {
        this.stopDragging(e);
        return;
    }

    $('.drop-zone').remove();
    $('iframe:visible').contents()
      .find('body,html')
      .css('pointer-events', 'none !important');

    if (iframe && offset) {
      $('#drag-data-cursor')
      .css('top', pos.y + offset.top - 10)
      .css('left', pos.x + offset.left - 5);

      this.moveMouseEventInIFrameCallback(e);
      // console.log('1', document.elementFromPoint(pos.x + offset.top, pos.y + offset.left));
    }
    else {
      $('#drag-data-cursor').css('top', pos.y - 10).css('left', pos.x - 5);

      const inIFrame = pos.x >= offset.left && pos.y >= offset.top;
      if (inIFrame) {
        /**
         * turn state out -> in
         */
        this.moveMouseEventOutIFrameCallback(e);
        this.moveMouseEventInIFrameCallback(e);
      }
      else {
        this.moveMouseEventOutIFrameCallback(e);
      }
    }
  }

  private moveMouseEventInIFrameCallback(eventData: MouseEvent) {
    this.customPaletteDragMouseMoveInIFrameEvent$.next(eventData);
  }

  private moveMouseEventOutIFrameCallback(eventData: MouseEvent) {
    this.customPaletteDragMouseMoveOutIFrameEvent$.next(eventData);
  }

  private stopDragging(eventData: MouseEvent, iframe?: boolean) {
    $(document).off('.drgs');
    // $(document).off('.drgs').off('.cme');
    // $('iframe:visible').contents().off('.drgs').off('.cme').off('.cmb');
    $('iframe:visible').contents().off('.drgs');
    // $('iframe:visible').contents().find('.plominoGroupClass').off('.cme');
    $('#drag-data-cursor').remove();

    console.log('stopDragging');

    const pos = this.getMousePos(eventData);
    const offset = $('iframe:visible').offset();
    const inIFrame = pos.x >= offset.left && pos.y >= offset.top;

    if (iframe || inIFrame) {
      this.customPaletteDragEvent$.next(eventData);
    }
    else {
      console.log('cancel', eventData);
      this.currentDraggingData = null;
      this.customPaletteDragEventCancel$.next(eventData);
    }
  }

  private getMousePos(e: MouseEvent): { x: number, y: number } {
    return typeof e.clientX !== "number" ? null : { x: e.clientX, y: e.clientY };
  }
}

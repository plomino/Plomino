import { WidgetService } from './widget.service';
import { PlominoActiveEditorService } from './active-editor.service';
import { LogService } from './log.service';
import { FieldsService } from './fields.service';
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
  targetRange: Range = null;
  targetSideBottom = true;

  subformDragEvent: Subject<MouseEvent> = new Subject<MouseEvent>();
  subformDragEvent$: Observable<MouseEvent> = this.subformDragEvent.asObservable();
  treeFieldDragEvent: Subject<{ mouseEvent: MouseEvent; fieldType: string }> 
    = new Subject<{ mouseEvent: MouseEvent; fieldType: string }>();
  treeFieldDragEvent$: Observable<{ mouseEvent: MouseEvent; fieldType: string }> 
    = this.treeFieldDragEvent.asObservable();
  dndType: any;

  constructor(
    private templateService: TemplatesService, 
    private log: LogService,
    private activeEditorService: PlominoActiveEditorService,
    private fieldsService: FieldsService,
    private widgetService: WidgetService,
  ) {}

  followDNDType(dndType: any) {
    this.dndType = dndType;
  }
  
  setDragging(data?: any): void {
    this.log.info('setDragging', data);
    if (data !== false && data !== null) {
      this.currentDraggingData = <PlominoDraggingData>data;
      // preload the widget code
      const {parent, templateId} = this.currentDraggingData;

      if (data['@type'] === 'PlominoTemplate' && !this.currentDraggingData.resolved) {
        this.log.info('this.currentDraggingData', this.currentDraggingData);
        const widgetCode = this.currentDraggingData.template.layout;
        this.log.info('widgetCode initialized', widgetCode);
        this.templateService
        .getTemplate(parent, templateId)
        .subscribe((widgetCode: string) => {
          this.currentDraggingTemplateCode = widgetCode;
          this.log.info('widgetCode updated', widgetCode);
  
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
      else if (data['@type'] === 'PlominoSubform' && !this.currentDraggingData.resolved) {
        this.currentDraggingTemplateCode = `
          <div class="drag-autopreview">
            <span class="plominoSubformClass mceNonEditable" data-plominoid="Subform">
            <h2>Subform</h2><input type="text" value='...'/>
            </span>
          </div>
        `;

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

          const eventData = this.currentDraggingData.eventData;
          const $target = (<HTMLElement> eventData.target)
            .classList.contains('tree-node--name') 
              ? $(eventData.target) 
              : $(eventData.target).find('.tree-node--name');
          const text = $target.text().trim();
          if (text) {
            this.templateService
              .getTemplate(parent, text, true)
              .subscribe((widgetCode: string) => {
                $dragCursor.html($(widgetCode).html());
                this.currentDraggingTemplateCode = `<div class="drag-autopreview">${ $dragCursor.html() }</div>`;
              });
          }
        }
      }
      else if (data['@type'] === 'PlominoPagebreak' && !this.currentDraggingData.resolved) {
        this.currentDraggingTemplateCode = `
          <div class="drag-autopreview">
            <hr class="plominoPagebreakClass">
          </div>
        `;

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
      }
      else if (data['@type'] === 'PlominoHidewhen' && !this.currentDraggingData.resolved) {
        this.log.info('hw this.currentDraggingData', this.currentDraggingData);

        this.currentDraggingTemplateCode = `
          <div class="drag-autopreview">
            <span class="plominoHidewhenClass mceNonEditable"
            data-plomino-position="start"
            contenteditable="false">&nbsp;</span>
            <span class="plominoHidewhenClass mceNonEditable"
            data-plomino-position="end"
            contenteditable="false">&nbsp;</span>
          </div>
        `;

        if (this.currentDraggingData.eventData) {
          const $dragCursor = $(this.currentDraggingTemplateCode);
  
          $dragCursor.css({
            position: 'absolute',
            display: 'block',
          });

          $dragCursor.attr('id', 'drag-data-cursor');
          $dragCursor.css('pointer-events', 'none');
          $dragCursor.css('transform', 'translate3d(0, 0, 0)');
          $('body').append($dragCursor);

          this.startDragging(
            this.currentDraggingData.eventData
          );
        }
      }
      else if (
        ['PlominoAction', 'PlominoLabel', 'PlominoField'].indexOf(data['@type']) !== -1
        && !this.currentDraggingData.resolved) {
        this.log.info('action/label/field this.currentDraggingData', this.currentDraggingData);

        (this.currentDraggingData.existingElementId 
          ? this.widgetService.getWidget(
              parent, data['@type'].replace('Plomino', '').toLowerCase(), 
              this.currentDraggingData.existingElementId
            )
          : this.fieldsService.getTemplate(
            parent, data['@type'].replace('Plomino', '').toLowerCase()
          )
        )
        .subscribe((widgetCode: string) => {
          this.currentDraggingTemplateCode = widgetCode;
  
          if (this.currentDraggingData.eventData) {
            const $dragCursor = $(`<div>${this.currentDraggingTemplateCode}</div>`);
    
            $dragCursor.css({
              position: 'absolute',
              display: 'block',
            });
  
            $dragCursor.attr('id', 'drag-data-cursor');
            $dragCursor.css('pointer-events', 'none');
            $dragCursor.css('z-index', 10000);
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
      this.log.info('null dragData');
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

    $(this.activeEditorService.getActive().getBody())
    .on('mousemove.drgs', ((e: any) => this.drag(e, true)).bind(this))
    .on('mouseup.drgs', ((e: any) => this.stopDragging(e, true)).bind(this));

    $(document)
    .on('keydown.drgs', (se: any) => {
      if (se.keyCode === 27) {
        this.stopDragging(e);
      }
    });

    this.drag(e);
  }

  private drag(e: MouseEvent, iframe?: boolean) {

    const activeEditor = this.activeEditorService.getActive();

    if (!activeEditor) {
      this.stopDragging(e);
      return;
    }

    const $iframe = $(activeEditor.getContainer().querySelector('iframe'));
    const pos = this.getMousePos(e);
    const offset = $iframe.offset();

    if (this.currentDraggingData === null) {
      this.stopDragging(e);
      return;
    }
  
    if (pos === null) {
        this.stopDragging(e);
        return;
    }

    $('.drop-zone').remove();
    $iframe
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
        $iframe.find('.drag-autopreview').remove();
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
    const activeEditor = this.activeEditorService.getActive();

    if (!activeEditor) {
      $(document).off('.drgs');
      $('#drag-data-cursor').remove();
      this.currentDraggingData = null;
      this.customPaletteDragEventCancel$.next(eventData);
      return;
    }

    const $iframe = $(activeEditor.getContainer().querySelector('iframe'));
    $(document).off('.drgs');
    $iframe.contents().off('.drgs');
    $(activeEditor.getBody()).off('.drgs');
    $('#drag-data-cursor').remove();

    this.log.info('stopDragging');

    const pos = this.getMousePos(eventData);
    const offset = $iframe.offset();
    const inIFrame = pos.x >= offset.left && pos.y >= offset.top;

    if (iframe || inIFrame) {
      this.customPaletteDragEvent$.next(eventData);
    }
    else {
      this.log.info('cancel', eventData);
      this.currentDraggingData = null;
      this.customPaletteDragEventCancel$.next(eventData);
    }
  }

  private getMousePos(e: MouseEvent): { x: number; y: number } {
    return typeof e.clientX !== "number" ? null : { x: e.clientX, y: e.clientY };
  }
}

import { Subject, Observable } from 'rxjs/Rx';
import { Injectable } from '@angular/core';

export const DS_TYPE = {
  EXISTING_WORKFLOW_ITEM: 'existing-wf-item',
  EXISTING_TREE_ITEM: 'existing-subform',
};

export const DS_FROM_PALETTE = [
  'workflowFormTask', 'workflowViewTask', 
  'workflowExternalTask', 'workflowProcess', 
  'workflowCondition', 'workflowGoto',
];

@Injectable()
export class WFDragControllerService {

  private wfEditorOffset: { left: number; top: number };
  private hovered: PlominoWorkflowItem;
  private hoveredId: number;

  receiver: Subject<ReceiverEvent> = new Subject();
  receiver$ = this.receiver.asObservable();

  private leave: Subject<ReceiverEvent> = new Subject();
  leave$ = this.leave.asObservable();

  private enter: Subject<ReceiverEvent> = new Subject();
  enter$ = this.enter.asObservable();

  private drop: Subject<ReceiverEvent> = new Subject();
  drop$ = this.drop.asObservable();

  private rebuildWorkflow: Subject<boolean> = new Subject();
  rebuildWorkflow$ = this.rebuildWorkflow.asObservable();

  private swapItems: Subject<{ a: number; b: number }> = new Subject();
  swapItems$ = this.swapItems.asObservable();

  constructor() {
    const leave = new Subject<ReceiverEvent>();
    const receiver$ = this.receiver$;

    const start$ = receiver$.filter((data) => data.eventName === 'start');
    const drop$ = receiver$.filter((data) => data.eventName === 'drop');
    const end$ = receiver$.filter((data) => data.eventName === 'end');

    start$.subscribe((data) => {
      if (data.dragServiceType === DS_TYPE.EXISTING_WORKFLOW_ITEM) {
        data.wfNode.classList.add('workflow-node--dragging');
      }
    });

    /**
     * remember enter mouse position
     * 
     * if leave mouse position === +/- 3px (enter pos) -> filter
     */

    const enterPosition = { x: 0, y: 0 };

    const enter$ = receiver$
      .filter((data) => data.eventName === 'enter')
      .filter((data) => {
        const xDiff = Math.abs(data.dragEvent.screenX - enterPosition.x);
        const yDiff = Math.abs(data.dragEvent.screenY - enterPosition.y);

        enterPosition.x = data.dragEvent.screenX;
        enterPosition.y = data.dragEvent.screenY;

        let $node = $(data.dragEvent.target).closest('.workflow-node');
        $node = $node.length ? $node : $(data.dragEvent.target);

        return $node.hasClass('workflow-node--root') || (xDiff > 12 || yDiff > 12);
      })
      .filter((data: ReceiverEvent) => {
        const $node = $(data.dragEvent.target).closest('.workflow-node');
        const hoveredId = $node.length ? +$node.attr('data-node-id') : 0;
    
        if (hoveredId && this.hoveredId !== hoveredId) {
          this.hoveredId = hoveredId;
          data.wfNode = $node.get(0);
          $('.plomino-workflow-editor__branches--virtual')
            .css('display', 'none');
          return true;
        }
        else {
          if (this.hoveredId && !$node.length) {
            data.wfNode = $('.workflow-node[data-node-id="' 
              + this.hoveredId +'"]').get(0);
            leave.next(data);
          }
          return false;
        }
      })
      .map((data) => {
        if (data.dragServiceType === DS_TYPE.EXISTING_WORKFLOW_ITEM) {
          $('.workflow-node--dropping')
            .removeClass('workflow-node--dropping');
          data.wfNode.classList.add('workflow-node--dropping');
        }

        return data;
      });
      
    enter$.subscribe(this.onItemEnter.bind(this));

    /* workflow mouse out */
    receiver$.subscribe((data) => {
      if (data.eventName === 'leave' 
        && data.dragServiceType !== DS_TYPE.EXISTING_WORKFLOW_ITEM
        && data.dragEvent.clientX < this.wfEditorOffset.left 
        || data.dragEvent.clientY < this.wfEditorOffset.top
      ) {
        // enter$
        this.rebuildWorkflow.next(true);
      }
      else if (data.eventName === 'start') {
        $('.plomino-workflow-editor__branches--virtual')
          .css('display', 'none');
      }
    });

    leave.asObservable()
      .map((data) => {
        if (!data.item) {
          data.item = {
            id: this.hoveredId,
            type: 'fake',
            children: []
          }
        }

        this.hoveredId = null;
      
        if (data.dragServiceType === DS_TYPE.EXISTING_WORKFLOW_ITEM) {
          // data.wfNode.classList.remove('workflow-node--dropping');
          $('.workflow-node--dropping')
            .removeClass('workflow-node--dropping');
        }
  
        return data;
      })
      .subscribe(this.onItemLeave.bind(this));
    
    Observable.merge(drop$, end$)
      .filter((data) => Boolean(this.hoveredId))
      .map((data) => {
        if (!data.item) {
          data.item = {
            id: this.hoveredId,
            type: 'fake',
            children: []
          }
        }

        this.hoveredId = null;

        $('.workflow-node--dropping')
          .removeClass('workflow-node--dropping');
        $('.workflow-node--dragging')
          .removeClass('workflow-node--dragging');

        $('.plomino-workflow-editor__branches--virtual')
          .removeAttr('style');

        return data;
      })
      .subscribe((data) => {
        if (data.eventName === 'drop') {
          this.onDrop(data);
        }
      });
  }

  registerWorkflowOffset(offset: { left: number; top: number }) {
    this.wfEditorOffset = offset;
  }

  receive(dragEvent: DragEvent, 
    eventName: 'enter'|'leave'|'start'|'end'|'drop'|'over', 
    dragServiceType: string, wfNode?: HTMLElement, item?: PlominoWorkflowItem
  ) {
    this.receiver.next({
      dragEvent, eventName, dragServiceType, wfNode, item
    });
  }

  getHoveredId() {
    return this.hoveredId;
  }

  onItemEnter(data: ReceiverEvent) {
    this.enter.next(data);
  }

  onItemLeave(data: ReceiverEvent) {
    this.leave.next(data);
  }

  onDrop(data: ReceiverEvent) {
    this.drop.next(data);
  }
}

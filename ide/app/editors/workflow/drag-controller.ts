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

  private wfEditorOffset: { left: number, top: number };
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

  private rebuildWorkflow: Subject<Boolean> = new Subject();
  rebuildWorkflow$ = this.rebuildWorkflow.asObservable();

  private swapItems: Subject<{ a: number, b: number }> = new Subject();
  swapItems$ = this.swapItems.asObservable();

  constructor() {
    const leave = new Subject<ReceiverEvent>();
    const drop$ = this.receiver$.filter((data) => data.eventName === 'drop');
    const end$ = this.receiver$.filter((data) => data.eventName === 'end');

    /* workflow mouse out */
    this.receiver$.subscribe((data) => {
      if (data.eventName === 'leave' 
        && data.dragServiceType !== DS_TYPE.EXISTING_WORKFLOW_ITEM
        && data.dragEvent.clientX < this.wfEditorOffset.left 
        || data.dragEvent.clientY < this.wfEditorOffset.top
      ) {
        this.rebuildWorkflow.next(true);
      }
      else if (data.eventName === 'start') {
        $('.plomino-workflow-editor__branches--virtual')
          .css('display', 'none');
      }
    });

    this.receiver$
      .filter((data) => data.eventName === 'enter')
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
          data.wfNode.classList.add('workflow-node--dropping');
        }

        return data;
      })
      .subscribe(this.onItemEnter.bind(this));

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
          data.wfNode.classList.remove('workflow-node--dropping');
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

  registerWorkflowOffset(offset: { left: number, top: number }) {
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

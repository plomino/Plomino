import { Component, ElementRef, ViewChild, ViewEncapsulation } from '@angular/core';
import { PlominoBlockPreloaderComponent } from '../../utility';
import { DND_DIRECTIVES } from 'ng2-dnd';
import { treeBuilder, WF_ITEM_TYPE } from './tree-builder';
import { PlominoWorkflowNodeSettingsComponent } from "../../palette-view";
import { PlominoWorkflowChangesNotifyService } from './workflow.changes.notify.service';
import { PlominoFormsListService, LogService, FormsService } from "../../services";

@Component({
  selector: 'plomino-workflow-editor',
  template: require('./workflow.component.html'),
  styles: [require('./workflow.component.css')],
  directives: [DND_DIRECTIVES, PlominoBlockPreloaderComponent],
  encapsulation: ViewEncapsulation.None,
})
export class PlominoWorkflowComponent {
  @ViewChild('workflowEditorNode') workflowEditorNode: ElementRef;
  tree: PlominoWorkflowItem = { id: 1, root: true, children: [] };
  latestTree: PlominoWorkflowItem = null;
  tmpOnTopFormItem: PlominoWorkflowItem = null;
  selectedItemRef: any;
  lastId: number = 4;
  itemSettingsDialog: HTMLDialogElement;

  constructor(
    private log: LogService,
    private formsService: FormsService,
    private workflowChanges: PlominoWorkflowChangesNotifyService,
    private formsList: PlominoFormsListService,
  ) {
    this.itemSettingsDialog = <HTMLDialogElement> 
      document.querySelector('#wf-item-settings-dialog');

    if (!this.itemSettingsDialog.showModal) {
      window['materialPromise'].then(() => {
        dialogPolyfill.registerDialog(this.itemSettingsDialog);
      });
    }

    Array.from(
      this.itemSettingsDialog
        .querySelectorAll('input[type="text"], select')
    )
    .forEach((input: HTMLInputElement|HTMLSelectElement) => {
      $(input).keyup((evd) => {
        if (evd.keyCode === 13) {
          this.apply2selected();
          this.itemSettingsDialog.close();
        }
      });
    });

    Array.from(
      this.itemSettingsDialog
        .querySelectorAll('.mdl-dialog__actions button')
    )
    .forEach((btn: HTMLElement) => {
      btn.addEventListener('click', (evt) => {
        if (btn.classList.contains('wf-item-settings-dialog__apply-btn')) {
          this.apply2selected();
        }
        this.itemSettingsDialog.close();
      });
    })
    // this.tree = {
    //   id: 1,
    //   root: true,
    //   children: [{
    //     id: 2,
    //     task: 'Fill in reason to contact',
    //     form: 'Contact Us',
    //     user: 'Anon',
    //     children: [
    //       {
    //         id: 3,
    //         condition: 'View Complaints',
    //         children: [
    //           {
    //             id: 4,
    //             process: 'Delete',
    //             user: 'Admin',
    //             children: []
    //           },
    //           {
    //             id: 5,
    //             process: 'Reply to user',
    //             user: 'Admin',
    //             children: []
    //           }
    //         ]
    //       }
    //     ]
    //   }],
    // };
  }

  ngOnInit() {
    this.buildWFTree();

    this.workflowChanges.onChangesDetect$
    .subscribe((kvData) => {
      /* update current task description */
      const item = this.selectedItemRef;
      if (item) {
        if (kvData.key === 'description') {
          item.title = kvData.value;
          $('.workflow-node--selected .workflow-node__task')
            .html(`Task: ${ item.title }`);
        }
      }
    });
  }

  findWFItemById(itemId: number, tree = this.tree): PlominoWorkflowItem {
    if (tree.id === itemId) {
      return tree;
    }
    if (tree.children) {
      for (let subTree of tree.children) {
        let result = this.findWFItemById(itemId, subTree);
        if (result) {
          return result;
        }
      }
    }
    return null;
  }

  /**
   * @param {JQuery} parentItem - closest .workflow-node to the mouse cursor
   */
  dragInsertPreview($parentItem: JQuery, dragData: { title: string, type: string }) {
    if ($parentItem.hasClass('workflow-node--dropping')) {
      return false; // do nothing
    }
    const previewItem: PlominoWorkflowItem = {
      id: -1,
      dropping: true,
      type: dragData.type,
      children: []
    };

    if (this.eventTypeIsTask(dragData.type)) {
      previewItem.title = 'Empty task';

      if (dragData.type === WF_ITEM_TYPE.FORM_TASK) {
        previewItem.form = '';
      }
      else if (dragData.type === WF_ITEM_TYPE.VIEW_TASK) {
        previewItem.view = '';
      }
    }
    else if (dragData.type === WF_ITEM_TYPE.PROCESS) {
      previewItem.title = 'Empty process';
    }
    else if (dragData.type === WF_ITEM_TYPE.GOTO) {
      previewItem.goto = 'nothing';
    }
    else if (dragData.type === WF_ITEM_TYPE.CONDITION) {
      previewItem.condition = '';

      const truePreviewItem: PlominoWorkflowItem = {
        id: -2,
        title: 'true process',
        dropping: true,
        type: WF_ITEM_TYPE.PROCESS,
        children: []
      };

      const falsePreviewItem: PlominoWorkflowItem = {
        id: -3,
        title: 'false process',
        dropping: true,
        type: WF_ITEM_TYPE.PROCESS,
        children: []
      };

      previewItem.children = [
        truePreviewItem, falsePreviewItem
      ];
    }

    /* copy original tree to temporary sandbox-tree */
    const sandboxTree = jQuery.extend(true, {}, this.tree);

    /* current preview way is just a way to temporary change the tree */
    let parentItem = this.findWFItemById(
      +$parentItem.attr('data-node-id'), sandboxTree
    );
    
    if (parentItem) {
      const parentChildren = jQuery.extend(true, {}, parentItem.children);
      parentItem.children = []; // do children empty

      Object.assign(previewItem.children, parentChildren); // copy with saving link

      parentItem.children.push(previewItem); // make previewItem child of parentItem

      /* compare trees - if they are equal then do nothing */
      if (this.latestTree !== null) {
        const hashA = JSON.stringify(sandboxTree);
        const hashB = JSON.stringify(this.latestTree);
        if (hashA === hashB) {
          this.log.info('equal trees, do nothing');
          return false;
        }
      }
      
      this.buildWFTree(sandboxTree);
    }

    // this.log.info($parentItem, parentItem);
  }

  onDragLeave(dragEvent: { dragData: any, mouseEvent: DragEvent }) {
    const event: DragEvent = dragEvent.mouseEvent;
    const $offset = $(this.workflowEditorNode.nativeElement).offset();

    if (event.clientX < $offset.left || event.clientY < $offset.top) {
      this.buildWFTree();
    }
  }

  getClosestWFItemToDragEvent(
    dragEvent: {
      dragData: { title: string, type: string },
      mouseEvent: DragEvent
    }
  ): JQuery {
    /* at first we need to detect closest node */
    const $target = $(dragEvent.mouseEvent 
      ? dragEvent.mouseEvent.target : (<any> dragEvent).target);
    let $relatedItem;

    /**
     * cases:
     * 
     * 1. div.workflow-node__view - closest .workflow-node
     * 2. li.plomino-workflow-editor__branch - find .workflow-node:first
     * 3. ul.plomino-workflow-editor__branches - find .workflow-node:first ?
     */

    if (
      $target.hasClass('plomino-workflow-editor__branch')
      || $target.hasClass('plomino-workflow-editor__branches')
    ) {
      $relatedItem = $target.find('.workflow-node:first');
    }
    else if ($target.closest('.workflow-node').length) {
      $relatedItem = $target.closest('.workflow-node');
    }
    else {
      $relatedItem = $(this.workflowEditorNode.nativeElement)
        .find('.workflow-node:last');
    }

    return $relatedItem;
  }

  generateNewId() {
    this.lastId = this.lastId + 1;
    return this.lastId;
  }

  isEmptySpace() {
    return !(this.tree && this.tree.children.length);
  }

  eventTypeIsTask(eventType: string) {
    return [
      WF_ITEM_TYPE.FORM_TASK, WF_ITEM_TYPE.VIEW_TASK, WF_ITEM_TYPE.EXT_TASK
    ].indexOf(eventType) !== -1;
  }

  onDragEnter(dragEvent: { dragData: any, mouseEvent: DragEvent }) {
    const dragData = dragEvent.dragData;

    const $wfItemClosest = this.getClosestWFItemToDragEvent(dragEvent);
    let allowedDrag = true;

    if (
      $wfItemClosest.hasClass('workflow-node--root')
      && (
        dragData.type === WF_ITEM_TYPE.PROCESS
        || dragData.type === WF_ITEM_TYPE.CONDITION
        || dragData.type === WF_ITEM_TYPE.GOTO
      )
    ) {
      allowedDrag = false;
    }
    // else if (
    //   !$wfItemClosest.hasClass('workflow-node--root') 
    //   && dragData.type === WF_ITEM_TYPE.CONDITION
    // ) {
    //   /** @todo: allowed drag related to bottom children element */
    //   allowedDrag = Boolean(
    //     $wfItemClosest.length 
    //     && $wfItemClosest.hasClass('workflow-node--task')
    //   );
    // }
    else if (
      !$wfItemClosest.hasClass('workflow-node--root') 
      && [WF_ITEM_TYPE.PROCESS,  WF_ITEM_TYPE.CONDITION].indexOf(dragData.type) !== -1
    ) {
      /** @todo: allowed drag related to bottom children element */
      allowedDrag = Boolean(
        $wfItemClosest.length 
        && $wfItemClosest
          .find('>.workflow-node__inner>.workflow-node__text--form')
          .length
      );
    }
    
    if (allowedDrag) {
      this.dragInsertPreview($wfItemClosest, dragData);
    }
  }

  allowDrop() {
    return ((dragData: any) => {
      if (this.isEmptySpace()) {
        return this.eventTypeIsTask(dragData.type);
      }
      
      return true;
    }).bind(this);
  }

  onDrop(dropEvent: any) {
    const sandboxTree = this.latestTree;
    const temporaryItem = this.findWFItemById(-1, sandboxTree);

    if (temporaryItem) {
      temporaryItem.dropping = false;
      temporaryItem.id = this.generateNewId();
  
      if (temporaryItem.type === WF_ITEM_TYPE.CONDITION) {
        const temporaryTrueProcessItem = this.findWFItemById(-2, sandboxTree);
        if (temporaryTrueProcessItem) {
          /* true process can be just branch continue */
          temporaryTrueProcessItem.dropping = false;
          temporaryTrueProcessItem.id = this.generateNewId();
        }
  
        const temporaryFalseProcessItem = this.findWFItemById(-3, sandboxTree);
        temporaryFalseProcessItem.dropping = false;
        temporaryFalseProcessItem.id = this.generateNewId();
      }
  
      this.tree = sandboxTree;
      this.buildWFTree();
    }
  }

  unselectAllWFItems() {
    const _unselectAllWFItems = (wfItem: PlominoWorkflowItem): void => {
      wfItem.selected = false;

      if (wfItem.children) {
        for (let subTree of wfItem.children) {
          _unselectAllWFItems(subTree);
        }
      }
    };

    _unselectAllWFItems(this.tree);
    this.workflowEditorNode.nativeElement
      .querySelectorAll('.workflow-node--selected')
      .forEach((selectedNode: HTMLElement) => {
        selectedNode.classList.remove('workflow-node--selected');
      });
  }

  onWFItemClicked($event: JQueryEventObject, $item: JQuery, item: PlominoWorkflowItem) {
    this.log.info($event, $item, item);

    if (!item.selected) {
      this.unselectAllWFItems();
      item.selected = true;
      this.selectedItemRef = item;
      $item.find('.workflow-node:first')
        .addClass('workflow-node--selected');
    }

    if (
      $event.target
        .classList.contains('plomino-workflow-editor__branch-plus-btn')
      || $event.target.parentElement
        .classList.contains('plomino-workflow-editor__branch-plus-btn')
    ) {
      return this.onConditionPlusClicked($event, $item, item);
    }

    $event.stopImmediatePropagation();
    // this.formsService.changePaletteTab(4);
    return true;
  }

  onWFItemDblClicked($event: JQueryEventObject, $item: JQuery, item: PlominoWorkflowItem) {
    if (
      $event.target
        .classList.contains('plomino-workflow-editor__branch-plus-btn')
      || $event.target.parentElement
        .classList.contains('plomino-workflow-editor__branch-plus-btn')
    ) {
      return false;
    }
    
    this.itemSettingsDialog
      .querySelector('#wf-item-settings-dialog__form')
      .innerHTML = this.formsList.getFiltered()
        .map((f: any) => `<option>${ f.url.split('/').pop() }</option>`)
        .join('');

    if (item.type === WF_ITEM_TYPE.GOTO) {
      const nodesList = Array.from(this.getTreeNodesMap().values());
      this.itemSettingsDialog
        .querySelector('#wf-item-settings-dialog__node')
        .innerHTML = nodesList.filter((n: any) => item.id !== n.id && n.id > 1)
          .map((n: any) => 
            `<option value="${ n.id }">#${ n.id } ${ n.title }</option>`
          )
          .join('');
    }
    
    Array.from(this.itemSettingsDialog
      .querySelectorAll('[data-key]'))
      .forEach((input: HTMLInputElement) => {
        $(input).val(item[input.dataset.key] || '');
      });
    
    Array.from(this.itemSettingsDialog
      .querySelectorAll('[data-typefor]'))
      .forEach((inputGroup: HTMLElement) => {
        if (!(new RegExp(item.type, 'g')).test(inputGroup.dataset.typefor)) {
          inputGroup.style.display = 'none';
        }
        else {
          inputGroup.style.display = 'block';
        }
      });
    
    this.itemSettingsDialog.showModal();
    $event.stopImmediatePropagation();
  }

  apply2selected() {
    const item = this.selectedItemRef;

    Array.from(this.itemSettingsDialog
      .querySelectorAll('[data-key]'))
      .forEach((input: HTMLInputElement) => {
        if (item.hasOwnProperty(input.dataset.key)) {
          item[input.dataset.key] = $(input).val();
        }
      });
    
    this.buildWFTree();
  }

  /** @todo: change algorythm */
  findWFFormItemOnTop(itemId: any, tree = this.tree): PlominoWorkflowItem {
    if (tree.id === itemId) {
      return tree;
    }
    if (tree.children) {
      for (let subTree of tree.children) {
        if (subTree.form) {
          this.tmpOnTopFormItem = subTree;
        }
        let result = this.findWFFormItemOnTop(itemId, subTree);
        if (result) {
          return result;
        }
      }
    }
    return null;
  }

  onWFItemMacroClicked($event: JQueryEventObject, $item: JQuery, item: PlominoWorkflowItem) {
    this.log.info('onWFItemMacroClicked', $event, item);
    $event.stopImmediatePropagation();
    $event.preventDefault();

    this.tmpOnTopFormItem = null;
    this.findWFFormItemOnTop(item.id);

    if (this.tmpOnTopFormItem) {
      const $resource = 
        $(`.tree-node--name:contains("${ this.tmpOnTopFormItem.form }")`)
          .filter((i, node: HTMLElement) => 
            $(node).text().trim() === this.tmpOnTopFormItem.form);

      $resource.click();
      setTimeout(() => {
        this.formsService.changePaletteTab(2);
      }, 100);
    }
    return false;
  }

  onConditionPlusClicked(
    $event: JQueryEventObject, $item: JQuery, item: PlominoWorkflowItem
  ) {
    this.log.info('condition plus');
    $event.stopImmediatePropagation();

    const newLogicItem: PlominoWorkflowItem = {
      id: this.generateNewId(),
      dropping: false,
      title: 'other logic way',
      type: WF_ITEM_TYPE.PROCESS,
      children: []
    };

    item.children.push(newLogicItem);
    this.buildWFTree();
  }

  getTreeNodesMap(tree = this.tree): Map<number, PlominoWorkflowItem> {
    const stackMap: Map<number, PlominoWorkflowItem> = new Map();
    
    const _iterate = (obj: PlominoWorkflowItem) => {
      for (const property in obj) {
        if (obj.hasOwnProperty(property)) {
          if (typeof obj[property] == "object") {
            _iterate(obj[property]);
          } else {
            stackMap.set(obj.id, obj);
          }
        }
      }
    }

    _iterate(tree);
    return stackMap;
  }

  buildWFTree(tree = this.tree) {
    this.latestTree = tree;

    const wfTree: HTMLElement = this.workflowEditorNode.nativeElement;
    
    wfTree.innerHTML = '';
    $(wfTree).append(
      treeBuilder.getBuildedTree({
        workingTree: tree, 
        onItemClick: this.onWFItemClicked.bind(this),
        onItemDblClick: this.onWFItemDblClicked.bind(this),
        onMacroClick: this.onWFItemMacroClicked.bind(this),
      })
    );

    return true;
  }
}

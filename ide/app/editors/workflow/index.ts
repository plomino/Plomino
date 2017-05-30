import { ElementService } from './../../services/element.service';
import { ObjService } from './../../services/obj.service';
import { PlominoSaveManagerService } from './../../services/save-manager/save-manager.service';
import { FakeFormData } from './../../utility/fd-helper/fd-helper';
import { PlominoHTTPAPIService } from './../../services/http-api.service';
import { Component, ElementRef, ViewChild, ViewEncapsulation, NgZone } from '@angular/core';
import { PlominoBlockPreloaderComponent } from '../../utility';
import { DND_DIRECTIVES } from 'ng2-dnd';
import { treeBuilder, WF_ITEM_TYPE } from './tree-builder';
import { PlominoWorkflowNodeSettingsComponent } from "../../palette-view";
import { PlominoWorkflowChangesNotifyService } from './workflow.changes.notify.service';
import { PlominoFormsListService, LogService, 
  FormsService, DraggingService } from "../../services";

const FORM_OR_VIEW_FROM_TREE = 'existing-subform';

@Component({
  selector: 'plomino-workflow-editor',
  template: require('./workflow.component.html'),
  styles: [require('./workflow.component.sources.css')],
  directives: [DND_DIRECTIVES, PlominoBlockPreloaderComponent],
  encapsulation: ViewEncapsulation.None,
})
export class PlominoWorkflowComponent {
  @ViewChild('workflowEditorNode') workflowEditorNode: ElementRef;
  tree: PlominoWorkflowItem = { id: 1, root: true, children: [] };
  latestTree: PlominoWorkflowItem = null;
  tmpOnTopFormItem: PlominoWorkflowItem = null;
  selectedItemRef: PlominoWorkflowItem;
  lastId: number = 4;
  itemSettingsDialog: HTMLDialogElement;
  $itemSettingsDialog: JQuery;
  latestUsingForm: any;

  constructor(
    private log: LogService,
    private formsService: FormsService,
    private elementService: ElementService,
    private workflowChanges: PlominoWorkflowChangesNotifyService,
    private formsList: PlominoFormsListService,
    private dragService: DraggingService,
    private api: PlominoHTTPAPIService,
    private saveManager: PlominoSaveManagerService,
    private zone: NgZone,
    private objService: ObjService,
  ) {
    if (!this.dragService.dndType) {
      this.dragService.followDNDType('nothing');
    }

    this.itemSettingsDialog = <HTMLDialogElement> 
      document.querySelector('#wf-item-settings-dialog');

    this.$itemSettingsDialog = $(this.itemSettingsDialog);

    Array.from(
      this.itemSettingsDialog
        .querySelectorAll('input[type="text"], select')
    )
    .forEach((input: HTMLInputElement|HTMLSelectElement) => {
      $(input).keyup((evd) => {
        if (evd.keyCode === 13) {
          this.apply2selected();
          this.$itemSettingsDialog.modal('hide');
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
        else if (btn.classList.contains('wf-item-settings-dialog__edit-btn')) {
          this.apply2selected();
          this.openResourceTab(this.selectedItemRef);
        }
        else if (btn.classList.contains('wf-item-settings-dialog__macro-btn')) {
          this.editMacro(this.selectedItemRef);
        }
        else if (btn.classList.contains('wf-item-settings-dialog__create-btn--form')) {
          this.saveManager.createNewForm((url, label) => {
            this.selectedItemRef.title = label;
            this.selectedItemRef.form = url.split('/').pop();
            this.buildWFTree();
          });
        }
        else if (btn.classList.contains('wf-item-settings-dialog__create-btn--view')) {
          this.saveManager.createNewView((url, label) => {
            this.selectedItemRef.title = label;
            this.selectedItemRef.view = url.split('/').pop();
            this.buildWFTree();
          });
        }
        this.$itemSettingsDialog.modal('hide');
      });
    });

    this.formsService.formIdChanged$
      .subscribe((data) => {
        const item = this.findWFItemByFormOrViewId(data.oldId.split('/').pop());
        if (item !== null) {
          item[
            item.type === WF_ITEM_TYPE.FORM_TASK ? 'form' : 'view'
            ] = data.newId.split('/').pop();
          this.buildWFTree();
        }
      })
  }

  getDBLink() {
    return `${ 
      window.location.pathname
      .replace('++resource++Products.CMFPlomino/ide/', '')
      .replace('/index.html', '')
    }`;
  }

  ngOnInit() {
    try {
      const dbLink = this.getDBLink();
      const fd = new FakeFormData(<any> $(`form[action*="${ dbLink }"]`).get(0));
      this.tree = JSON.parse(fd.get('form.widgets.IBasic.description'));

      if (!fd.get('form.widgets.IBasic.description') || !this.tree) {
        this.tree = { id: 1, root: true, children: [] };
      }
      
      this.lastId = Math.max(...Array.from(this.getTreeNodesMap().keys()));
      this.buildWFTree();
    }
    catch(e) {
      this.tree = { id: 1, root: true, children: [] };
      this.buildWFTree();
    }

    if (!this.tree.children.length) {
      this.tree.id = 1;
      this.lastId = 1;
    }

    setTimeout(() => $('tabset tab.active.tab-pane').css('background', '#fafafa'), 1);

    // $(document).keydown((eventData) => {
    //   if (this.selectedItemRef && (eventData.keyCode === 8 || eventData.keyCode === 46)
    //     && !(this.$itemSettingsDialog.data('bs.modal') || {}).isShown
    //   ) {
    //     /* delete the node */
    //     const workWithItemRecursive = (item: PlominoWorkflowItem) => {
    //       if (item.children.length) {
    //         item.children.forEach((child, index) => {
    //           if (child.id === this.selectedItemRef.id) {
    //             this.log.info('splice', child.id);
    //             item.children.splice(index, 1);
    //           }
    //           else {
    //             workWithItemRecursive(child);
    //           }
    //         });
    //       }
    //     };
    
    //     workWithItemRecursive(this.tree);
    //     this.buildWFTree();
    //   }

    //   eventData.stopImmediatePropagation();
    // });
  }

  findWFItemByFormOrViewId(fvId: string, tree = this.tree): PlominoWorkflowItem {
    if (tree.form === fvId || tree.view === fvId) {
      return tree;
    }
    if (tree.children) {
      for (let subTree of tree.children) {
        let result = this.findWFItemByFormOrViewId(fvId, subTree);
        if (result) {
          return result;
        }
      }
    }
    return null;
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

  findWFItemParentById(itemId: number, tree = this.tree): PlominoWorkflowItem {
    if (tree.children) {
      if (tree.children.filter((x: any) => x.id === itemId).length) {
        return tree;
      }
      for (let subTree of tree.children) {
        let result = this.findWFItemParentById(itemId, subTree);
        if (result) {
          return result;
        }
      }
    }
    return null;
  }

  deleteWFItem($e: any, $item: JQuery, targetItem: PlominoWorkflowItem) {
    /* delete the node */
    let result: PlominoWorkflowItem = null;
    let resultIndex: number = 0;
    const workWithItemRecursive = (item: PlominoWorkflowItem) => {
      if (item.children.length) {
        if (item.children.filter((x, i) => {
          if (x.id === targetItem.id) {
            resultIndex = i;
            return true;
          }
          else {
            return false;
          }
        }).length) {
          result = item;
        }
        else {
          item.children.forEach((child, index) => {
            workWithItemRecursive(child);
          });
        }
      }
    };

    workWithItemRecursive(this.tree);
    const $_: PlominoWorkflowItem[] = 
      (<any>Object).values($.extend({}, targetItem.children));
    result.children.splice(resultIndex, 1);
    result.children = result.children.concat($_);

    if (result.type === WF_ITEM_TYPE.CONDITION && !result.children.length) {
      this.deleteWFItem($e, $item, result);
    }
    else {
      const $wfItemClosest = $(
        `.workflow-node[data-node-id="${ targetItem.id }"]`
      );
      $wfItemClosest.fadeOut(100, () => {
        this.buildWFTree();
      });
    }
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
      children: (<any> dragData).children || []
    };

    if (this.dragService.dndType !== 'existing-wf-item') {
      if (this.eventTypeIsTask(dragData.type)) {
        previewItem.title = '';
  
        if (dragData.type === WF_ITEM_TYPE.FORM_TASK) {
          previewItem.form = '';
        }
        else if (dragData.type === WF_ITEM_TYPE.VIEW_TASK) {
          previewItem.view = '';
        }
      }
      else if (dragData.type === WF_ITEM_TYPE.PROCESS) {
        previewItem.title = '';
      }
      else if (dragData.type === WF_ITEM_TYPE.GOTO) {
        previewItem.goto = '';
      }
      else if (dragData.type === WF_ITEM_TYPE.CONDITION) {
        previewItem.condition = '';
  
        const truePreviewItem: PlominoWorkflowItem = {
          id: -2,
          title: '',
          dropping: true,
          type: WF_ITEM_TYPE.PROCESS,
          children: []
        };
  
        const falsePreviewItem: PlominoWorkflowItem = {
          id: -3,
          title: '',
          dropping: true,
          type: WF_ITEM_TYPE.PROCESS,
          children: []
        };
  
        previewItem.children = [
          truePreviewItem, falsePreviewItem
        ];
      }
  
      if (this.dragService.dndType.slice(0, 16) === FORM_OR_VIEW_FROM_TREE) {
        const dragFormData = this.dragService.dndType.slice(18).split('::');
        dragFormData.pop();
        previewItem.title = dragFormData.pop();
        previewItem[previewItem.type === WF_ITEM_TYPE.FORM_TASK 
          ? 'form' : 'view'] = dragFormData.pop().split('/').pop();
      }
    }

    /* copy original tree to temporary sandbox-tree */
    const sandboxTree = jQuery.extend(true, {}, this.tree);

    /* current preview way is just a way to temporary change the tree */
    const nodeId = +$parentItem.attr('data-node-id');
    let parentItem = this.findWFItemById(nodeId, sandboxTree);
    
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
      
      this.buildWFTree(sandboxTree, false);
    }

    // this.log.info($parentItem, parentItem);
  }

  onDragLeave(dragEvent: WFDragEvent) {
    const event: DragEvent = dragEvent.mouseEvent;
    const $offset = $(this.workflowEditorNode.nativeElement).offset();

    if (event.clientX < $offset.left || event.clientY < $offset.top) {
      this.buildWFTree();
    }
  }

  getClosestWFItemToDragEvent(dragEvent: WFDragEvent): JQuery {
    /* at first we need to detect closest node */
    let $target = $(dragEvent.mouseEvent 
      ? dragEvent.mouseEvent.target : (<any> dragEvent).target);
    let $relatedItem;

    if ($target.hasClass('plomino-workflow-editor__branch')) {
      const calculateDistance = ($elem: JQuery) => {
        const mouseX = dragEvent.mouseEvent.pageX;
        const mouseY = dragEvent.mouseEvent.pageY;
        return Math.floor(Math.sqrt(Math.pow(
          mouseX - ($elem.offset().left+($elem.width()/2)), 2) + 
          Math.pow(mouseY - ($elem.offset().top+($elem.height()/2)), 2)));
      }

      const dMap = new Map();
      const dList: number[] = [];
      const $nodes = $('.workflow-node:not(.workflow-node--virtual)');
      if ($nodes.length) {
        $nodes.each(function () {
          const distance = calculateDistance($(this));
          dList.push(distance);
          dMap.set(distance, $(this));
        });
        $target = dMap.get(Math.min(...dList));
        // console.log('$target changed on fly');
      }
    }

    // console.log('$target dnd', dragEvent.mouseEvent, $target.get(0).outerHTML);

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
      $relatedItem = $target.find('.workflow-node:not(.workflow-node--virtual):last');
      // this.log.info('first condition', $relatedItem);
    }
    else if ($target.closest('.workflow-node:not(.workflow-node--virtual)').length) {
      $relatedItem = $target.closest('.workflow-node:not(.workflow-node--virtual)');
      // this.log.info('second condition', $relatedItem);
    }
    else {
      $relatedItem = $(this.workflowEditorNode.nativeElement)
        .find('.workflow-node:not(.workflow-node--virtual):last');
      // this.log.info('third condition', $relatedItem);
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

  /**
   * Is the eventType is PROCESS or CONDITION
   * @param eventType 
   */
  eTypeIsProcCond(eventType: string) {
    return [
      WF_ITEM_TYPE.PROCESS, WF_ITEM_TYPE.CONDITION
    ].indexOf(eventType) !== -1;
  }

  isDragAllowed($wfItemClosest: JQuery, dType: string): Boolean {
    let allowedDrag = true;
    const closestExists = Boolean($wfItemClosest.length);
    const onGoto = closestExists && $wfItemClosest.hasClass('workflow-node--goto');
    const onCond = closestExists && $wfItemClosest.hasClass('workflow-node--condition');
    const onRoot = closestExists && $wfItemClosest.hasClass('workflow-node--root');
    const pathIsForm = '>.workflow-node__inner>.workflow-node__text--form';
    const onForm = closestExists && $wfItemClosest.find(pathIsForm).length;
    const onTask = closestExists && $wfItemClosest.hasClass('workflow-node--task');
    const cp = '>.plomino-workflow-editor__branches>.plomino-workflow-editor__branch';
    const $childBranch = closestExists ? $wfItemClosest.parent().find(cp).first() : $();
    const chBranchExists = $childBranch.length;
    const $childNode = $childBranch.find('>.workflow-node');
    const belowIsThere = chBranchExists && $childNode.length;
    const belowIsTask = belowIsThere && $childNode.hasClass('workflow-node--task');
    const belowIsProc = belowIsThere && $childNode.hasClass('workflow-node--process');
    const belowIsCond = belowIsThere && $childNode.hasClass('workflow-node--condition');
    const belowIsProcOrCond = belowIsProc || belowIsCond;
    const isProcOrCondDrag = this.eTypeIsProcCond(dType);
    const isGotoDrag = dType === WF_ITEM_TYPE.GOTO;
    const isTaskDrag = this.eventTypeIsTask(dType);
    const lvl = closestExists ? +$wfItemClosest.attr('data-node-level') : 0;

    if (onCond || onGoto || (onRoot && (isProcOrCondDrag || isGotoDrag))) {
      allowedDrag = false;
    }
    else if (!onRoot && isProcOrCondDrag) {
      /** @todo: allowed drag related to bottom children element */
      // allowedDrag = onForm && !belowIsProcOrCond;
      allowedDrag = true;
    }
    else if (!onRoot && isTaskDrag) {
      // allowedDrag = !onTask && !belowIsTask;
      allowedDrag = true;
    }
    if (allowedDrag && isGotoDrag) {
      allowedDrag = !Boolean($('[data-node-level="' + (lvl + 1) + '"]').length);
    }

    return allowedDrag;
  }

  /**
   * ng2-dnd event callback
   * @param dragEvent 
   */
  onDragEnter(dragEvent: WFDragEvent) {
    /**
     * closest to mouse cursor worfklow item
     * parent item to drag preview
     */
    const $wfItemClosest = this.getClosestWFItemToDragEvent(dragEvent);
    if (this.isDragAllowed($wfItemClosest, dragEvent.dragData.type)) {
      this.dragInsertPreview($wfItemClosest, dragEvent.dragData);
    }
  }

  /**
   * When the user drags existing f/v onto wf-editor's item or drags existing wf-items
   * @param eventData 
   * @param item 
   * @param item 
   */
  onItemDragEnter(eventData: DragEvent, $item: JQuery, item: PlominoWorkflowItem) {
    const dndType = this.dragService.dndType;
    
    if (dndType === 'existing-wf-item' 
      && this.selectedItemRef.id !== item.id
    ) {
      eventData.stopImmediatePropagation();
      const dragEvent = <any> {
        dragData: item,
        mouseEvent: eventData,
      };
      // eventData.preventDefault();
      /**
       * step 1: temporary variable for item
       * step 2: assign selected attributes to item
       */
      // const itemParent = this.findWFItemParentById(item.id);
      const selectedParent = this.findWFItemParentById(this.selectedItemRef.id);
      if (selectedParent.children.filter((x: any) => x.id === item.id).length) {
        /* swap */
        const $wfItemClosest = this.getClosestWFItemToDragEvent(dragEvent);
        $('.workflow-node--dropping').removeClass('workflow-node--dropping');
        $wfItemClosest.addClass('workflow-node--dropping');
      }
      
      return true;
    }
    else if (dndType.slice(0, 16) === FORM_OR_VIEW_FROM_TREE) {
      eventData.stopImmediatePropagation();

      const dragEvent = {
        dragData: {
          title: '',
          type: dndType.slice(18).split('::').pop() === 'Views' 
            ? WF_ITEM_TYPE.VIEW_TASK : WF_ITEM_TYPE.FORM_TASK
        },
        mouseEvent: eventData,
      };
      const $wfItemClosest = this.getClosestWFItemToDragEvent(dragEvent);
      if (this.isDragAllowed($wfItemClosest, dragEvent.dragData.type)) {
        this.dragInsertPreview($wfItemClosest, dragEvent.dragData);
      }
    }
    return true;
  }

  /**
   * fires when the user drags something on workflow-editor div
   * native html5 event
   * special for existing forms/views from tree
   * @param eventData 
   */
  wfDragEnterNativeEvent(eventData: DragEvent) {
    if (this.dragService.dndType.slice(0, 16) === FORM_OR_VIEW_FROM_TREE) {
      const dragFormData = this.dragService.dndType.slice(18).split('::');
      this.onDragEnter({
        dragData: {
          title: '',
          type: dragFormData.pop() === 'Views'
            ? WF_ITEM_TYPE.VIEW_TASK : WF_ITEM_TYPE.FORM_TASK
        },
        mouseEvent: eventData
      });
    }
  }

  wfDragLeaveNativeEvent(eventData: DragEvent) {
    if (this.dragService.dndType.slice(0, 16) === FORM_OR_VIEW_FROM_TREE) {
      const dragFormData = this.dragService.dndType.slice(18).split('::');
      this.onDragLeave({
        dragData: {
          title: '',
          type: dragFormData.pop() === 'Views'
            ? WF_ITEM_TYPE.VIEW_TASK : WF_ITEM_TYPE.FORM_TASK
        },
        mouseEvent: eventData
      });
    }
  }

  wfDropNativeEvent(eventData: DragEvent) {
    if (this.dragService.dndType.slice(0, 16) === FORM_OR_VIEW_FROM_TREE) {
      this.onDrop();
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

  onDrop() {
    const sandboxTree = this.latestTree;
    const temporaryItem = this.findWFItemById(-1, sandboxTree);

    if (temporaryItem) {
      temporaryItem.dropping = false;
      temporaryItem.id = this.generateNewId();

      console.log('temporaryItem', temporaryItem);
  
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

  targetIsHoverPlus(eventTarget: Element) {
    return eventTarget.parentElement.parentElement.parentElement
        .classList.contains('workflow-node--condition')
      || eventTarget
        .classList.contains('workflow-node--condition')
      || eventTarget.parentElement
        .classList.contains('workflow-node--condition')
      || eventTarget.parentElement.parentElement
        .classList.contains('workflow-node--condition');
  }

  targetIsDeleteBtn(eventTarget: Element) {
    return eventTarget.parentElement.parentElement
        .classList.contains('workflow-node__bubble-delete')
      || eventTarget
        .classList.contains('workflow-node__bubble-delete')
      || eventTarget.parentElement
        .classList.contains('workflow-node__bubble-delete');
  }

  targetIsVirtual(eventTarget: Element) {
    return eventTarget.classList.contains('workflow-node--virtual')
      || eventTarget.parentElement.parentElement.parentElement
        .classList.contains('workflow-node--virtual')
      || eventTarget.parentElement.parentElement
        .classList.contains('workflow-node--virtual')
      || eventTarget.parentElement
        .classList.contains('workflow-node--virtual');
  }

  onWFItemClicked($e: JQueryEventObject, $i: JQuery, itm: PlominoWorkflowItem, r = false) {
    this.log.info($e, $i, itm, r);
    $e.stopImmediatePropagation();
    const isDelBtn = this.targetIsDeleteBtn($e.target);
    const isCreate = (<HTMLElement> $e.target).dataset.create;
    const isVirtual = this.targetIsVirtual($e.target);

    if (!r && !itm.selected && !isDelBtn && !isCreate && !isVirtual) {
      this.unselectAllWFItems();
      itm.selected = true;
      this.selectedItemRef = itm;
      $i.find('.workflow-node:first')
        .addClass('workflow-node--selected');
    }

    if (!r && isDelBtn) {
      return this.deleteWFItem($e, $i, itm);
    }
    else if (!r && this.targetIsHoverPlus($e.target)) {
      return this.onHoverPlusClicked($e, $i, itm);
    }
    else if (!r && $e.target.classList.contains('workflow-node__text-modal-link')) {
      if ($e.target.parentElement
        .classList.contains('workflow-node__text--form')
        || $e.target.parentElement
        .classList.contains('workflow-node__text--view')) {
        this.openResourceTab(itm);
      }
      else if ($e.target.parentElement
        .classList.contains('workflow-node__text--process')) {
        /* process modal */
        this.showModal(itm, true);
      }
      else {
        /* just modal */
        this.showModal(itm);
      }
    }
    else if (isCreate) {
      this.log.info('go create from menu');
      const _target = (<HTMLElement> $e.target);
      const creatingType = _target.dataset.create;
      const $wfItemClosest = $(
        `.workflow-node[data-node-id="${ _target.dataset.target }"]`
      );
      this.dragService.followDNDType('wf-menu-dnd-callback');
      this.dragInsertPreview($wfItemClosest, { title: '', type: creatingType });
      this.onDrop();
    }
    else if (itm.type === WF_ITEM_TYPE.GOTO && itm.goto) {
      $('.workflow-node[data-node-id="' + itm.goto +'"]').get(0).scrollIntoView(false);
    }

    return true;
  }

  showModal(item: PlominoWorkflowItem, processModal = false) {
    if (!this.selectedItemRef) {
      this.log.error('nothing selected');
      return false;
    }
    this.itemSettingsDialog
      .querySelector('#wf-item-settings-dialog__form')
      .innerHTML = this.formsList.getFiltered()
        .map((f: any) => `<option>${ f.url.split('/').pop() }</option>`)
        .join('');

    this.itemSettingsDialog
      .querySelector('#wf-item-settings-dialog__view')
      .innerHTML = this.formsList.getViews()
        .map((f: any) => `<option>${ f.url.split('/').pop() }</option>`)
        .join('');

    if (item.type === WF_ITEM_TYPE.GOTO) {
      const nodesList = Array.from(this.getTreeNodesMap().values());
      this.itemSettingsDialog
        .querySelector('#wf-item-settings-dialog__node')
        .innerHTML = nodesList.filter((n: any) => item.id !== n.id && n.id > 1)
          .map((n: any) => 
            `<option value="${ n.id }:::${ n.title }">#${ n.id } ${ n.title }</option>`
          )
          .join('');
    }
    
    Array.from(this.itemSettingsDialog
      .querySelectorAll('[data-key]'))
      .forEach((input: HTMLInputElement) => {
        $(input).val(item[input.dataset.key] || '');

        if ((input.dataset.key === 'form' && item.type === WF_ITEM_TYPE.FORM_TASK) 
          || (input.dataset.key === 'view' && item.type === WF_ITEM_TYPE.VIEW_TASK)
        ) {
          $('.wf-item-settings-dialog__create-btn')
            .css('visibility', Boolean(item[input.dataset.key]) ? 'hidden' : 'visible');
          $('.wf-item-settings-dialog__edit-btn')
            .css('visibility', Boolean(!item[input.dataset.key]) ? 'hidden' : 'visible');
          if (!Boolean(item[input.dataset.key])) {
            $(input).change((eventData) => {
              $('.wf-item-settings-dialog__create-btn').css('visibility', 'hidden');
              $('.wf-item-settings-dialog__edit-btn').css('visibility', 'visible');
            });
          }
        }
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

    this.latestUsingForm = {};
    if (processModal) {
      this.itemSettingsDialog
        .querySelectorAll('[data-typefor]')
        .forEach((inputGroup: HTMLElement) => {
          if (inputGroup.dataset.typefor === 'processModal') {
            inputGroup.style.display = 'block';
          }
          else {
            inputGroup.style.display = 'none';
          }
        });
      // this.loadFormMacro(item);
      // const $wd = this.$itemSettingsDialog.find('#wf-item-settings-dialog__wd');
    }
    else {
      this.clearFormMacro();
    }
    
    this.$itemSettingsDialog.modal({
      show: true, backdrop: false
    });
  }

  clearFormMacro(): void {
    this.$itemSettingsDialog.find('#wf-item-settings-dialog__wd').html('');
  }

  loadFormMacro(item: PlominoWorkflowItem): void {
    /* step 1: get form url ontop */
    const $wd = this.$itemSettingsDialog.find('#wf-item-settings-dialog__wd');
    this.tmpOnTopFormItem = null;
    this.findWFFormItemOnTop(item.id);
    if (!this.tmpOnTopFormItem || !this.tmpOnTopFormItem.form) {
      $wd.html('');
      return;
    }
    /* step 2: run loading */
    let htmlBuffer = '';
    $wd.html(`
      <div id="p2" class="mdl-progress mdl-js-progress 
        mdl-progress__indeterminate"></div>
      <div>&nbsp;</div>
    `);
    componentHandler.upgradeDom();

    /* step 3: load form settings */

    const formURL = `${ this.getDBLink() }/${ this.tmpOnTopFormItem.form }`;
    this.objService.getFormSettings(formURL).subscribe((htmlFS) => {
      /* step 4: cut <ul class="plomino-macros" ...</ul> and read it in data */
      try {
        const $htmlFS = $(htmlFS);
        this.latestUsingForm = {
          action: $htmlFS.find('form[data-pat-autotoc]').attr('action'),
          $form: $htmlFS.find('form[data-pat-autotoc]')
        };
        htmlBuffer = $htmlFS.find('ul.plomino-macros').get(0).outerHTML;
        htmlBuffer = `<label style="margin-bottom: 15px; margin-top: 10px">
          Optionally select the code builder rule 
          which implements this process</label>${ htmlBuffer }`;
      }
      catch(e) {
        $wd.html('');
        return;
      }

      window['MacroWidgetPromise'].then((MacroWidget: any) => {
        /* step 5: clear html of dialog, put data in html of dialog */
        $wd.html(htmlBuffer);
  
        /* step 6: loading finished: inject macrowidget */
        const $widget = $wd.find('ul.plomino-macros');
        if ($widget.length) {
          this.zone.runOutsideAngular(() => {
            // $widget.find('input').prop('disabled', true);
            new MacroWidget($widget);
          });

          try {
            delete (<any>jQuery)._data(document, 'events').focusin;
          } catch(e) {}
        }
  
        /* step 7: put radios */
        // $wd.find('.plomino-macros-rule:last').remove();
        // $(document)
        //   .off('macros_selector_refresh')
        //   .on('macros_selector_refresh', () => {
          $wd.find('.plomino-macros-rule').each((i, e) => {
            if (!item.macroId) {
              item.macroId = 1;
            }
            const $r = $(`<input type="radio" name="macro-radio" 
              style="margin-right: 6pt;
              margin-left: 6pt; position: relative; top: 3pt; float: left;"
              ${ item.macroId === i + 1 ? 'checked' : '' }
              value="${ i + 1 }">`);
            const text = $(e).find('.plomino_edit_macro')
              .toArray().map((_e: HTMLElement) => _e.innerText).join(', ');
            if (!item.macroText) {
              item.macroText = text;
              this.buildWFTree();
            }
            $r.click(() => {
              item.macroId = i + 1;
              item.macroText = text;
              this.buildWFTree();
            });
            $(e).prepend($r);
            $(e).find('.select2-container').css('width', '95%');
          });
        });
      // });
    });
  }

  onWFItemDblClicked($event: JQueryEventObject, $i: JQuery, item: PlominoWorkflowItem) {
    // if (this.targetIsHoverPlus($event.target) || this.targetIsVirtual($event.target)) {
    //   return false;
    // }
    
    // this.selectedItemRef = item;
    // this.showModal(item);
    $event.stopImmediatePropagation();
    return this.onWFItemClicked($event, $i, item);
  }

  apply2selected() {
    const item = this.selectedItemRef;

    Array.from(this.itemSettingsDialog
      .querySelectorAll('[data-key]'))
      .forEach((input: HTMLInputElement) => {
        if (item.hasOwnProperty(input.dataset.key)
          || (this.eventTypeIsTask(item.type) && input.dataset.key === 'title')
          || (this.eventTypeIsTask(item.type) && input.dataset.key === 'process')
          || (item.type === WF_ITEM_TYPE.PROCESS && input.dataset.key === 'process')
        ) {
          item[input.dataset.key] = $(input).val();

          if (input.dataset.key === 'goto') {
            const _data = item.goto.split(':::');
            item.goto = _data[0];
            item.gotoLabel = _data[1];
          }
        }
      });
    
    this.buildWFTree();

    /* if it is a process - take fields rules and save */
    if (item.type === WF_ITEM_TYPE.PROCESS && this.latestUsingForm.action) {
      const fd = new FormData();

      this.latestUsingForm.$form.find('input,textarea,select')
        .each((i: number, element: HTMLInputElement) => {
          if (['form.widgets.IHelpers.helpers:list', 
            'form.buttons.save', 'form.buttons.cancel'].indexOf(element.name) === -1) {
            fd.append(element.name, $(element).val());
          }
        });

      this.itemSettingsDialog
        .querySelectorAll('input[name="form.widgets.IHelpers.helpers:list"]')
        .forEach((input: HTMLInputElement) => {
          fd.append('form.widgets.IHelpers.helpers:list', $(input).val());
        });

      fd.append('form.buttons.save', 'Save');
      
      this.api.postWithOptions(this.latestUsingForm.action, fd, {})
        .subscribe((data: Response) => {
          console.log('OMG', data);
        });
    }
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

  openResourceTab(item: PlominoWorkflowItem) {
    const key = item.type === WF_ITEM_TYPE.VIEW_TASK ? 'view' : 'form';
    const $resource = 
      $(`.tree-node--name:contains("${ item[key] }")`)
        .filter((i, node: HTMLElement) => 
          $(node).text().trim() === item[key]);
  
    $resource.click();
  }

  editMacro(item: PlominoWorkflowItem) {
    this.tmpOnTopFormItem = null;
    this.findWFFormItemOnTop(item.id);

    if (this.tmpOnTopFormItem) {
      this.openResourceTab(this.tmpOnTopFormItem);
      setTimeout(() => {
        this.formsService.changePaletteTab(2);
      }, 100);
    }
  }

  onWFItemMacroClicked($e: JQueryEventObject, $i: JQuery, item: PlominoWorkflowItem) {
    this.log.info('onWFItemMacroClicked', $e, item);
    $e.stopImmediatePropagation();
    $e.preventDefault();

    this.editMacro(item);
    return false;
  }

  onHoverPlusClicked($e: JQueryEventObject, $i: JQuery, item: PlominoWorkflowItem) {
    this.log.info('hover plus');
    $e.stopImmediatePropagation();

    const newLogicItem: PlominoWorkflowItem = {
      id: this.generateNewId(),
      dropping: false,
      title: '',
      type: WF_ITEM_TYPE.PROCESS,
      children: []
    };

    item.children.push(newLogicItem);
    this.buildWFTree();
  }

  /**
   * Can be cached on built?
   * @param tree 
   */
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

  onItemDragStart(eventData: DragEvent, $item: JQuery, item: PlominoWorkflowItem) {
    this.dragService.followDNDType('existing-wf-item');
    this.selectedItemRef = item;
    $item.addClass('workflow-node--dragging');
    eventData.stopImmediatePropagation();
    return true;
  }

  onItemDragLeave(eventData: DragEvent, $item: JQuery, item: PlominoWorkflowItem) {
    const dndType = this.dragService.dndType;
    if (dndType === 'existing-wf-item'
      && this.selectedItemRef.id !== item.id) {
      eventData.stopImmediatePropagation();
    }
    else if (dndType.slice(0, 16) === FORM_OR_VIEW_FROM_TREE) {
      const $offset = $item.offset();
  
      if (eventData.clientX < $offset.left || eventData.clientY < $offset.top) {
        this.buildWFTree();
      }
    }
    return true;
  }

  onItemDragEnd(eventData: DragEvent, $item: JQuery, item: PlominoWorkflowItem) {
    const dndType = this.dragService.dndType;
    if (dndType === 'existing-wf-item') {
      // console.log('onItemDragEnd', item);
      $item.removeClass('workflow-node--dragging');
      $('.workflow-node--dropping').removeClass('workflow-node--dropping');
      eventData.stopImmediatePropagation();
    }
    return true;
  }

  onItemDrop(eventData: DragEvent, $item: JQuery, item: PlominoWorkflowItem) {
    const dndType = this.dragService.dndType;
    if (dndType === 'existing-wf-item') {
      $('.workflow-node--dropping').removeClass('workflow-node--dropping');
      eventData.stopImmediatePropagation();

      const selectedParent = this.findWFItemParentById(this.selectedItemRef.id);
      if (selectedParent.children.filter((x: any) => x.id === item.id).length) {
        const tmp = jQuery.extend(true, {}, item);
        for (let key of Object.keys(item)) {
          if (!this.selectedItemRef.hasOwnProperty(key)) {
            delete item[key];
          }
        }
        for (let key of Object.keys(this.selectedItemRef)) {
            item[key] = this.selectedItemRef[key];
            if (!tmp.hasOwnProperty(key)) {
              delete this.selectedItemRef[key];
            }
        }
        for (let key of Object.keys(tmp)) {
            this.selectedItemRef[key] = tmp[key];
        }
  
        this.buildWFTree();
      }
    }
    else if (dndType.slice(0, 16) === FORM_OR_VIEW_FROM_TREE) {
      return this.onDrop();
    }
    return true;
  }

  buildWFTree(tree = this.tree, autosave = true) {
    this.latestTree = tree;

    const wfTree: HTMLElement = this.workflowEditorNode.nativeElement;
    
    wfTree.innerHTML = '';
    $(wfTree).append(
      treeBuilder.getBuildedTree({
        workingTree: tree, 
        onItemClick: this.onWFItemClicked.bind(this),
        onItemDblClick: this.onWFItemDblClicked.bind(this),
        onMacroClick: this.onWFItemMacroClicked.bind(this),
        onDragStart: this.onItemDragStart.bind(this),
        onDragEnter: this.onItemDragEnter.bind(this),
        onDragLeave: this.onItemDragLeave.bind(this),
        onDragEnd: this.onItemDragEnd.bind(this),
        onDrop: this.onItemDrop.bind(this),
      })
    );

    componentHandler.upgradeDom();

    if (autosave) {

      this.elementService.updateDBSettings({
        'description': JSON.stringify(this.tree)
          .replace(/,"(selected|dropping)":(false|true)/g, '')
      }).subscribe((response) => {});

      const dbLink = `${ 
        window.location.pathname
        .replace('++resource++Products.CMFPlomino/ide/', '')
        .replace('/index.html', '')
      }`;
  
      const fd = new FakeFormData(<any> $(`form[action*="${ dbLink }"]`).get(0));
      fd.set('form.widgets.IBasic.description', JSON.stringify(this.tree)
        .replace(/,"(selected|dropping)":(false|true)/g, ''));
      // fd.set('form.buttons.save', 'Save');
  
      // this.api
      //   .postWithOptions(`${ dbLink }/@@edit`, fd.build(), {})
      //   .subscribe((response) => {});
    }

    return true;
  }
}

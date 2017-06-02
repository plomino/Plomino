import { WFDragControllerService, DS_TYPE, DS_FROM_PALETTE } from './drag-controller';
import { TreeStructure } from './tree-structure';
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

@Component({
  selector: 'plomino-workflow-editor',
  template: require('./workflow.component.html'),
  styles: [require('./workflow.component.sources.css')],
  directives: [DND_DIRECTIVES, PlominoBlockPreloaderComponent],
  providers: [WFDragControllerService],
  encapsulation: ViewEncapsulation.None,
})
export class PlominoWorkflowComponent {
  @ViewChild('workflowEditorNode') workflowEditorNode: ElementRef;
  tree: TreeStructure;
  latestTree: TreeStructure = null;
  tmpOnTopFormItem: PlominoWorkflowItem = null;
  selectedItemRef: PlominoWorkflowItem;
  itemSettingsDialog: HTMLDialogElement;
  $itemSettingsDialog: JQuery;
  latestUsingForm: any;
  editorOffset: { top: number, left: number };
  enteredItemId: number = 0;

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
    private dragController: WFDragControllerService,
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
    let tree;

    try {
      const dbLink = this.getDBLink();
      const fd = new FakeFormData(<any> $(`form[action*="${ dbLink }"]`).get(0));
      tree = JSON.parse(fd.get('form.widgets.IBasic.description'));

      if (!fd.get('form.widgets.IBasic.description')) {
        tree = { id: 1, root: true, children: [] };
      }
    }
    catch(e) {
      tree = { id: 1, root: true, children: [] };
    }

    if (!tree.children.length) {
      tree.id = 1;
    }

    this.tree = new TreeStructure(tree);
    this.buildWFTree(this.tree, false);

    this.editorOffset = $(this.workflowEditorNode.nativeElement).offset();
    this.dragController.registerWorkflowOffset(this.editorOffset);
    this.dragController.rebuildWorkflow$.subscribe(() => {
      this.buildWFTree(this.tree, false);
    });

    this.dragController.enter$
      .map((data: ReceiverEvent) => {
        if (!data.item) {
          data.item = this.tree.getItemById(this.dragController.getHoveredId());
        }
        return data;
      })
      .subscribe(this.onItemDragEnter.bind(this));
    
    this.dragController.drop$
      .map((data: ReceiverEvent) => {
        if (data.item && data.item.type === 'fake') {
          data.item = this.tree.getItemById(data.item.id);
        }
        return data;
      })
      .subscribe(this.onDrop.bind(this));
    
    this.dragController.leave$
      .map((data: ReceiverEvent) => {
        if (data.item && data.item.type === 'fake') {
          data.item = this.tree.getItemById(data.item.id);
        }
        return data;
      })
      .subscribe(this.onItemDragLeave.bind(this));

    setTimeout(() => $('tabset tab.active.tab-pane').css('background', '#fafafa'), 1);
  }

  findWFItemByFormOrViewId(fvId: string, tree = this.tree): PlominoWorkflowItem {
    let result: PlominoWorkflowItem = null;

    this.tree.iterate((item) => {
      if (item.form === fvId || item.view === fvId) {
        result = item;
      }
    });

    return result;
  }

  deleteWFItem($e: any, $item: JQuery, targetItem: PlominoWorkflowItem) {
    if (targetItem.type === WF_ITEM_TYPE.CONDITION) {
      this.elementService.awaitForConfirm('This action will remove the branches below')
      .then(() => {
        this.tree.deleteBranchByTopItemId(targetItem.id);
        this.buildWFTree();
      })
      .catch(() => {});
    }
    else {
      this.tree.deleteNodeById(targetItem.id);

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

    /* copy original tree to temporary sandbox-tree */
    const sandboxTree = this.tree.createSandbox();

    /* current preview way is just a way to temporary change the tree */
    const nodeId = +$parentItem.attr('data-node-id');
    let parentItem = sandboxTree.getItemById(nodeId);

    if (this.dragService.dndType !== DS_TYPE.EXISTING_WORKFLOW_ITEM) {
      
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

        if (parentItem.type === WF_ITEM_TYPE.CONDITION) {
          previewItem.type = WF_ITEM_TYPE.PROCESS;
          previewItem.title = '';
        }
        else {
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
      }
  
      if (this.dragService.dndType.slice(0, 16) === DS_TYPE.EXISTING_TREE_ITEM) {
        const dragFormData = this.dragService.dndType.slice(18).split('::');
        dragFormData.pop();
        previewItem.title = dragFormData.pop();
        previewItem[previewItem.type === WF_ITEM_TYPE.FORM_TASK 
          ? 'form' : 'view'] = dragFormData.pop().split('/').pop();
      }
    }
    
    if (parentItem) {
      sandboxTree.pushNewItemToParentById(previewItem, parentItem.id);

      /* compare trees - if they are equal then do nothing */
      if (this.latestTree !== null) {
        if (sandboxTree.getCountOfNodes() === this.latestTree.getCountOfNodes()) {
          const hashA = sandboxTree.toJSON();
          const hashB = this.latestTree.toJSON();
          if (hashA === hashB) {
            return false;
          }
        }
      }
      
      this.buildWFTree(sandboxTree, false);
    }
  }

  onDragLeave(dragEvent: WFDragEvent) {
    // console.log('onDragLeave', dragEvent.target);
    // const event: DragEvent = dragEvent.mouseEvent;
    // const $offset = $(this.workflowEditorNode.nativeElement).offset();

    // if (event.clientX - 5 < $offset.left || event.clientY < $offset.top) {
    //   this.buildWFTree(this.tree, false);
    // }
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
      }
    }

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
    }
    else if ($target.closest('.workflow-node:not(.workflow-node--virtual)').length) {
      $relatedItem = $target.closest('.workflow-node:not(.workflow-node--virtual)');
    }
    else {
      $relatedItem = $(this.workflowEditorNode.nativeElement)
        .find('.workflow-node:not(.workflow-node--virtual):last');
    }

    return $relatedItem;
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
    const onBranch = closestExists && $wfItemClosest.hasClass('workflow-node--process');
    const onRoot = closestExists && $wfItemClosest.hasClass('workflow-node--root');
    // const pathIsForm = '>.workflow-node__inner>.workflow-node__text--form';
    // const onForm = closestExists && $wfItemClosest.find(pathIsForm).length;
    // const onTask = closestExists && $wfItemClosest.hasClass('workflow-node--task');
    // const cp = '>.plomino-workflow-editor__branches>.plomino-workflow-editor__branch';
    // const $childBranch = closestExists ? $wfItemClosest.parent().find(cp).first() : $();
    // const chBranchExists = $childBranch.length;
    // const $childNode = $childBranch.find('>.workflow-node');
    // const belowIsThere = chBranchExists && $childNode.length;
    // const belowIsTask = belowIsThere && $childNode.hasClass('workflow-node--task');
    // const belowIsProc = belowIsThere && $childNode.hasClass('workflow-node--process');
    // const belowIsCond = belowIsThere && $childNode.hasClass('workflow-node--condition');
    // const belowIsProcOrCond = belowIsProc || belowIsCond;
    const isProcOrCondDrag = this.eTypeIsProcCond(dType);
    const isBranchDrag = dType === WF_ITEM_TYPE.CONDITION;
    const isGotoDrag = dType === WF_ITEM_TYPE.GOTO;
    // const isTaskDrag = this.eventTypeIsTask(dType);
    const lvl = closestExists ? +$wfItemClosest.attr('data-node-level') : 0;

    if ((onCond && !isBranchDrag) || onGoto 
      || (onRoot && (isProcOrCondDrag || isGotoDrag))
    ) {
      allowedDrag = false;
    }
    // else if (!onRoot && isProcOrCondDrag) {
    //   /** @todo: allowed drag related to bottom children element */
    //   // allowedDrag = onForm && !belowIsProcOrCond;
    //   allowedDrag = true;
    // }
    // else if (!onRoot && isTaskDrag) {
    //   // allowedDrag = !onTask && !belowIsTask;
    //   allowedDrag = true;
    // }
    if (allowedDrag && isGotoDrag) {
      allowedDrag = !Boolean($('[data-node-level="' + (lvl + 1) + '"]').length);
    }

    if (!allowedDrag) {
      console.log('NOT ALLOWED');
    }

    return allowedDrag;
  }

  isSwapAllowed(itemA: PlominoWorkflowItem, itemB: PlominoWorkflowItem): Boolean {
    const isBranch = (item: PlominoWorkflowItem) => 
      item.type === WF_ITEM_TYPE.PROCESS;
    const isCondition = (item: PlominoWorkflowItem) => 
      item.type === WF_ITEM_TYPE.CONDITION;
    const isGoto = (item: PlominoWorkflowItem) => 
      item.type === WF_ITEM_TYPE.GOTO;
    const isLowestElementInBranch = (item: PlominoWorkflowItem) => 
      !item.children.length;

    const bothItems = (query: (item: PlominoWorkflowItem) => Boolean) => 
      query(itemA) && query(itemB);
    const oneOfItems = (query: (item: PlominoWorkflowItem) => Boolean) => 
      query(itemA) || query(itemB);
    
    if (bothItems(isBranch)) {
      return true;
    }
    else if (oneOfItems(isBranch)) {
      /* probably there should be put, not drag */
      return false;
    }
    else if (oneOfItems(isCondition)) {
      return false;
    }
    else if (bothItems(isGoto)) {
      return true;
    }
    else if (oneOfItems(isGoto)) {
      return isGoto(itemA) 
        ? isLowestElementInBranch(itemB) 
        : isLowestElementInBranch(itemA);
    }
    return true;
  }

  onDrop(data: ReceiverEvent = null) {
    if (data && data.dragServiceType === DS_TYPE.EXISTING_WORKFLOW_ITEM) {
      /* swap items */
      if (this.isSwapAllowed(this.selectedItemRef, data.item)) {
        this.log.info('items swapped', this.selectedItemRef.id, data.item.id);
        this.tree.swapNodesByIds(this.selectedItemRef.id, data.item.id);
        this.buildWFTree();
      }
      else {
        this.buildWFTree(this.tree, false);
      }
    }
    else {
      const sandboxTree = this.latestTree;
      const temporaryItem = sandboxTree.getItemById(-1);
      this.enteredItemId = null;
  
      if (temporaryItem) {
        sandboxTree.makeItemReal(temporaryItem);
    
        if (temporaryItem.type === WF_ITEM_TYPE.CONDITION) {
          const temporaryTrueProcessItem = sandboxTree.getItemById(-2);
          sandboxTree.makeItemReal(temporaryTrueProcessItem);
    
          const temporaryFalseProcessItem = sandboxTree.getItemById(-3);
          sandboxTree.makeItemReal(temporaryFalseProcessItem);
        }
    
        this.tree = sandboxTree;
        this.buildWFTree();
      }
    }
  }

  onItemDragLeave(data: ReceiverEvent) {
    if (data.dragServiceType !== DS_TYPE.EXISTING_WORKFLOW_ITEM) {
      this.enteredItemId = null;
      this.buildWFTree(this.tree, false);
    }
  }

  onItemDragEnter(data: ReceiverEvent) {
    if (data.dragServiceType !== DS_TYPE.EXISTING_WORKFLOW_ITEM) {
      /* drag from palette */
      const dragEvent = {
        dragData: {
          title: '',
          type: data.dragServiceType.slice(0, 16) === DS_TYPE.EXISTING_TREE_ITEM 
            ? (data.dragServiceType.slice(18).split('::').pop() === 'Views' 
            ? WF_ITEM_TYPE.VIEW_TASK : WF_ITEM_TYPE.FORM_TASK) : data.dragServiceType
        },
        mouseEvent: data.dragEvent,
      };
      if (this.isDragAllowed($(data.wfNode), dragEvent.dragData.type)) {
        this.dragInsertPreview($(data.wfNode), dragEvent.dragData);
      }
    }
  }

  unselectAllWFItems() {
    this.tree.iterate((wfItem) => {
      wfItem.selected = false;
    });

    this.workflowEditorNode.nativeElement
      .querySelectorAll('.workflow-node--selected')
      .forEach((selectedNode: HTMLElement) => {
        selectedNode.classList.remove('workflow-node--selected');
      });
  }

  checkTarget(eventTarget: Element, className: string) {
    return eventTarget.parentElement.parentElement.parentElement
        .classList.contains(className)
      || eventTarget.classList.contains(className)
      || eventTarget.parentElement.classList.contains(className)
      || eventTarget.parentElement.parentElement.classList.contains(className);
  }

  targetIsHoverPlus(eventTarget: Element) {
    return this.checkTarget(eventTarget, 'workflow-node--condition');
  }

  targetIsDeleteBtn(eventTarget: Element) {
    return this.checkTarget(eventTarget, 'workflow-node__bubble-delete');
  }

  targetIsHoverAddBelowBtn(eventTarget: Element) {
    return this.checkTarget(eventTarget, 
      'plomino-workflow-editor__branch-add-below-bubble-btn');
  }

  targetIsVirtual(eventTarget: Element) {
    return this.checkTarget(eventTarget, 'workflow-node--virtual');
  }

  onWFItemClicked($e: JQueryEventObject, $i: JQuery, itm: PlominoWorkflowItem, r = false) {
    this.log.info($e, $i, itm, r);
    $e.stopImmediatePropagation();
    const isDelBtn = this.targetIsDeleteBtn($e.target);
    const isCreate = (<HTMLElement> $e.target).dataset.create;
    const isVirtual = this.targetIsVirtual($e.target);
    const isAddBelow = this.targetIsHoverAddBelowBtn($e.target);

    if (!r && !itm.selected && !isDelBtn && !isCreate && !isVirtual && !isAddBelow) {
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
      else if (itm.type === WF_ITEM_TYPE.PROCESS || $e.target.parentElement
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
      .innerHTML = '<option value=""></option>' + this.formsList.getFiltered()
        .map((f: any) => `<option>${ f.url.split('/').pop() }</option>`)
        .join('');

    this.itemSettingsDialog
      .querySelector('#wf-item-settings-dialog__view')
      .innerHTML = '<option value=""></option>' + this.formsList.getViews()
        .map((f: any) => `<option>${ f.url.split('/').pop() }</option>`)
        .join('');

    if (item.type === WF_ITEM_TYPE.GOTO) {
      const nodesList = this.tree.getNodesList();
      this.itemSettingsDialog
        .querySelector('#wf-item-settings-dialog__node')
        .innerHTML = '<option value=""></option>' + 
          nodesList.filter((n: any) => item.id !== n.id && n.id > 1)
          .map((n: any) => 
            `<option value="${ n.id }:::${ n.title }">#${ n.id } ${ n.title }</option>`
          )
          .join('');
    }
    
    Array.from(this.itemSettingsDialog
      .querySelectorAll('[data-key]'))
      .forEach((input: HTMLInputElement) => {
        if (input.dataset.key !== 'goto' || !item.goto) {
          $(input).val(item[input.dataset.key] || '');
        }
        else {
          $(input).val(item.goto + ':::' + item.gotoLabel);
        }

        if ((input.dataset.key === 'form' && item.type === WF_ITEM_TYPE.FORM_TASK) 
          || (input.dataset.key === 'view' && item.type === WF_ITEM_TYPE.VIEW_TASK)
        ) {
          $('.wf-item-settings-dialog__create-btn')
            .css('visibility', Boolean(item[input.dataset.key]) ? 'hidden' : 'visible');
          $('.wf-item-settings-dialog__edit-btn')
            .css('visibility', Boolean(!item[input.dataset.key]) ? 'hidden' : 'visible');
          
          $(input).change((eventData) => {
            if ($(input).val()) {
              $('.wf-item-settings-dialog__create-btn').css('visibility', 'hidden');
              $('.wf-item-settings-dialog__edit-btn').css('visibility', 'visible');
            }
            else {
              $('.wf-item-settings-dialog__create-btn').css('visibility', 'visible');
              $('.wf-item-settings-dialog__edit-btn').css('visibility', 'hidden');
            }
          });
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
          if (!(new RegExp('processModal', 'g')).test(inputGroup.dataset.typefor)) {
            if (item.type === WF_ITEM_TYPE.PROCESS 
              && (new RegExp(item.type, 'g')).test(inputGroup.dataset.typefor)
              && !inputGroup.classList.contains('modal-title')
            ) {
              inputGroup.style.display = 'block';
            }
            else {
              inputGroup.style.display = 'none';
            }
          }
          else {
            inputGroup.style.display = 'block';
          }
        });
      this.loadFormMacro(item);
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
    this.tmpOnTopFormItem = (item.form || item.view) 
      ? item : (this.findWFFormItemOnTop(item.id) || null);
    if (!this.tmpOnTopFormItem 
      || !(this.tmpOnTopFormItem.form || this.tmpOnTopFormItem.view)) {
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

    const formURL = `${ this.getDBLink() }/${ 
      this.tmpOnTopFormItem.form || this.tmpOnTopFormItem.view }`;
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
          Implementation</label>${ htmlBuffer }`;
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
        if (!window['macrosSelectorRefreshEvent']) {
          window['macrosSelectorRefreshEvent'] = {};
        }
        $(window['macrosSelectorRefreshEvent'])
          .unbind('macros_selector_refresh')
          .bind('macros_selector_refresh', () => {
            $wd.find('input[type="radio"]').remove();
            $wd.find('.plomino-macros-rule').each((i, e) => {
              if (!item.macroText) {
                item.macroText = '';
              }
              const $macroValues = $(e).find('[data-macro-values]');
              const text = $macroValues.length 
                ? $macroValues.attr('data-macro-values')
                : $(e).find('.plomino_edit_macro')
                  .toArray().map((_e: HTMLElement) => _e.innerText).join(', ');
              const $r = $(`<input type="radio" name="macro-radio" 
                style="margin-right: 6pt;
                margin-left: 6pt; position: relative; top: 3pt; float: left;"
                ${ item.macroText === text ? 'checked' : '' }
                value="${ i + 1 }">`);
              // if (!item.macroText) {
              //   item.macroText = text;
              //   this.buildWFTree();
              // }
              // $r.click(() => {
              //   item.macroId = i + 1;
              //   item.macroText = text;
              //   this.buildWFTree();
              // });
              $(e).prepend($r);
              $(e).find('.select2-container').css('width', '95%');
            });
          });

        $(window['macrosSelectorRefreshEvent']).trigger('macros_selector_refresh');
      });
    });
  }

  onWFItemDblClicked($event: JQueryEventObject, $i: JQuery, item: PlominoWorkflowItem) {
    $event.stopImmediatePropagation();
    return this.onWFItemClicked($event, $i, item);
  }

  apply2selected() {
    const item = this.selectedItemRef;

    /* save process for form task or branch */
    const $e = $('li.plomino-macros-rule:visible:has(input[type="radio"]:checked)');

    if ($e.length) {
      const $macroValues = $e.find('[data-macro-values]');
      const text = $macroValues.length 
        ? $macroValues.attr('data-macro-values')
        : $e.find('.plomino_edit_macro')
          .toArray().map((_e: HTMLElement) => _e.innerText).join(', ');
      item.macroText = text;
    }

    Array.from(this.itemSettingsDialog
      .querySelectorAll('[data-key]'))
      .forEach((input: HTMLInputElement) => {
        if (item.hasOwnProperty(input.dataset.key)
          || (this.eventTypeIsTask(item.type) && input.dataset.key === 'title')
          || (this.eventTypeIsTask(item.type) && input.dataset.key === 'notes')
          || (this.eventTypeIsTask(item.type) && input.dataset.key === 'process')
          || (item.type === WF_ITEM_TYPE.PROCESS && input.dataset.key === 'process')
        ) {
          this.log.info('using', input.dataset.key, 'for', item.title, item.id);
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
    if (item.macroText && this.latestUsingForm.action) {
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
        .subscribe((data: Response) => {});
    }
  }

  findWFFormItemOnTop(itemId: number, tree = this.tree): false|PlominoWorkflowItem {
    const result = tree.searchParentItemOfItemByCondition(
      tree.getItemById(itemId), 
      (item: PlominoWorkflowItem): Boolean => 
        Boolean(item.form) || Boolean(item.view)
      );
    return result;
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
    this.tmpOnTopFormItem = (item.form || item.view) 
      ? item : (this.findWFFormItemOnTop(item.id) || null);

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
    $e.stopImmediatePropagation();

    const newLogicItem: PlominoWorkflowItem = {
      id: null,
      dropping: false,
      title: '',
      type: WF_ITEM_TYPE.PROCESS,
      children: []
    };

    this.tree.pushNewItemToParentById(newLogicItem, item.id);
    this.buildWFTree();
  }

  onItemDragStart(eventData: DragEvent, wfNode: HTMLElement, item: PlominoWorkflowItem) {
    this.dragService.followDNDType(DS_TYPE.EXISTING_WORKFLOW_ITEM);
    this.selectedItemRef = item;
    this.dragController.receive(
      eventData, 'start', DS_TYPE.EXISTING_WORKFLOW_ITEM, wfNode, item
    );
  }

  onItemDragEnd(eventData: DragEvent, wfNode: HTMLElement, item: PlominoWorkflowItem) {
    this.dragController.receive(
      eventData, 'end', DS_TYPE.EXISTING_WORKFLOW_ITEM, wfNode, item
    );
  }

  buildWFTree(tree = this.tree, autosave = true) {
    this.latestTree = tree;

    const wfTree: HTMLElement = this.workflowEditorNode.nativeElement;
    
    wfTree.innerHTML = '';
    $(wfTree).append(
      treeBuilder.getBuildedTree({
        workingTree: tree.getRawTree(), 
        onItemClick: this.onWFItemClicked.bind(this),
        onItemDblClick: this.onWFItemDblClicked.bind(this),
        onMacroClick: this.onWFItemMacroClicked.bind(this),
        onDragStart: this.onItemDragStart.bind(this),
        onDragEnd: this.onItemDragEnd.bind(this),
      })
    );

    componentHandler.upgradeDom();

    if (autosave) {
      const jsonTree = this.tree.toJSON();

      this.elementService.updateDBSettings({
        'description': jsonTree
      }).subscribe((response) => {});

      const dbLink = `${ 
        window.location.pathname
        .replace('++resource++Products.CMFPlomino/ide/', '')
        .replace('/index.html', '')
      }`;
  
      const fd = new FakeFormData(<any> $(`form[action*="${ dbLink }"]`).get(0));
      fd.set('form.widgets.IBasic.description', jsonTree);
    }

    return true;
  }
}

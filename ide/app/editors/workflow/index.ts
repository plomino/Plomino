import { PlominoWorkflowItemEditorService } from './workflow.item-editor.service';
import { WFDragControllerService, DS_TYPE, DS_FROM_PALETTE } from './drag-controller';
import { TreeStructure } from './tree-structure';
import { FakeFormData } from './../../utility/fd-helper/fd-helper';
import { Component, ElementRef, ViewChild, ViewEncapsulation } from '@angular/core';
import { PlominoBlockPreloaderComponent } from '../../utility';
import { DND_DIRECTIVES } from 'ng2-dnd';
import { treeBuilder, WF_ITEM_TYPE as WF } from './tree-builder';
import { PlominoWorkflowNodeSettingsComponent } from "../../palette-view";
import { PlominoWorkflowChangesNotifyService } from './workflow.changes.notify.service';
import { PlominoDBService, ElementService, LogService, 
  FormsService, DraggingService } from '../../services';

const NO_AUTOSAVE = false;
const AUTOSAVE = true;
const NO_AUTOUPGRADE = false;
const AUTOUPGRADE = true;

@Component({
  selector: 'plomino-workflow-editor',
  template: require('./workflow.component.html'),
  styles: [require('./workflow.component.sources.css')],
  directives: [DND_DIRECTIVES, PlominoBlockPreloaderComponent],
  providers: [PlominoWorkflowItemEditorService, WFDragControllerService],
  encapsulation: ViewEncapsulation.None,
})
export class PlominoWorkflowComponent {
  @ViewChild('workflowEditorNode') workflowEditorNode: ElementRef;
  tree: TreeStructure;
  latestTree: TreeStructure = null;
  editorOffset: { top: number, left: number };

  constructor(
    private log: LogService,
    private formsService: FormsService,
    private elementService: ElementService,
    private workflowChanges: PlominoWorkflowChangesNotifyService,
    private dragService: DraggingService,
    private dragController: WFDragControllerService,
    private itemEditor: PlominoWorkflowItemEditorService,
    private dbService: PlominoDBService,
  ) {
    if (!this.dragService.dndType) {
      this.dragService.followDNDType('nothing');
    }

    this.formsService.formRemoved$
      .subscribe((formId) => {
        const item = this.findWFItemByFormOrViewId(formId.split('/').pop());
        if (item !== null) {
          item[
            item.type === WF.FORM_TASK ? 'form' : 'view'
            ] = '';
          this.buildWFTree(this.tree, AUTOSAVE, AUTOUPGRADE);
        }
      });

    this.formsService.formIdChanged$
      .subscribe((data: { oldId: string, newId: string }) => {
        const item = this.findWFItemByFormOrViewId(data.oldId.split('/').pop());
        if (item !== null) {
          item[
            item.type === WF.FORM_TASK ? 'form' : 'view'
            ] = data.newId.split('/').pop();
          this.buildWFTree(this.tree, AUTOSAVE, AUTOUPGRADE);
        }
      });

    this.workflowChanges.needSave$
      .subscribe(() => {
        this.buildWFTree(this.tree, AUTOSAVE, AUTOUPGRADE);
      });

    this.workflowChanges.runAdd$
      .subscribe((wfType) => {
        let correctId = this.tree.getLatestId();
        const dragData = { title: '', type: wfType };
        let $item = $('.workflow-node[data-node-id="' + correctId +'"]');
        
        while (!$item.length || !this.isDragAllowed($item, wfType)) {
          if (correctId <= 1) { return; }
          correctId = correctId - 1;
          $item = $('.workflow-node[data-node-id="' + correctId +'"]');
        }

        this.dragService.followDNDType('wf-menu-dnd-callback');
        this.dragInsertPreview(
          $('.workflow-node[data-node-id="' + correctId +'"]'), dragData);
        this.onDrop();
      });
  }

  ngOnInit() {
    let tree;

    try {
      const dbLink = this.dbService.getDBLink();
      const fd = new FakeFormData(<any> $(`form[action*="${ dbLink }/@@edit"]`).get(0));
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
    this.buildWFTree(this.tree, NO_AUTOSAVE, NO_AUTOUPGRADE);
    this.itemEditor.registerTree(this.tree);

    this.editorOffset = $(this.workflowEditorNode.nativeElement).offset();
    this.dragController.registerWorkflowOffset(this.editorOffset);
    this.dragController.rebuildWorkflow$.subscribe(() => {
      this.buildWFTree(this.tree, NO_AUTOSAVE, AUTOUPGRADE);
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

  deleteWFItem(wfNode: HTMLElement, targetItem: PlominoWorkflowItem) {
    if (targetItem.type === WF.CONDITION || targetItem.type === WF.PROCESS) {
      /* if 1 branch -> assume to remove only it, not whole */
      const aloneBranch = targetItem.type === WF.PROCESS
        && this.tree.getItemParentById(targetItem.id).children.length === 1;
      const aloneCondition = targetItem.type === WF.CONDITION
        && targetItem.children.length === 1;
      if (aloneBranch || aloneCondition) {
        this.elementService.awaitForConfirm('One branch. Remove just division?')
        .then(() => {
          const idParent = this.tree.getItemParentById(targetItem.id).id;
          const idChildren = targetItem.children[0].id;
          const idItem = targetItem.id;
          this.tree.deleteNodeById(aloneBranch ? idParent : idChildren);
          this.tree.deleteNodeById(idItem);
          this.buildWFTree(this.tree, AUTOSAVE, AUTOUPGRADE);
        })
        .catch(() => {
          this.elementService.awaitForConfirm(
            targetItem.type === WF.CONDITION 
              ? 'This action will remove the branches below'
              : 'This action will remove the branch below')
          .then(() => {
            this.tree.deleteBranchByTopItemId(targetItem.id);
            this.buildWFTree(this.tree, AUTOSAVE, AUTOUPGRADE);
          })
          .catch(() => {});
        });
      }
      else {
        /* else */
        this.elementService.awaitForConfirm(
          targetItem.type === WF.CONDITION 
            ? 'This action will remove the branches below'
            : 'This action will remove the branch below')
        .then(() => {
          this.tree.deleteBranchByTopItemId(targetItem.id);
          this.buildWFTree(this.tree, AUTOSAVE, AUTOUPGRADE);
        })
        .catch(() => {});
      }
    }
    else {
      this.tree.deleteNodeById(targetItem.id);
      const $wfItemClosest = $(wfNode);
      $wfItemClosest.fadeOut(100, () => 
        this.buildWFTree(this.tree, AUTOSAVE, AUTOUPGRADE));
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
    const nodeId = +$parentItem.attr('data-node-id') || 1;
    let parentItem = sandboxTree.getItemById(nodeId);

    if (!parentItem) {
      return;
    }

    if (this.dragService.dndType !== DS_TYPE.EXISTING_WORKFLOW_ITEM) {
      
      if ([WF.FORM_TASK, WF.VIEW_TASK, WF.EXT_TASK].indexOf(dragData.type) !== -1) {
        previewItem.title = '';
  
        if (dragData.type === WF.FORM_TASK) {
          previewItem.form = '';
        }
        else if (dragData.type === WF.VIEW_TASK) {
          previewItem.view = '';
        }
      }
      else if (dragData.type === WF.PROCESS) {
        previewItem.title = '';
      }
      else if (dragData.type === WF.GOTO) {
        previewItem.goto = '';
      }
      else if (dragData.type === WF.CONDITION) {

        if (parentItem.type === WF.CONDITION) {
          previewItem.type = WF.PROCESS;
          previewItem.title = '';
        }
        else {
          previewItem.condition = '';
    
          const truePreviewItem: PlominoWorkflowItem = {
            id: -2,
            title: '',
            dropping: true,
            type: WF.PROCESS,
            children: []
          };
    
          const falsePreviewItem: PlominoWorkflowItem = {
            id: -3,
            title: '',
            dropping: true,
            type: WF.PROCESS,
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
        previewItem[previewItem.type === WF.FORM_TASK 
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
      
      this.buildWFTree(sandboxTree, NO_AUTOSAVE, NO_AUTOUPGRADE);
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

  /**
   * Is the eventType is PROCESS or CONDITION
   * @param eventType 
   */
  eTypeIsProcCond(eventType: string) {
    return [
      WF.PROCESS, WF.CONDITION
    ].indexOf(eventType) !== -1;
  }

  isDragAllowed($wfItemClosest: JQuery, dType: string): Boolean {
    let allowedDrag = true;
    const closestExists = Boolean($wfItemClosest.length);
    const onGoto = closestExists && $wfItemClosest.hasClass('workflow-node--goto');
    const onCond = closestExists && $wfItemClosest.hasClass('workflow-node--condition');
    const onBranch = closestExists && $wfItemClosest.hasClass('workflow-node--process');
    const onRoot = closestExists && $wfItemClosest.hasClass('workflow-node--root');
    const isProcOrCondDrag = this.eTypeIsProcCond(dType);
    const isBranchDrag = dType === WF.CONDITION;
    const isGotoDrag = dType === WF.GOTO;
    const lvl = closestExists ? +$wfItemClosest.attr('data-node-level') : 0;

    if ((onCond && !isBranchDrag) || onGoto 
      || (onRoot && (isProcOrCondDrag || isGotoDrag))
    ) {
      allowedDrag = false;
    }

    if (allowedDrag && isGotoDrag) {
      allowedDrag = !Boolean($('[data-node-level="' + (lvl + 1) + '"]').length);
    }

    return allowedDrag;
  }

  isSwapAllowed(itemA: PlominoWorkflowItem, itemB: PlominoWorkflowItem): Boolean {
    const isBranch = (item: PlominoWorkflowItem) => 
      item.type === WF.PROCESS;
    const isCondition = (item: PlominoWorkflowItem) => 
      item.type === WF.CONDITION;
    const isGoto = (item: PlominoWorkflowItem) => 
      item.type === WF.GOTO;
    const isLowestElementInBranch = (item: PlominoWorkflowItem) => 
      !item.children.length;

    const bothItems = (query: (item: PlominoWorkflowItem) => Boolean) => 
      query(itemA) && query(itemB);
    const oneOfItems = (query: (item: PlominoWorkflowItem) => Boolean) => 
      query(itemA) || query(itemB);
    
    if (bothItems(isBranch)) {
      return true;
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
    else if (isBranch(itemA)) {
      return false;
    }
    else if (isBranch(itemB)) {
      return true;
    }

    return true;
  }

  onDrop(data: ReceiverEvent = null) {
    if (data && data.dragServiceType === DS_TYPE.EXISTING_WORKFLOW_ITEM) {
      /* swap items */
      if (this.isSwapAllowed(this.itemEditor.getSelectedItem(), data.item)) {
        if (data.item.type === WF.PROCESS) {
          this.tree.moveNodeToAnotherParentById(
            this.itemEditor.getSelectedItem().id, data.item.id);
        }
        else {
          this.tree.swapNodesByIds(
            this.itemEditor.getSelectedItem().id, data.item.id);
        }

        this.buildWFTree(this.tree, AUTOSAVE, AUTOUPGRADE);
      }
      else {
        this.buildWFTree(this.tree, AUTOSAVE, AUTOUPGRADE);
      }
    }
    else {
      const sandboxTree = this.latestTree;
      const temporaryItem = sandboxTree.getItemById(-1);
  
      if (temporaryItem) {
        sandboxTree.makeItemReal(temporaryItem);
    
        if (temporaryItem.type === WF.CONDITION) {
          const temporaryTrueProcessItem = sandboxTree.getItemById(-2);
          sandboxTree.makeItemReal(temporaryTrueProcessItem);
    
          const temporaryFalseProcessItem = sandboxTree.getItemById(-3);
          sandboxTree.makeItemReal(temporaryFalseProcessItem);
        }
    
        this.tree = sandboxTree;
        this.itemEditor.registerTree(this.tree);
        this.buildWFTree(this.tree, AUTOSAVE, AUTOUPGRADE);
      }
    }
  }

  onItemDragLeave(data: ReceiverEvent) {
    if (data.dragServiceType !== DS_TYPE.EXISTING_WORKFLOW_ITEM) {
      this.buildWFTree(this.tree, NO_AUTOSAVE, AUTOUPGRADE);
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
            ? WF.VIEW_TASK : WF.FORM_TASK) : data.dragServiceType
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

  onClickReceive(clickEvent: MouseEvent) {
    this.log.info(clickEvent.target);
    clickEvent.stopPropagation();
    
    const eventTarget = <HTMLElement> clickEvent.target;
    let $tmp = $(eventTarget).closest('.workflow-node');
    
    let wfNode = $tmp.length ? $tmp.get(0) 
      : ($(eventTarget).hasClass('workflow-node') ? eventTarget : null);

    if (wfNode === null) {
      $tmp = $(eventTarget)
        .closest('.plomino-workflow-editor__branch')
        .find('.workflow-node');
      if ($tmp.length) {
        wfNode = $tmp.get(0);
      }
      else {
        return false;
      }
    }
    
    const isDelBtn = treeBuilder.checkTarget(eventTarget, 'workflow-node__bubble-delete');
    const isAddBelow = treeBuilder.checkTarget(eventTarget, 
      'plomino-workflow-editor__branch-add-below-bubble-btn');
    
    const isCreate = eventTarget.dataset.create;

    const isVirtual = wfNode.classList.contains('workflow-node--virtual');
    const isRoot = wfNode.classList.contains('workflow-node--root');
    const item = this.tree.getItemById(+wfNode.dataset.nodeId);

    if (!item && !isCreate) { return true; }

    if (isCreate) {
      const $wfItemClosest = $(wfNode.parentElement.firstElementChild);
      this.dragService.followDNDType('wf-menu-dnd-callback');
      this.dragInsertPreview($wfItemClosest, { title: '', type: isCreate });
      return this.onDrop();
    }

    if (!isRoot && !item.selected && !isDelBtn && !isCreate && !isVirtual && !isAddBelow) {
      this.unselectAllWFItems();
      item.selected = true;
      this.itemEditor.setSelectedItem(item);
      wfNode.classList.add('workflow-node--selected');
    }

    if (!isRoot && isDelBtn) {
      return this.deleteWFItem(wfNode, item);
    }
    else if (!isRoot && wfNode.classList.contains('workflow-node--condition')) {
      const newLogicItem: PlominoWorkflowItem = {
        id: null,
        dropping: false,
        title: '',
        type: WF.PROCESS,
        children: []
      };
  
      this.tree.pushNewItemToParentById(newLogicItem, item.id);
      return this.buildWFTree(this.tree, AUTOSAVE, AUTOUPGRADE);
    }
    else if (!isRoot && eventTarget.classList.contains('workflow-node__text-modal-link')) {
      if (eventTarget.parentElement.classList.contains('workflow-node__text--form')
        || eventTarget.parentElement.classList.contains('workflow-node__text--view')
      ) {
        this.itemEditor.openResourceTab(item);
      }
      else if (item.type === WF.PROCESS 
        || eventTarget.parentElement.classList.contains('workflow-node__text--process')
      ) {
        /* process modal */
        this.itemEditor.showModal(item, true);
      }
      else {
        /* just modal */
        this.itemEditor.showModal(item);
      }
    }
    else if (item && item.type === WF.GOTO && item.goto) {
      $('.workflow-node[data-node-id="' + item.goto +'"]').get(0).scrollIntoView(false);
    }

    return true;
  }

  onWFItemMacroClicked($e: JQueryEventObject, $i: JQuery, item: PlominoWorkflowItem) {
    this.log.info('onWFItemMacroClicked', $e, item);
    $e.stopImmediatePropagation();
    $e.preventDefault();

    this.itemEditor.editMacro(item);
    return false;
  }

  onItemDragStart(eventData: DragEvent, wfNode: HTMLElement, item: PlominoWorkflowItem) {
    this.dragService.followDNDType(DS_TYPE.EXISTING_WORKFLOW_ITEM);
    this.itemEditor.setSelectedItem(item);
    this.dragController.receive(
      eventData, 'start', DS_TYPE.EXISTING_WORKFLOW_ITEM, wfNode, item
    );
  }

  onItemDragEnd(eventData: DragEvent, wfNode: HTMLElement, item: PlominoWorkflowItem) {
    this.dragController.receive(
      eventData, 'end', DS_TYPE.EXISTING_WORKFLOW_ITEM, wfNode, item
    );
  }

  buildWFTree(tree = this.tree, autosave = AUTOSAVE, upgrade = NO_AUTOUPGRADE) {
    this.latestTree = tree;
    const wfTree: HTMLElement = this.workflowEditorNode.nativeElement;
    wfTree.innerHTML = treeBuilder.getBuildedTree(tree.getRawTree());
    const $wfTree: JQuery = $(wfTree);

    $wfTree.find('.workflow-node').each((i, wfNode: HTMLElement) => {
      const item = tree.getItemById(+wfNode.dataset.nodeId);

      if (!item || item.root) { return true; }
      if (item.type !== WF.CONDITION) {
        wfNode.ondragstart = (eventData: DragEvent) => {
          eventData.dataTransfer.setData('text', 'q:' + item.id.toString());
          return this.onItemDragStart(eventData, wfNode, item);
        };
      }

      wfNode.ondragend = (eventData: DragEvent) => {
        return this.onItemDragEnd(eventData, wfNode, item);
      };

      wfNode.ondragover = (eventData: DragEvent) => {
        eventData.preventDefault();
        eventData.stopImmediatePropagation();
      };
    });

    if (upgrade) {
      setTimeout(() => componentHandler.upgradeElements(wfTree), 200);
    }

    if (autosave) {
      const jsonTree = this.tree.toJSON();

      this.elementService.updateDBSettings({
        'description': jsonTree
      }).subscribe((response) => {});

      const dbLink = this.dbService.getDBLink();
  
      const fd = new FakeFormData(<any> $(`form[action*="${ dbLink }/@@edit"]`).get(0));
      fd.set('form.widgets.IBasic.description', jsonTree);
    }

    return true;
  }
}

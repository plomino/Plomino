import { WF_ITEM_TYPE } from './tree-builder';
export class TreeStructure {
  private latestIdNumber: number;
  private tree: PlominoWorkflowItem;
  private indexOfNodes: Array<PlominoNodeIndexKey>;
  private mapOfIndex: Map<number, { indx: PlominoNodeIndexKey; i: number }>;

  constructor(tree: PlominoWorkflowItem = null) {
    this.tree = tree ? tree : this.getEmptyTree();
    this.rebuildIndex();
  }

  public getRawTree(): PlominoWorkflowItem {
    return this.tree;
  }

  public getLatestId(): number {
    return this.latestIdNumber;
  }

  public getCountOfNodes(): number {
    return this.indexOfNodes.length;
  }

  public createSandbox(): TreeStructure {
    return new TreeStructure(jQuery.extend(true, {}, this.tree));
  }

  public isEmptySpace(): boolean {
    return !(this.tree && this.tree.children.length);
  }

  public makeItemReal(item: PlominoWorkflowItem) {
    if (item && item.id && this.mapOfIndex.has(item.id)) {
      const tmpId = item.id;
      item.id = this.latestIdNumber + 1;
      this.latestIdNumber = item.id;
      item.dropping = false;
      const tmpIndex = this.mapOfIndex.get(tmpId);
      tmpIndex.indx.id = item.id;
      this.mapOfIndex.set(item.id, tmpIndex);
      this.mapOfIndex.delete(tmpId);
    }
  }

  public pushNewItemToParentById(item: PlominoWorkflowItem, parentItemId: number): boolean {
    if (this.mapOfIndex.has(parentItemId)) {
      const parentNodeIndex = this.mapOfIndex.get(parentItemId);

      if (!item.id) {
        item.id = this.latestIdNumber + 1;
        this.latestIdNumber = item.id;
      }

      const parentItem = parentNodeIndex.indx.item;

      if (parentItem.type === WF_ITEM_TYPE.CONDITION || !parentItem.children.length) {
        parentItem.children.push(item);
  
        this.indexOfNodes.push({
          id: item.id, item, 
          parent: parentItem,
          parentIndex: parentItem.children.length - 1
        });

        const i = this.indexOfNodes.length - 1;
        this.mapOfIndex.set(item.id, { indx: this.indexOfNodes[i], i });
  
        if (item.children.length > 0) {
          for (let parentIndex = 0; parentIndex < item.children.length; parentIndex++) {
            this.indexOfNodes.push({
              id: item.children[parentIndex].id, item: item.children[parentIndex], 
              parent: item,
              parentIndex
            });
  
            const i = this.indexOfNodes.length - 1;
            this.mapOfIndex.set(
              item.children[parentIndex].id, { indx: this.indexOfNodes[i], i }
            );
          }
        }
      }
      else if (item.type === WF_ITEM_TYPE.CONDITION && parentItem.children.length) {
        /* hardcode */
        const itemBelow = parentItem.children[0];

        const belowIndex = this.mapOfIndex.get(itemBelow.id);
        belowIndex.indx.parent = item.children[0];
        belowIndex.indx.parentIndex = 0;

        item.children[0].children = [itemBelow]; // clear children
        parentItem.children = [item];

        this.indexOfNodes.push({
          id: item.id, item, parent: parentItem, 
          parentIndex: parentItem.children.length - 1
        });

        const i = this.indexOfNodes.length - 1;
        this.mapOfIndex.set(item.id, { indx: this.indexOfNodes[i], i });

        this.indexOfNodes.push({
          id: item.children[0].id, item: item.children[0], parent: item, parentIndex: 0
        });

        this.mapOfIndex.set(
          item.children[0].id, { indx: this.indexOfNodes[i + 1], i: i + 1 });

        this.indexOfNodes.push({
          id: item.children[1].id, item: item.children[1], parent: item, parentIndex: 1
        });

        this.mapOfIndex.set(
          item.children[1].id, { indx: this.indexOfNodes[i + 2], i: i + 2 });
      }
      else {
        /* find first children of this item and make it as our item children */
        const itemBelow = parentItem.children[0];

        const belowIndex = this.mapOfIndex.get(itemBelow.id);
        belowIndex.indx.parent = item;
        belowIndex.indx.parentIndex = 0;

        item.children = [itemBelow]; // clear children
        parentItem.children = [item];

        this.indexOfNodes.push({
          id: item.id, item, 
          parent: parentItem,
          parentIndex: parentItem.children.length - 1
        });

        const i = this.indexOfNodes.length - 1;
        this.mapOfIndex.set(item.id, { indx: this.indexOfNodes[i], i });
      }

      return true;
    }

    return false;
  }

  public getItemById(id: number): PlominoWorkflowItem|null {
    return this.mapOfIndex.has(id) 
      ? this.mapOfIndex.get(id).indx.item : null;
  }

  public getItemParentById(id: number): PlominoWorkflowItem|null {
    return this.mapOfIndex.has(id) 
      ? this.mapOfIndex.get(id).indx.parent : null;
  }

  public searchParentItemOfItemByCondition(
    item: PlominoWorkflowItem,
    condition: (currentItem: PlominoWorkflowItem) => boolean
  ): PlominoWorkflowItem|false {
    let currentItem = item;
    while (this.mapOfIndex.get(currentItem.id).indx.parent.id !== 1) {
      currentItem = this.mapOfIndex.get(currentItem.id).indx.parent;
      if (condition(currentItem)) {
        return currentItem;
      }
    }
    return false;
  }

  public deleteNodeById(id: number): boolean {
    if (this.mapOfIndex.has(id)) {
      /* 1. get index writing */
      const x = this.mapOfIndex.get(id);
      if (x.indx.item.children.length > 1) {
        return false;
      }
      if (x.indx.item.children.length) {
        /* 2. delete parent[parentIndex] BUT not its children */
        const exportedChild = x.indx.item.children[0]; // $.EXTEND?
        // x.indx.parent.children.splice(x.indx.parentIndex, 1);
        x.indx.parent.children[x.indx.parentIndex] = exportedChild;
        const y = this.mapOfIndex.get(exportedChild.id);
        y.indx.parent = x.indx.parent;
        y.indx.parentIndex = x.indx.parentIndex;
      }
      else if (x.indx.parent.children.length === 1) {
        x.indx.parent.children.splice(0, 1);
      }
      else {
        x.indx.parent.children.splice(x.indx.parentIndex, 1);
      }
      /* 3. delete mapOfIndex relation to writing */
      this.mapOfIndex.delete(id);
      /* 4. delete index writing */
      this.indexOfNodes.splice(x.i, 1);
      return true;
    }
    return false;
  }

  public deleteBranchByTopItemId(id: number): boolean {
    if (this.mapOfIndex.has(id)) {
      const x = this.mapOfIndex.get(id);
      if (x.indx.parent.children.length === 1) {
        x.indx.parent.children = [];
        this.mapOfIndex.delete(id);
        this.indexOfNodes.splice(x.i, 1);
      }
      else {
        x.indx.parent.children.splice(x.indx.parentIndex, 1);
        this.rebuildIndex();
      }

      /* can be realised with collection of deleting nodes: */
        /* delete mapOfIndex relation to writing */
        // this.mapOfIndex.delete(id);
        /* delete index writing */
        // this.indexOfNodes.splice(x.i, 1);

      return true;
    }
    return false;
  }

  public moveNodeToAnotherParentById(itemId: number, newParentId: number): boolean {
    if (this.mapOfIndex.has(itemId) && this.mapOfIndex.has(newParentId)) {
      const itemCopy = $.extend({}, this.getItemById(itemId));
      itemCopy.children = [];
      this.deleteNodeById(itemId);
      return this.pushNewItemToParentById(itemCopy, newParentId);
    }

    return false;
  }

  public swapNodesByIds(idA: number, idB: number): boolean {
    if (this.mapOfIndex.has(idA) && this.mapOfIndex.has(idB)) {
      const a = this.mapOfIndex.get(idA);
      const b = this.mapOfIndex.get(idB);

      /* 1. export item A without it's children to variable */
      const exportedA = $.extend({}, a.indx.item);
      exportedA.children = [];

      /* 2. export item B without is's children to variable */
      const exportedB = $.extend({}, b.indx.item);
      exportedB.children = [];

      /* 3. to variable of item A set children of item B */
      exportedA.children = b.indx.item.children;

      /* 4. to variable of item B set children of item A */
      exportedB.children = a.indx.item.children;

      /* 5. place variable of item A to item B's place */
      b.indx.parent.children[b.indx.parentIndex] = exportedA;

      /* 6. place variable of item B to item A's place */
      a.indx.parent.children[a.indx.parentIndex] = exportedB;

      /* 7. updt index: update item A parent and item B parent */
      const indxUpdateA = {
        id: exportedB.id,
        item: exportedB,
        parent: a.indx.parent,
        parentIndex: a.indx.parentIndex,
      };

      const indxUpdateB = {
        id: exportedA.id,
        item: exportedA,
        parent: b.indx.parent,
        parentIndex: b.indx.parentIndex,
      };

      this.indexOfNodes[a.i] = indxUpdateA;
      this.indexOfNodes[b.i] = indxUpdateB;

      this.mapOfIndex.set(indxUpdateA.id, { indx: indxUpdateA, i: a.i });
      this.mapOfIndex.set(indxUpdateB.id, { indx: indxUpdateB, i: b.i });

      return true;
    }
    return false;
  }

  public iterate(calllbc: (item: PlominoWorkflowItem, 
    parent: PlominoWorkflowItem, indexInParentChildren: number) => any
  ) {
    for (const e of this.indexOfNodes) {
      calllbc(e.item, e.parent, e.parentIndex);
    }
  }

  public getNodesList() {
    return this.indexOfNodes.map((node) => node.item);
  }

  public walk( 
    calllbc: (
      item: PlominoWorkflowItem, 
      parent: PlominoWorkflowItem, 
      indexInParentChildren: number) => void,
    tree: PlominoWorkflowItem = this.tree,
    parent: PlominoWorkflowItem = null,
    parentIndex = 0,
  ) {
    let result = calllbc(tree, parent, parentIndex);
    for (let i = 0; i < tree.children.length; i++) {
      result = this.walk(calllbc, tree.children[i], tree, i);
    }
  }

  public toJSON() {
    return JSON.stringify(this.tree)
      .replace(/,"(selected|dropping)":(false|true)/g, '');
  }

  private getEmptyTree(): PlominoWorkflowItem {
    return { id: 1, root: true, children: [] };
  }

  private rebuildIndex() {
    this.indexOfNodes = [];
    this.mapOfIndex = new Map();
    this.latestIdNumber = 1;
    this.walk((item, parent, parentIndex) => {
      if (item.id > this.latestIdNumber) {
        this.latestIdNumber = item.id;
      }

      this.indexOfNodes.push({
        id: item.id, item, parent, parentIndex
      });

      const i = this.indexOfNodes.length - 1;
      this.mapOfIndex.set(item.id, { indx: this.indexOfNodes[i], i });
    });
  }
}

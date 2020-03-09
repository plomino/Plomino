import { TreeStructure } from "./tree-structure";
import { Injectable } from "@angular/core";

@Injectable()
export class PlominoWorkflowTreeService {
    activeTree: TreeStructure = null;

    constructor() {}

    setActiveTree(tree: TreeStructure) {
        this.activeTree = tree;
    }

    getActiveTree() {
        return this.activeTree;
    }
}

export const treeBuilder = {
  getBuildedTree(
    tree: PlominoWorkflowItem, 
    onItemClick: (
      $event: JQueryEventObject, $item: JQuery, item: PlominoWorkflowItem
    ) => any
  ): JQuery {
    const workWithItemRecursive = (item: PlominoWorkflowItem): JQuery => {
      const $item: JQuery = this.parseWFItem(item);
      if (item.children.length) {
        const $childrenTree = $(`<ul class="plomino-workflow-editor__branches"></ul>`);
        for (let child of item.children) {
          $childrenTree.append(workWithItemRecursive(child));
        }
        $item.append($childrenTree);
      }

      $item.click(($event) => onItemClick($event, $item, item));
      return $item;
    };

    const $root = $(`<ul class="plomino-workflow-editor__branches"></ul>`);
    $root.append(workWithItemRecursive(tree));
    return $root;
  },

  /**
   * parse PlominoWorkflowItem and convert it to jQuery Object
   * @param {PlominoWorkflowItem} item PlominoWorkflowItem
   */
  parseWFItem(item: PlominoWorkflowItem): JQuery {
    return $(
      `<li class="plomino-workflow-editor__branch">
          <div class="workflow-node${
              item.root ? ' workflow-node--root' : ''
            }${ item.dropping ? ' workflow-node--dropping' : '' }"
            ${ item.id ? ` data-node-id="${ item.id }"` : '' }>
              <div class="workflow-node__inner"><!--
                -->${ item.task ? 
                  `<div class="workflow-node__task">
                      Task: ${ item.task }
                  </div>` : ''
                }<!--
                -->${ item.form ? 
                  `<div class="workflow-node__form">
                      Form: ${ item.form }
                  </div>` : ''
                }<!--
                -->${ item.process ? 
                  `<div class="workflow-node__process">
                      Process: ${ item.process }
                  </div>` : ''
                }<!--
                -->${ item.condition ? 
                  `<div class="workflow-node__condition">
                      Condition: ${ item.condition }
                  </div>` : ''
                }<!--
                -->${ item.user ? 
                  `<div class="workflow-node__user">
                      User: ${ item.user }
                  </div>` : ''
                }<!--
                -->${ item.goto ? 
                  `<div class="workflow-node__goto">
                      Goto: ${ item.goto }
                  </div>` : ''
                }<!--
              --></div>
          </div>
      </li>`);
  }
};

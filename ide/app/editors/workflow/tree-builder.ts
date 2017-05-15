export const WF_ITEM_TYPE = {
  FORM_TASK: 'workflowFormTask',
  VIEW_TASK: 'workflowViewTask',
  EXT_TASK: 'workflowExternalTask',
  PROCESS: 'workflowProcess',
  CONDITION: 'workflowCondition',
  GOTO: 'workflowGoto',
};

export const treeBuilder = {
  getBuildedTree(
    configuration: {
      workingTree: PlominoWorkflowItem, 
      onItemClick: (
        $event: JQueryEventObject, $item: JQuery, item: PlominoWorkflowItem
      ) => any,
      onItemDblClick: (
        $event: JQueryEventObject, $item: JQuery, item: PlominoWorkflowItem
      ) => any,
      onMacroClick?: (
        $event: JQueryEventObject, $item: JQuery, item: PlominoWorkflowItem
      ) => any,
    }
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

      if (!item.root) {
        $item.find('.workflow-node__text--macro a')
          .click(($event) => configuration.onMacroClick($event, $item, item));
        $item.click(($event) => configuration.onItemClick($event, $item, item));
        $item.dblclick(($event) => configuration.onItemDblClick($event, $item, item));
      }

      return $item;
    };

    const $root = $(
      `<ul class="plomino-workflow-editor__branches
        plomino-workflow-editor__branches--root"></ul>`
    );
    $root.append(workWithItemRecursive(configuration.workingTree));
    return $root;
  },

  eventTypeIsTask(eventType: string) {
    return [
      WF_ITEM_TYPE.FORM_TASK, WF_ITEM_TYPE.VIEW_TASK, WF_ITEM_TYPE.EXT_TASK
    ].indexOf(eventType) !== -1;
  },

  /**
   * parse PlominoWorkflowItem and convert it to jQuery Object
   * @param {PlominoWorkflowItem} item PlominoWorkflowItem
   */
  parseWFItem(item: PlominoWorkflowItem): JQuery {
    return $(
      `<li class="plomino-workflow-editor__branch"><!--${
           item.type === WF_ITEM_TYPE.CONDITION 
           ? `--><button class="plomino-workflow-editor__branch-plus-btn
             mdl-button mdl-js-button 
             mdl-button--fab mdl-button--mini-fab">
              <i class="material-icons">add</i>
            </button><!--` : ''
          }--><div class="workflow-node
            ${ item.root ? ' workflow-node--root' : ''}
            ${ item.dropping ? ' workflow-node--dropping' : '' }
            ${ item.type === WF_ITEM_TYPE.CONDITION ? 
              ' workflow-node--as-a-shape workflow-node--condition' : '' }
            ${ item.type === WF_ITEM_TYPE.GOTO ? 
              ' workflow-node--as-a-shape workflow-node--goto' : '' }
            ${ this.eventTypeIsTask(item.type) ? 
              ' workflow-node--as-a-shape workflow-node--task' : '' }"
            ${ item.id ? ` data-node-id="${ item.id }"` : '' }>
              <div class="workflow-node__inner"><!--
                --><div class="workflow-node__shape-outside"><!--
                --><div class="workflow-node__shape-inside"></div><!--
                --></div><!--
                -->${ this.eventTypeIsTask(item.type) ? 
                  `<div class="workflow-node__text workflow-node__text--task">
                      Task: ${ item.title }
                  </div>` : ''
                }<!--
                -->${ item.form ? 
                  `<div class="workflow-node__text workflow-node__text--form">
                      Form: ${ item.form }
                  </div>` : ''
                }<!--
                -->${ item.view ? 
                  `<div class="workflow-node__text workflow-node__text--view">
                      View: ${ item.view }
                  </div>` : ''
                }<!--
                -->${ item.type === WF_ITEM_TYPE.PROCESS ? 
                  `<div class="workflow-node__text workflow-node__text--process">
                      Process: ${ item.title }
                  </div>` : ''
                }<!--
                -->${ item.type === WF_ITEM_TYPE.PROCESS ? 
                  `<div class="workflow-node__text workflow-node__text--macro">
                      Macro: <a href onclick="return false">edit macros</a>
                  </div>` : ''
                }<!--
                -->${ item.type === WF_ITEM_TYPE.CONDITION ? 
                  `<div class="workflow-node__text workflow-node__text--condition">
                      ${ item.condition || '&nbsp;' }
                  </div>` : ''
                }<!--
                -->${ item.user ? 
                  `<div class="workflow-node__text workflow-node__text--user">
                      User: ${ item.user }
                  </div>` : ''
                }<!--
                -->${ item.goto ? 
                  `<div class="workflow-node__text workflow-node__text--goto">
                      Goto: ${ item.goto }
                  </div>` : ''
                }<!--
              --></div><!--
          --></div>
      </li>`);
  }
};

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
      onMacroClick: (
        $event: JQueryEventObject, $item: JQuery, item: PlominoWorkflowItem
      ) => any,
      onDragStart: (
        eventData: DragEvent, $item: JQuery, item: PlominoWorkflowItem
      ) => true,
      onDragEnter: (
        eventData: DragEvent, $item: JQuery, item: PlominoWorkflowItem
      ) => true,
      onDragLeave: (
        eventData: DragEvent, $item: JQuery, item: PlominoWorkflowItem
      ) => true,
      onDragEnd: (
        eventData: DragEvent, $item: JQuery, item: PlominoWorkflowItem
      ) => true,
      onDrop: (
        eventData: DragEvent, $item: JQuery, item: PlominoWorkflowItem
      ) => true,
    }
  ): JQuery {
    let level = 1;
    const workWithItemRecursive = (
        item: PlominoWorkflowItem, parent: PlominoWorkflowItem = null
    ): JQuery => {
      const $item: JQuery = this.parseWFItem(item, parent, level++);
      
      if (item.children.length) {
        const $childrenTree = $(`<ul class="plomino-workflow-editor__branches"></ul>`);
        for (let child of item.children) {
          $childrenTree.append(workWithItemRecursive(child, item));
          level--;
        }
        $item.append($childrenTree);
      }

      $item.click(($event) => configuration.onItemClick($event, $item, item));

      if (!item.root) {
        $item.find('.workflow-node__text--macro a')
          .click(($event) => configuration.onMacroClick($event, $item, item));
        
        $item.dblclick(($event) => configuration.onItemDblClick($event, $item, item));

        $item.find('.workflow-node__text-modal-link')
          .click(($event) => configuration.onItemDblClick($event, $item, item));

        $item[0].ondragstart = (eventData: DragEvent) => {
          eventData.dataTransfer.setData('text', 'q:' + item.id.toString());
          return configuration.onDragStart(eventData, $item, item);
        };

        $item[0].ondragend = (eventData: DragEvent) => {
          return configuration.onDragEnd(eventData, $item, item);
        };

        $item[0].ondrop = (eventData: DragEvent) => {
          // console.log('drop', eventData.dataTransfer.getData('text'));
          return configuration.onDrop(eventData, $item, item);
        }

        $item[0].ondragenter = (eventData: DragEvent) => {
          // console.log('dragenter', eventData.dataTransfer.getData('text'));
          return configuration.onDragEnter(eventData, $item, item);
        }

        $item[0].ondragleave = (eventData: DragEvent) => {
          // console.log('dragleave', eventData.dataTransfer.getData('text'));
          return configuration.onDragLeave(eventData, $item, item);
        }

        $item.on('dragover', ($event) => {
          $event.preventDefault();
        });
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

  nodeIsLast(node: PlominoWorkflowItem) {
    return !node.children.length;
  },

  /**
   * parse PlominoWorkflowItem and convert it to jQuery Object
   * @param {PlominoWorkflowItem} item PlominoWorkflowItem
   * @param {PlominoWorkflowItem} parent PlominoWorkflowItem
   * @param {number} level
   */
  parseWFItem(
    item: PlominoWorkflowItem, parent: PlominoWorkflowItem = null, level = 0
  ): JQuery {

    const allowedLength = 18;
    const allowedLengthWide = 128;

    const cutString = ((str: string, l = allowedLength) => {
      if (str && str.length > l) {
        str = str.substr(0, l) + '...';
      }
      return str || '';
    });

    const autoBR = (result: string) => {
      if (!result) { return ''; }
      return result.match(/(.\s?){1,22}/g).join('<br>');
    }

    const $buildJQItem = (spec: string = null) => {
      const hashId = item.id !== -1 ? '#' + item.id : '';
      return $(
      `${ !spec ? `<li class="plomino-workflow-editor__branch" 
           ${ !item.root ? ' draggable="true"' : ''}>` : '' }<!--
           --><div class="workflow-node
            ${ item.root ? ' workflow-node--root' : ''}
            ${ item.dropping ? ' workflow-node--dropping' : '' }
            ${ item.type === WF_ITEM_TYPE.PROCESS ? ' workflow-node--branch' : '' }
            ${ item.type === WF_ITEM_TYPE.CONDITION ? 
              ' workflow-node--as-a-shape workflow-node--condition' : '' }
            ${ item.type === WF_ITEM_TYPE.GOTO ? 
              ' workflow-node--as-a-shape workflow-node--goto' : '' }
            ${ item.type === WF_ITEM_TYPE.FORM_TASK ? 
              ' workflow-node--as-a-shape workflow-node--form-task' : '' }
            ${ item.type === WF_ITEM_TYPE.VIEW_TASK ? 
              ' workflow-node--as-a-shape workflow-node--view-task' : '' }
            ${ spec && spec === 'shadow-view' ? 
              ' workflow-node--shadow-view-task' : '' }
            ${ item.type === WF_ITEM_TYPE.EXT_TASK ? 
              ' workflow-node--ext-task' : '' }
            ${ this.eventTypeIsTask(item.type) ? 
              ' workflow-node--task' : '' }"
            ${ level ? ` data-node-level="${ level }"` : '' }
            ${ item.id ? ` data-node-id="${ item.id }"` : '' }><!--
              -->${ 
                  item.root ? '<div class="workflow-node__start-text">START</div>' : ''
                }<div class="workflow-node__inner">${ false 
                  ? `<div class="workflow-node__shadow-shape-1"></div><!--
                  --><div class="workflow-node__shadow-shape-2"></div><!--
                  --><div class="workflow-node__round-1"></div><!--
                   --><div class="workflow-node__round-2"></div><!--
                -->` : '' }<!--
                --><div class="workflow-node__shape-outside"><!--
                --><div class="workflow-node__shape-inside"></div><!--
                --></div><!--
                -->${ this.eventTypeIsTask(item.type) ? 
                  `<div class="workflow-node__text workflow-node__text--task"
                    id="workflow-node__text--task-${ item.id }">
                      Task: <a href onclick="return false"
                        class="workflow-node__text-modal-link"
                      >${ hashId } ${ cutString(item.title, 
                        item.type !== WF_ITEM_TYPE.VIEW_TASK 
                        ? allowedLengthWide : allowedLength) || '......' }</a>
                  </div>${ item.title && item.title.length > allowedLength 
                    ? `<div class="mdl-tooltip mdl-tooltip--top" 
                    data-mdl-for="workflow-node__text--task-${ item.id }">
                    ${ autoBR(item.title) }</div>` : '' }` : ''
                }<!--
                -->${ item.type === WF_ITEM_TYPE.FORM_TASK ? 
                  `<div class="workflow-node__text workflow-node__text--form"
                    id="workflow-node__text--form-${ item.id }">
                      Form: <a href onclick="return false"
                        class="workflow-node__text-modal-link"
                      >${ cutString(item.form) || '......' }</a>
                  </div>${ item.form && item.form.length > allowedLength 
                    ? `<div class="mdl-tooltip mdl-tooltip--top" 
                    data-mdl-for="workflow-node__text--form-${ item.id }">
                    ${ autoBR(item.form) }</div>` : '' }` : ''
                }<!--
                -->${ item.type === WF_ITEM_TYPE.VIEW_TASK ? 
                  `<div class="workflow-node__text workflow-node__text--view"
                    id="workflow-node__text--view-${ item.id }">
                    View: <a href onclick="return false"
                        class="workflow-node__text-modal-link"
                      >${ cutString(item.view) || '......' }</a>
                  </div>${ item.view && item.view.length > allowedLength 
                    ? `<div class="mdl-tooltip mdl-tooltip--top" 
                    data-mdl-for="workflow-node__text--view-${ item.id }">
                    ${ autoBR(item.view) }</div>` : '' }` : ''
                }${ item.type === WF_ITEM_TYPE.PROCESS ? 
                  `<div id="workflow-node__text--branch-${ item.id }" 
                    class="workflow-node__text workflow-node__text--branch">
                      Branch: <a href onclick="return false">${ 
                        item.title || 'unnamed' 
                      }</a>
                  </div>` : ''
                }${ item.type === WF_ITEM_TYPE.FORM_TASK
                    || item.type === WF_ITEM_TYPE.VIEW_TASK
                    || item.type === WF_ITEM_TYPE.PROCESS ? 
                  `<div class="workflow-node__text workflow-node__text--process"
                    id="workflow-node__text--process-${ item.id }">
                      Next Action: <a href onclick="return false"
                        class="workflow-node__text-modal-link"
                      >${ cutString(item.process, allowedLengthWide) || '......' }</a>
                  </div>${ item.process && item.process.length > allowedLengthWide 
                    ? `<div class="mdl-tooltip mdl-tooltip--top" 
                    data-mdl-for="workflow-node__text--process-${ item.id }">
                    ${ autoBR(item.process) }</div>` : '' }` : ''
                }${ item.type === WF_ITEM_TYPE.CONDITION ? 
                  `<div class="workflow-node__text workflow-node__text--condition">
                      <i class="material-icons">add</i>
                  </div>${ item.condition && item.condition.length > allowedLength 
                    ? `<div class="mdl-tooltip mdl-tooltip--top" 
                    data-mdl-for="workflow-node__text--condition-${ item.id }">
                    ${ autoBR(item.condition) }</div>` : '' }` : ''
                }<!--
                -->${ item.type === WF_ITEM_TYPE.GOTO ? 
                  `<div class="workflow-node__text workflow-node__text--goto">
                      <a href onclick="return false"
                        id="workflow-node__text--goto-${ item.id }"
                        class="workflow-node__text-modal-link"
                      >Goto: ${ '#' + cutString(item.goto, allowedLengthWide) || '...' }</a>
                  </div>${ item.goto && item.goto.length > allowedLengthWide 
                    ? `<div class="mdl-tooltip mdl-tooltip--top" 
                    data-mdl-for="workflow-node__text--goto-${ item.id }">
                    ${ autoBR(item.goto) }</div>` : '' }` : ''
                }<!--
              --></div><!--
              ${ !item.root ? `--><div class="workflow-node__bubble-delete">
                <button class="mdl-button mdl-js-button mdl-button--icon">
                  <i class="material-icons">delete</i>
                </button>
              </div><!--` : '' }
          --></div><!--
          ${ !spec && this.nodeIsLast(item) 
              && item.type !== WF_ITEM_TYPE.GOTO && item.type !== WF_ITEM_TYPE.CONDITION 
            ? `--><ul class="plomino-workflow-editor__branches 
            plomino-workflow-editor__branches--virtual"><!--
          --><li class="plomino-workflow-editor__branch
            plomino-workflow-editor__branch--virtual"><!--
          --><div class="workflow-node workflow-node--virtual"><div><!--
            --><button id="wf-vrt-btn-${ item.id }" 
            class="mdl-button mdl-js-button mdl-js-ripple-effect
            mdl-button--fab mdl-button--mini-fab mdl-button--colored 
            mdl-color--grey-800"><i class="material-icons">add</i>
            </button></div></div><!--
            --><ul class="mdl-menu ${ level > 3 
              ? 'mdl-menu--top-left' : 'mdl-menu--bottom-left' } mdl-js-menu 
                mdl-js-ripple-effect"
                for="wf-vrt-btn-${ item.id }">
              ${ 
                // !this.eventTypeIsTask(item.type)
                true
                ? `<li class="mdl-menu__item" 
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.FORM_TASK }">
                Form task
              </li>
              <li class="mdl-menu__item"
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.VIEW_TASK }">
                View task
              </li>
              <li class="mdl-menu__item${ 
                parent ? ' mdl-menu__item--full-bleed-divider' : '' }"
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.EXT_TASK }">
                Ext. task
              </li>` : '' }
              ${ parent ? `<li class="mdl-menu__item"
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.CONDITION }">
                Branches
              </li>
              <li class="mdl-menu__item"
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.GOTO }">
                Goto
              </li>` : '' }
            </ul><!--
          --></li></ul>` : '-->' }<!--
      -->${ !spec ? `</li>` : '' }`);
    }

    return $buildJQItem();
  }
};

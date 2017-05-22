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
    const workWithItemRecursive = (item: PlominoWorkflowItem): JQuery => {
      const $item: JQuery = this.parseWFItem(item, level++);
      
      if (item.children.length) {
        const $childrenTree = $(`<ul class="plomino-workflow-editor__branches"></ul>`);
        for (let child of item.children) {
          $childrenTree.append(workWithItemRecursive(child));
          level--;
        }
        $item.append($childrenTree);
      }

      if (!item.root) {
        $item.find('.workflow-node__text--macro a')
          .click(($event) => configuration.onMacroClick($event, $item, item));
        $item.click(($event) => configuration.onItemClick($event, $item, item));
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
   */
  parseWFItem(item: PlominoWorkflowItem, level = 0): JQuery {

    const allowedLength = 16;

    const cutString = ((str: string) => {
      if (str.length > allowedLength) {
        str = str.substr(0, allowedLength) + '...';
      }

      return str;
    });

    return $(
      `<li class="plomino-workflow-editor__branch" 
           ${ !item.root ? ' draggable="true"' : ''}><!--
           --><div class="workflow-node
            ${ item.root ? ' workflow-node--root' : ''}
            ${ item.dropping ? ' workflow-node--dropping' : '' }
            ${ item.type === WF_ITEM_TYPE.CONDITION ? 
              ' workflow-node--as-a-shape workflow-node--condition' : '' }
            ${ item.type === WF_ITEM_TYPE.GOTO ? 
              ' workflow-node--as-a-shape workflow-node--goto' : '' }
            ${ this.eventTypeIsTask(item.type) ? 
              ' workflow-node--as-a-shape workflow-node--task' : '' }"
            ${ level ? ` data-node-level="${ level }"` : '' }
            ${ item.id ? ` data-node-id="${ item.id }"` : '' }><!--
              -->${ item.type === WF_ITEM_TYPE.CONDITION 
              ? `<div class="workflow-node__hover-plus-btn"><!--
              --><button class="mdl-button mdl-js-button mdl-js-ripple-effect
              mdl-button--fab mdl-button--mini-fab mdl-button--colored 
              mdl-color--blue-900"><i class="material-icons">add</i>
              </button></div>` : '' }<div class="workflow-node__inner"><!--
                --><div class="workflow-node__shape-outside"><!--
                --><div class="workflow-node__shape-inside"></div><!--
                --></div><!--
                -->${ this.eventTypeIsTask(item.type) ? 
                  `<div class="workflow-node__text workflow-node__text--task"
                    id="workflow-node__text--task-${ item.id }">
                      <a href onclick="return false"
                        class="workflow-node__text-modal-link"
                      >${ cutString(item.title) || '&nbsp;' }</a>
                  </div>${ item.title.length > allowedLength 
                    ? `<div class="mdl-tooltip mdl-tooltip--top" 
                    data-mdl-for="workflow-node__text--task-${ item.id }">
                    ${ item.title.match(/(.\s?){1,22}/g).join('<br>')
                   }</div>` : '' }` : ''
                }<!--
                -->${ item.form ? 
                  `<div class="workflow-node__text workflow-node__text--form"
                    id="workflow-node__text--form-${ item.id }">
                      Form: ${ cutString(item.form) }
                  </div>${ item.form.length > allowedLength 
                    ? `<div class="mdl-tooltip mdl-tooltip--top" 
                    data-mdl-for="workflow-node__text--form-${ item.id }">
                    ${ item.form.match(/(.\s?){1,22}/g).join('<br>')
                   }</div>` : '' }` : ''
                }<!--
                -->${ item.view ? 
                  `<div class="workflow-node__text workflow-node__text--view"
                    id="workflow-node__text--view-${ item.id }">
                      View: ${ cutString(item.view) }
                  </div>${ item.view.length > allowedLength 
                    ? `<div class="mdl-tooltip mdl-tooltip--top" 
                    data-mdl-for="workflow-node__text--view-${ item.id }">
                    ${ item.view.match(/(.\s?){1,22}/g).join('<br>')
                   }</div>` : '' }` : ''
                }<!--
                -->${ item.type === WF_ITEM_TYPE.PROCESS ? 
                  `<div class="workflow-node__text workflow-node__text--process"
                    id="workflow-node__text--process-${ item.id }">
                      <a href onclick="return false"
                        class="workflow-node__text-modal-link"
                      >${ cutString(item.title) }</a>
                  </div>${ item.title.length > allowedLength 
                    ? `<div class="mdl-tooltip mdl-tooltip--top" 
                    data-mdl-for="workflow-node__text--process-${ item.id }">
                    ${ item.title.match(/(.\s?){1,22}/g).join('<br>')
                   }</div>` : '' }` : ''
                }<!--
                -->${ item.type === WF_ITEM_TYPE.PROCESS ? 
                  `<div class="workflow-node__text workflow-node__text--macro">
                      Macro: <a href onclick="return false">add rules</a>
                  </div>` : ''
                }<!--
                -->${ item.type === WF_ITEM_TYPE.CONDITION ? 
                  `<div class="workflow-node__text workflow-node__text--condition">
                      <a href onclick="return false"
                        id="workflow-node__text--condition-${ item.id }"
                        class="workflow-node__text-modal-link"
                      >${ cutString(item.condition) || '&nbsp;' }</a>
                  </div>${ item.condition.length > allowedLength 
                    ? `<div class="mdl-tooltip mdl-tooltip--top" 
                    data-mdl-for="workflow-node__text--condition-${ item.id }">
                    ${ item.condition.match(/(.\s?){1,22}/g).join('<br>')
                   }</div>` : '' }` : ''
                }<!--
                -->${ item.goto ? 
                  `<div class="workflow-node__text workflow-node__text--goto">
                      <a href onclick="return false"
                        id="workflow-node__text--goto-${ item.id }"
                        class="workflow-node__text-modal-link"
                      >Goto: ${ cutString(item.goto) }</a>
                  </div>${ item.goto.length > allowedLength 
                    ? `<div class="mdl-tooltip mdl-tooltip--top" 
                    data-mdl-for="workflow-node__text--goto-${ item.id }">
                    ${ item.goto.match(/(.\s?){1,22}/g).join('<br>')
                   }</div>` : '' }` : ''
                }<!--
              --></div><!--
          --></div><!--
          ${ this.nodeIsLast(item) ? `--><ul class="plomino-workflow-editor__branches 
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
              <li class="mdl-menu__item" 
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.FORM_TASK }">
                Form task
              </li>
              <li class="mdl-menu__item"
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.VIEW_TASK }">
                View task
              </li>
              <li class="mdl-menu__item mdl-menu__item--full-bleed-divider"
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.EXT_TASK }">
                Ext. task
              </li>
              <li class="mdl-menu__item"
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.PROCESS }">
                Process
              </li>
              <li class="mdl-menu__item"
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.CONDITION }">
                Condition
              </li>
              <li class="mdl-menu__item"
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.GOTO }">
                Goto
              </li>
            </ul><!--
          --></li></ul>` : '-->' }<!--
      --></li>`);
  }
};

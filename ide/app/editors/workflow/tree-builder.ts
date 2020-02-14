export const WF_ITEM_TYPE = {
  FORM_TASK: 'workflowFormTask',
  VIEW_TASK: 'workflowViewTask',
  EXT_TASK: 'workflowExternalTask',
  PROCESS: 'workflowProcess',
  CONDITION: 'workflowCondition',
  GOTO: 'workflowGoto',
};

if (!(<any> String.prototype).splice) {
  /**
   * {JSDoc}
   *
   * The splice() method changes the content of a string by removing a range of
   * characters and/or adding new characters.
   *
   * @this {String}
   * @param {number} start Index at which to start changing the string.
   * @param {number} delCount An integer indicating the number of old chars to remove.
   * @param {string} newSubStr The String that is spliced in.
   * @return {string} A new string with the spliced substring.
   */
  (<any> String.prototype).splice = 
    function (start: number, delCount: number, newSubStr: string) {
      return this.slice(0, start) + newSubStr + this.slice(start + Math.abs(delCount));
    };
}

export const treeBuilder = {
  getBuildedTree(workingTree: PlominoWorkflowItem): string {
    let level = 1;
    const iWalk = (item: PlominoWorkflowItem, parent: PlominoWorkflowItem = null): string => {
      let buildedItem: any = this.parse(item, parent, level++);
      
      if (item.children.length) {
        let childrenTree: any = `<ul class="plomino-workflow-editor__branches${
          item.type === WF_ITEM_TYPE.CONDITION 
            ? ' plomino-workflow-editor__branches--condition' : ''
        }"></ul>`;
        
        if (item.type !== WF_ITEM_TYPE.CONDITION) {
          const bbtn = `<div class="plomino-workflow-editor__branch-add-below-bubble-btn" dnd-droppable>
            <button class="mdl-button mdl-js-button mdl-color--grey-700
              mdl-button--fab mdl-button--mini-fab mdl-button--colored"
              id="wf-vrt2-btn-${ item.id }">
              <i class="material-icons" (onDragLeave)="onDragLeave($event)"
        dnd-droppable (onDragEnter)="onDragEnter($event)">add</i>
            </button>
            </div><ul class="mdl-menu mdl-menu--bottom-right mdl-js-menu 
                mdl-js-ripple-effect"
                for="wf-vrt2-btn-${ item.id }">
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
              <li class="mdl-menu__item${ 
                parent && parent.type !== WF_ITEM_TYPE.CONDITION
                && !(item.children.length 
                  && item.children[0].type === WF_ITEM_TYPE.CONDITION)
                ? ' mdl-menu__item--full-bleed-divider' : '' }"
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.EXT_TASK }">
                Ext. task
              </li>
              ${ parent && parent.type !== WF_ITEM_TYPE.CONDITION 
                && !(item.children.length 
                  && item.children[0].type === WF_ITEM_TYPE.CONDITION)
                ? `<li class="mdl-menu__item"
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.CONDITION }">
                Branch
              </li>${ item.children.length ? '' : `
              <li class="mdl-menu__item"
                data-target="${ item.id }"
                data-create="${ WF_ITEM_TYPE.GOTO }">
                Goto
              </li>`}` : '' }
            </ul>`;
          childrenTree = childrenTree.splice(-5, 0, bbtn);
        }
        
        for (const child of item.children) {
          if (!child) { 
            console.error('child missed');
           }
          childrenTree = childrenTree.splice(-5, 0, iWalk(child, item));
          level--;
        }
        buildedItem = buildedItem.splice(-5, 0, childrenTree);
      }

      return buildedItem;
    };

    return `<ul class="plomino-workflow-editor__branches
      plomino-workflow-editor__branches--root">${ iWalk(workingTree) }</ul>`;
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
  parse(item: PlominoWorkflowItem, parent: PlominoWorkflowItem = null, level = 0) {
    const allowedLength = 36;
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

    if (!item) { return ''; }
    const hashId = item.id !== -1 ? '#' + item.id : '';
        return `<li class="plomino-workflow-editor__branch" 
        ><div ${ !item.root && item.type !== WF_ITEM_TYPE.CONDITION 
            ? ' draggable="true"' : ''} class="workflow-node ${ 
              item.root ? ' workflow-node--root' : ''}${ 
          item.dropping ? ' workflow-node--dropping' : '' }${ 
          item.type === WF_ITEM_TYPE.PROCESS ? ' workflow-node--branch' : '' }${ 
          item.type === WF_ITEM_TYPE.CONDITION ? 
          ' workflow-node--as-a-shape workflow-node--condition' : '' }${ 
            item.type === WF_ITEM_TYPE.GOTO ? 
          ' workflow-node--as-a-shape workflow-node--goto' : '' }${ 
            item.type === WF_ITEM_TYPE.FORM_TASK ? 
          ' workflow-node--as-a-shape workflow-node--form-task' : '' }${ 
            item.type === WF_ITEM_TYPE.VIEW_TASK ? 
          ' workflow-node--as-a-shape workflow-node--view-task' : '' }${ 
            item.type === WF_ITEM_TYPE.EXT_TASK ? 
          ' workflow-node--ext-task' : '' }${ 
            this.eventTypeIsTask(item.type) ? 
          ' workflow-node--task' : '' }"
        ${ level ? ` data-node-level="${ level }"` : '' }
        ${ item.id ? ` data-node-id="${ item.id }"` : '' }>${ 
              item.root ? '<div class="workflow-node__start-text">START</div>' : ''
            }<div class="workflow-node__inner"${ 
              item.type === WF_ITEM_TYPE.CONDITION 
            ? ` id="wf-condition-item-i${ item.id }"` : '' }>${ false 
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
                  <span>Task:</span> <a href onclick="return false"
                    class="workflow-node__text-modal-link"
                  >${ hashId } ${ cutString(item.title, allowedLength) || '......' }</a>
              </div>${ item.notes 
                ? `<div class="mdl-tooltip mdl-tooltip--top" 
                data-mdl-for="workflow-node__text--task-${ item.id }">
                ${ autoBR(item.notes) }</div>` : '' }` : ''
            }<!--
            -->${ item.type === WF_ITEM_TYPE.FORM_TASK ? 
              `<div class="workflow-node__text workflow-node__text--form"
                id="workflow-node__text--form-${ item.id }">
                  <span>Form:</span> <a href onclick="return false"
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
                <span>View:</span> <a href onclick="return false"
                    class="workflow-node__text-modal-link"
                  >${ cutString(item.view) || '......' }</a>
              </div>${ item.view && item.view.length > allowedLength 
                ? `<div class="mdl-tooltip mdl-tooltip--top" 
                data-mdl-for="workflow-node__text--view-${ item.id }">
                ${ autoBR(item.view) }</div>` : '' }` : ''
            }${ item.type === WF_ITEM_TYPE.PROCESS ? 
              `<div id="workflow-node__text--branch-${ item.id }" 
                class="workflow-node__text workflow-node__text--branch">
                  <span>Branch:</span> <a href onclick="return false"
                    class="workflow-node__text-modal-link">${ 
                    item.title || 'unnamed' 
                  }</a>
              </div>` : ''
            }${ item.type === WF_ITEM_TYPE.FORM_TASK
                || item.type === WF_ITEM_TYPE.VIEW_TASK
                || item.type === WF_ITEM_TYPE.PROCESS ? 
              `<div class="workflow-node__text workflow-node__text--process"
                id="workflow-node__text--process-${ item.id }">
                  <span>Next Action:</span> <a href onclick="return false"
                    class="workflow-node__text-modal-link"
                  >${ cutString(item.process, allowedLengthWide) || '......' }</a>
              </div>${ item.macroDesc 
                ? `<div class="mdl-tooltip mdl-tooltip--top" 
                data-mdl-for="workflow-node__text--process-${ item.id }">
                ${ autoBR(item.macroDesc) }</div>` : '' }` : ''
            }${ item.type === WF_ITEM_TYPE.CONDITION ? 
              `<div class="workflow-node__text workflow-node__text--condition">
                  <!--i class="material-icons">add</i-->
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
                  >Goto: ${ cutString(item.goto 
                    ? '#' + item.goto + ' ' + item.gotoLabel 
                    : '......', allowedLength) || '......' }</a>
              </div>${ item.goto 
                && ('#' + item.goto + ' ' + item.gotoLabel).length > allowedLength 
                ? `<div class="mdl-tooltip mdl-tooltip--top" 
                data-mdl-for="workflow-node__text--goto-${ item.id }">
                ${ autoBR('#' + item.goto + ' ' + item.gotoLabel) }</div>` : '' }` : ''
            }<!--
          --></div><!--
          ${ !item.root ? `--><div
            class="workflow-node__bubble-delete">
            <button class="mdl-button mdl-js-button mdl-button--icon">
              <i class="material-icons">delete</i>
            </button>
          </div><!--` : '' }
      --></div>${ item.type === WF_ITEM_TYPE.CONDITION 
          ? `<div class="mdl-tooltip mdl-tooltip--large" 
          for="wf-condition-item-i${ item.id }">
          click to create <br>new branch</div>` : ''}<!--
      ${ this.nodeIsLast(item) 
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
            parent && parent.type !== WF_ITEM_TYPE.CONDITION
            ? ' mdl-menu__item--full-bleed-divider' : '' }"
            data-target="${ item.id }"
            data-create="${ WF_ITEM_TYPE.EXT_TASK }">
            Ext. task
          </li>` : '' }
          ${ parent && parent.type !== WF_ITEM_TYPE.CONDITION
            && !(item.children.length 
            && item.children[0].type === WF_ITEM_TYPE.CONDITION)
            ? `<li class="mdl-menu__item"
            data-target="${ item.id }"
            data-create="${ WF_ITEM_TYPE.CONDITION }">
            Branch
          </li>` : '' }${ parent && !item.children.length ? `
          <li class="mdl-menu__item"
            data-target="${ item.id }"
            data-create="${ WF_ITEM_TYPE.GOTO }">
            Goto
          </li>` : '' }
        </ul><!--
      --></li></ul>` : '-->' }</li>`;
  },

  checkTarget(eventTarget: Element, className: string) {
    return eventTarget.parentElement.parentElement.parentElement
        .classList.contains(className)
      || eventTarget.classList.contains(className)
      || eventTarget.parentElement.classList.contains(className)
      || eventTarget.parentElement.parentElement.classList.contains(className);
  }
};

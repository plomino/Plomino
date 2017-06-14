import { PlominoWorkflowChangesNotifyService } from './workflow.changes.notify.service';
import { TreeStructure } from './tree-structure';
import { Injectable, NgZone } from '@angular/core';
import { WF_ITEM_TYPE as WF } from './tree-builder';
import { PlominoFormsListService, LogService, ObjService, PlominoDBService,
  FormsService, DraggingService, PlominoSaveManagerService, PlominoHTTPAPIService
} from '../../services';

@Injectable()
export class PlominoWorkflowItemEditorService {

  private selectedItemRef: PlominoWorkflowItem;
  private itemSettingsDialog: HTMLDialogElement;
  private $itemSettingsDialog: JQuery;
  private registeredTree: TreeStructure;
  private latestUsingForm: any;

  constructor(
    private saveManager: PlominoSaveManagerService,
    private formsService: FormsService,
    private formsList: PlominoFormsListService,
    private workflowChanges: PlominoWorkflowChangesNotifyService,
    private api: PlominoHTTPAPIService,
    private dbService: PlominoDBService,
    private objService: ObjService,
    private zone: NgZone,
  ) {}

  init() {
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
          this.applyDialog();
          this.$itemSettingsDialog.modal('hide');
        }
      });
    });

    Array.from(
      this.itemSettingsDialog
        .querySelectorAll('button')
    )
    .forEach((btn: HTMLElement) => {
      btn.addEventListener('click', (evt) => {
        if (btn.classList.contains('wf-item-settings-dialog__apply-btn')) {
          this.applyDialog();
        }
        else if (btn.classList.contains('wf-item-settings-dialog__edit-btn')) {
          this.applyDialog();
          this.openResourceTab(this.selectedItemRef);
        }
        else if (btn.classList.contains('wf-item-settings-dialog__macro-btn')) {
          this.editMacro(this.selectedItemRef);
        }
        else if (btn.classList.contains('wf-item-settings-dialog__create-btn--form')) {
          this.saveManager.createNewForm((url, label) => {
            this.selectedItemRef.title = label;
            this.selectedItemRef.form = url.split('/').pop();
            this.workflowChanges.needSave.next(true);
          });
        }
        else if (btn.classList.contains('wf-item-settings-dialog__create-btn--view')) {
          this.saveManager.createNewView((url, label) => {
            this.selectedItemRef.title = label;
            this.selectedItemRef.view = url.split('/').pop();
            this.workflowChanges.needSave.next(true);
          });
        }
        this.$itemSettingsDialog.modal('hide');
      });
    });
  }

  registerTree(tree: TreeStructure) {
    this.registeredTree = tree;
  }

  getTopItemWithForm(itemId: number, tree: TreeStructure): false|PlominoWorkflowItem {
    const result = tree.searchParentItemOfItemByCondition(
      tree.getItemById(itemId), 
      (item: PlominoWorkflowItem): Boolean => 
        Boolean(item.form) || Boolean(item.view)
      );
    return result;
  }

  editMacro(item: PlominoWorkflowItem) {
    const tmpOnTopFormItem = (item.form || item.view) 
      ? item : (this.getTopItemWithForm(item.id, this.registeredTree) || null);

    if (tmpOnTopFormItem) {
      this.openResourceTab(tmpOnTopFormItem);
      setTimeout(() => {
        this.formsService.changePaletteTab(2);
      }, 100);
    }
  }

  openResourceTab(item: PlominoWorkflowItem) {
    const key = item.type === WF.VIEW_TASK ? 'view' : 'form';
    const $resource = 
      $(`.tree-node--name:contains("${ item[key] }")`)
        .filter((i, node: HTMLElement) => 
          $(node).text().trim() === item[key]);
  
    $resource.click();
  }

  setSelectedItem(item: PlominoWorkflowItem) {
    this.selectedItemRef = item;
  }

  getSelectedItem(): PlominoWorkflowItem {
    return this.selectedItemRef;
  }

  selectedItemIsNothing(): Boolean {
    return !this.selectedItemRef || typeof this.selectedItemRef === 'undefined';
  }

  showModal(item: PlominoWorkflowItem, processModal = false) {
    if (this.selectedItemIsNothing()) {
      this.setSelectedItem(item);
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

    if (item.type === WF.GOTO) {
      const nodesList = this.registeredTree.getNodesList();
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

        if ((input.dataset.key === 'form' && item.type === WF.FORM_TASK) 
          || (input.dataset.key === 'view' && item.type === WF.VIEW_TASK)
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
            if (item.type === WF.PROCESS 
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
    const tmpOnTopFormItem = (item.form || item.view) 
      ? item : (this.getTopItemWithForm(item.id, this.registeredTree) || null);
    if (!tmpOnTopFormItem || !(tmpOnTopFormItem.form || tmpOnTopFormItem.view)) {
      if (item.type === WF.FORM_TASK || item.type === WF.VIEW_TASK 
        || item.type === WF.PROCESS
      ) {
        $wd.html(`<label style="margin-bottom: 15px; margin-top: 10px">
          Implementation<br>
          <small style="color: dimgray;">There is no form or view related - 
          you can\'t select the macros</small></label>`);
      }
      else {
        $wd.html('');
      }
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

    const formURL = `${ this.dbService.getDBLink() }/${ 
      tmpOnTopFormItem.form || tmpOnTopFormItem.view }`;
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
            new MacroWidget($widget);
          });

          try {
            delete (<any>jQuery)._data(document, 'events').focusin;
          } catch(e) {}
        }
  
        /* step 7: put radios */
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
              
              $(e).prepend($r);
              $(e).find('.select2-container').css('width', '94%');
            });
          });

        $(window['macrosSelectorRefreshEvent']).trigger('macros_selector_refresh');
      });
    });
  }

  applyDialog() {
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

        const eventTypeIsTask = [
          WF.FORM_TASK, WF.VIEW_TASK, WF.EXT_TASK
        ].indexOf(item.type) !== -1;

        if (item.hasOwnProperty(input.dataset.key)
          || (eventTypeIsTask && input.dataset.key === 'title')
          || (eventTypeIsTask && input.dataset.key === 'notes')
          || (eventTypeIsTask && input.dataset.key === 'process')
          || (item.type === WF.PROCESS && input.dataset.key === 'process')
        ) {
          item[input.dataset.key] = $(input).val();

          if (input.dataset.key === 'goto') {
            const _data = item.goto.split(':::');
            item.goto = _data[0];
            item.gotoLabel = _data[1];
          }
        }
      });
    
    this.workflowChanges.needSave.next(true);

    /* if it is a process - take fields rules and save */
    if (item.macroText !== null 
      && typeof item.macroText !== 'undefined' 
      && this.latestUsingForm.action
    ) {
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
}
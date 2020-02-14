import { PlominoWorkflowChangesNotifyService } from './workflow.changes.notify.service';
import { TreeStructure } from './tree-structure';
import { Injectable, NgZone } from '@angular/core';
import { WF_ITEM_TYPE as WF } from './tree-builder';
import { PlominoFormsListService, ObjService, PlominoDBService,
  FormsService, PlominoSaveManagerService, PlominoHTTPAPIService
} from '../../services';
import { PlominoWorkflowTreeService } from './workflow-tree.service';

@Injectable()
export class PlominoWorkflowItemEditorService {

  private selectedItemRef: PlominoWorkflowItem;
  private itemSettingsDialog: HTMLDialogElement;
  private $itemSettingsDialog: JQuery;
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
    private treeService: PlominoWorkflowTreeService,
  ) {
    this.setSelectedItem(null);
  }

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
      $(btn).unbind('click.wf').bind('click.wf', (evt) => {
        
        if (this.treeService.getActiveTree() && this.selectedItemIsNothing()) {
          // get selected item using id information 
          const item = this.treeService.getActiveTree()
            .getItemById(
              +(<HTMLElement> this.itemSettingsDialog).dataset.itemId
            );

          if (item) {
            this.selectedItemRef = item;
          }
        }

        const updateDBSettings = (formOrView: string) => 
          (url: string, label: string) => {
            if (this.selectedItemRef && this.treeService.getActiveTree()) {
              if (!this.selectedItemRef.title) {
                this.selectedItemRef.title = label;
              }
              this.selectedItemRef[formOrView] = url.split('/').pop();
              this.workflowChanges.needSave.next(true);
            }
          };

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
          this.applyDialog();
          this.saveManager.createNewForm(updateDBSettings('form').bind(this), true);
        }
        else if (btn.classList.contains('wf-item-settings-dialog__create-btn--view')) {
          this.applyDialog();
          this.saveManager.createNewView(updateDBSettings('view').bind(this), true);
        }
        
        this.$itemSettingsDialog.modal('hide');
      });
    });
  }

  getTopItemWithForm(itemId: number, tree: TreeStructure): false|PlominoWorkflowItem {
    const result = tree.searchParentItemOfItemByCondition(
      tree.getItemById(itemId), 
      (item: PlominoWorkflowItem): boolean => 
        Boolean(item.form) || Boolean(item.view)
      );
    return result;
  }

  editMacro(item: PlominoWorkflowItem) {
    const tmpOnTopFormItem = (item.form || item.view) 
      ? item : (this.getTopItemWithForm(item.id, 
        this.treeService.getActiveTree()) || null);

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

  selectedItemIsNothing(): boolean {
    return !this.selectedItemRef || typeof this.selectedItemRef === 'undefined';
  }

  showModal(item: PlominoWorkflowItem, processModal = false) {
    if (this.selectedItemIsNothing()) {
      this.setSelectedItem(item);
    }
    (<HTMLElement> this.itemSettingsDialog).dataset.itemId = item.id.toString();
    this.itemSettingsDialog
      .querySelector('#wf-item-settings-dialog__form')
      .innerHTML = '<option value=""></option>' + this.formsList.getForms()
        .map((f: any) => `<option>${ f.url.split('/').pop() }</option>`)
        .join('');

    this.itemSettingsDialog
      .querySelector('#wf-item-settings-dialog__view')
      .innerHTML = '<option value=""></option>' + this.formsList.getViews()
        .map((f: any) => `<option>${ f.url.split('/').pop() }</option>`)
        .join('');

    if (item.type === WF.GOTO) {
      const nodesList = this.treeService.getActiveTree().getNodesList();
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
            .css('visibility', item[input.dataset.key] ? 'hidden' : 'visible');
          $('.wf-item-settings-dialog__edit-btn')
            .css('visibility', !item[input.dataset.key] ? 'hidden' : 'visible');
          
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

      if (item.type === WF.FORM_TASK 
        || item.type === WF.VIEW_TASK || item.type === WF.PROCESS) {
        this.itemSettingsDialog
          .querySelectorAll(
            'label[for="wf-item-settings-dialog__process"] [data-typefor]')
          .forEach((inputGroup: HTMLElement) => {
            if (!(new RegExp(item.type === WF.PROCESS 
              ? 'inlineProcess' 
              : item.type, 'g'))
              .test(inputGroup.dataset.typefor)) {
              inputGroup.style.display = 'none';
            }
            else {
              inputGroup.style.display = 'inline-block';
            }
          });
      }
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
      ? item : (this.getTopItemWithForm(item.id, 
        this.treeService.getActiveTree()) || null);
    if (
      (item.type === WF.FORM_TASK || item.type === WF.VIEW_TASK) 
      && !(item.form || item.view)
    ) {
      $wd.html(`<label style="margin-bottom: 15px; margin-top: 10px">
        Implementation<br>
        <small style="color: dimgray;">Please select a form/view in the 
        task so a rule can be selected.</small></label>`);
      return;
    }
    if (!tmpOnTopFormItem || !(tmpOnTopFormItem.form || tmpOnTopFormItem.view)) {
      if (item.type === WF.FORM_TASK || item.type === WF.VIEW_TASK 
        || item.type === WF.PROCESS
      ) {
        
        $wd.html(`<label style="margin-bottom: 15px; margin-top: 10px">
          Implementation<br>
          <small style="color: dimgray;">Please select a 
                  <a href onclick="return false"
                    class="workflow-node__text-modal-link"
                  >form/view</a>
          in the 
          previous task so a rule can be selected.</small></label>`);
        /*
        $wd.html(`<label style="margin-bottom: 15px; margin-top: 10px">
          Implementation<br>
          <small style="color: dimgray;">Please select a 
                  <a href onclick="return false"
                    class="workflow-node__text-modal-link"
                  >form/view</a>
          in the 
          previous task so a rule can be selected.</small></label>`);
        const alink = $wd.find('#workflow-node__text-modal-link');
        alink.onclick = function() {
          console.log(item);
          };*/
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
        const $htmlFSForm = $htmlFS.find('form[data-pat-autotoc]');
        this.latestUsingForm = {
          id: $htmlFSForm.attr('action').split('/').slice(-2, -1),
          action: $htmlFSForm.attr('action'),
          $form: $htmlFSForm
        };
        htmlBuffer = $htmlFS.find('ul.plomino-macros').get(0).outerHTML;
        htmlBuffer = `<label style="margin-bottom: 15px; margin-top: 10px">
          Implementation<br>
          <small style="color: dimgray;">add or select a rule from 
          <b>${ tmpOnTopFormItem.form || tmpOnTopFormItem.view }</b> ${
            tmpOnTopFormItem.type === WF.FORM_TASK ? 'form' : 'view'
          } 
          <br>which implements the condition and action above</small>
          </label>${ htmlBuffer }`;
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
            const $radiosBefore = $wd.find('input[type="radio"]');
            const radiosBeforeLength = $radiosBefore.length;
            $radiosBefore.remove();

            $wd.find('.plomino-macros-rule').each((i, e) => {
              if (!item.macroText) {
                item.macroText = '';
                item.macroDesc = '';
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
            
            const $radiosNow = $wd.find('input[type="radio"]');
            const radiosNowLength = $radiosNow.length;
            const newMacroRuleAdded = radiosBeforeLength < radiosNowLength;

            if (newMacroRuleAdded && $radiosNow.length > 1) {
              /** mark the new macro rule as selected */
              $radiosNow[$radiosNow.length - 2].click();
            }
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
      item.macroDesc = $e.find('.plomino_edit_macro')
        .toArray().map((_e: HTMLElement) => _e.innerText).join(', ');
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
          if (['form.buttons.save', 'form.buttons.cancel']
              .indexOf(element.name) === -1
            && element.name.indexOf(':list') === -1
          ) {
            const value = element.type === 'checkbox' 
              ? $(element).is(':checked') : $(element).val();
            if (value !== 'true' && value !== 'false') {
              fd.append(element.name, value);
            }
          }
        });

      fd.append('form.widgets.form_method:list', 'Auto');

      this.itemSettingsDialog
        .querySelectorAll('input[name="form.widgets.IHelpers.helpers:list"]')
        .forEach((input: HTMLInputElement) => {
          fd.append('form.widgets.IHelpers.helpers:list', $(input).val());
        });

      fd.append('form.buttons.save', 'Save');
      
      /** flush cache of this form */
      this.objService.flushFormSettingsCache(this.latestUsingForm.id);

      this.api.postWithOptions(this.latestUsingForm.action, fd, {})
        .subscribe((data: Response) => {});
    }
  }
}
